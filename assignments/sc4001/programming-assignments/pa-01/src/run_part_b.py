import argparse
import csv
import json
import os
import platform
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F
from torch.utils.data import Subset

from .part_b_data import PartBData, load_part_b_data
from .part_b_models import (
    build_part_b_model,
    count_conv_linear_flops,
    count_trainable_parameters,
)
from .part_b_training import (
    PartBTrainingConfig,
    evaluate_classifier,
    resolve_device,
    set_part_b_seed,
    train_classifier,
)


DATA_PATH = Path("chestxray_binary_64.npz")
OUTPUT_ROOT = Path("outputs/part_b")
LEARNING_RATES = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
BATCH_SIZES = [16, 32, 64, 128, 256]
SELECTION_SEED = 42
GRADCAM_SEED = 2026


def write_json(path: str | Path, value) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def read_json(path: str | Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_csv(path: str | Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows available for {path}")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def save_checkpoint(path: str | Path, model: torch.nn.Module) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = {name: tensor.detach().cpu() for name, tensor in model.state_dict().items()}
    torch.save(state, path)


def load_checkpoint(path: str | Path, model_name: str, device: torch.device):
    model = build_part_b_model(model_name)
    state = torch.load(path, map_location="cpu", weights_only=True)
    # Checkpoints produced before gradcam_layer became a property contain a
    # duplicate alias of the final convolution. The canonical feature/block
    # key is also present, so dropping the alias preserves every parameter.
    state = {
        name: tensor for name, tensor in state.items() if not name.startswith("last_conv.")
    }
    model.load_state_dict(state)
    return model.to(device)


def _candidate_name(value) -> str:
    return str(value).replace("-", "m").replace(".", "p")


def _selection_key(row: dict) -> tuple[float, float]:
    return (
        float(row["validation_classification_error"]),
        float(row["validation_loss"]),
    )


def _train_candidate(
    model_name: str,
    data: PartBData,
    config: PartBTrainingConfig,
    device: torch.device,
):
    # Seed before construction so every hyperparameter candidate for the same
    # architecture starts from identical weights. train_classifier seeds again
    # before constructing its DataLoader and taking optimisation steps.
    set_part_b_seed(config.seed)
    return train_classifier(
        build_part_b_model(model_name),
        data.train,
        data.validation,
        config,
        device,
    )


def _result_row(name: str, value, result: dict) -> dict:
    return {
        name: value,
        "best_epoch": result["best_epoch"],
        **{f"validation_{key}": metric for key, metric in result["validation"].items()},
    }


def run_b1(
    data: PartBData,
    output_root: Path,
    device: torch.device,
    *,
    quick: bool,
    num_workers: int,
) -> dict:
    stage_dir = output_root / "b1"
    learning_rates = LEARNING_RATES[:2] if quick else LEARNING_RATES
    max_epochs = 2 if quick else 20
    rows = []
    histories = []
    checkpoint_by_rate = {}

    for learning_rate in learning_rates:
        config = PartBTrainingConfig(
            learning_rate=learning_rate,
            batch_size=128,
            seed=SELECTION_SEED,
            max_epochs=max_epochs,
            num_workers=num_workers,
        )
        result = _train_candidate("alexnet", data, config, device)
        rows.append(_result_row("learning_rate", learning_rate, result))
        histories.append((f"lr={learning_rate:g}", result["history"]))
        checkpoint = stage_dir / "candidates" / f"lr_{_candidate_name(learning_rate)}.pt"
        save_checkpoint(checkpoint, result["model"])
        checkpoint_by_rate[learning_rate] = checkpoint

    selected = min(rows, key=_selection_key)
    selected_rate = float(selected["learning_rate"])
    selected_checkpoint = checkpoint_by_rate[selected_rate]
    selected_model = load_checkpoint(selected_checkpoint, "alexnet", device)
    selected_config = PartBTrainingConfig(
        learning_rate=selected_rate,
        batch_size=128,
        seed=SELECTION_SEED,
        max_epochs=max_epochs,
        num_workers=num_workers,
    )
    test_metrics = evaluate_classifier(selected_model, data.test, selected_config, device)
    final_checkpoint = stage_dir / "selected_model.pt"
    save_checkpoint(final_checkpoint, selected_model)

    write_csv(stage_dir / "search_results.csv", rows)
    write_json(stage_dir / "histories.json", {label: history for label, history in histories})
    summary = {
        "model": "alexnet",
        "selected_learning_rate": selected_rate,
        "batch_size": 128,
        "selection_seed": SELECTION_SEED,
        "selection_criterion": "lowest validation classification error; validation loss tie-break",
        "best_epoch": int(selected["best_epoch"]),
        "validation": {
            key.removeprefix("validation_"): value
            for key, value in selected.items()
            if key.startswith("validation_")
        },
        "test": test_metrics,
        "checkpoint": str(final_checkpoint),
    }
    write_json(stage_dir / "summary.json", summary)
    return summary


def run_b2(
    data: PartBData,
    output_root: Path,
    device: torch.device,
    *,
    quick: bool,
    num_workers: int,
) -> dict:
    b1 = read_json(output_root / "b1" / "summary.json")
    stage_dir = output_root / "b2"
    batch_sizes = BATCH_SIZES[:2] if quick else BATCH_SIZES
    max_epochs = 2 if quick else 20
    rows = []
    histories = []
    checkpoint_by_batch = {}

    for batch_size in batch_sizes:
        config = PartBTrainingConfig(
            learning_rate=float(b1["selected_learning_rate"]),
            batch_size=batch_size,
            seed=SELECTION_SEED,
            max_epochs=max_epochs,
            num_workers=num_workers,
        )
        result = _train_candidate("vgg", data, config, device)
        rows.append(_result_row("batch_size", batch_size, result))
        histories.append((f"batch={batch_size}", result["history"]))
        checkpoint = stage_dir / "candidates" / f"batch_{batch_size}.pt"
        save_checkpoint(checkpoint, result["model"])
        checkpoint_by_batch[batch_size] = checkpoint

    selected = min(rows, key=_selection_key)
    selected_batch = int(selected["batch_size"])
    selected_model = load_checkpoint(
        checkpoint_by_batch[selected_batch], "vgg", device
    )
    selected_config = PartBTrainingConfig(
        learning_rate=float(b1["selected_learning_rate"]),
        batch_size=selected_batch,
        seed=SELECTION_SEED,
        max_epochs=max_epochs,
        num_workers=num_workers,
    )
    test_metrics = evaluate_classifier(selected_model, data.test, selected_config, device)
    final_checkpoint = stage_dir / "selected_model.pt"
    save_checkpoint(final_checkpoint, selected_model)

    write_csv(stage_dir / "search_results.csv", rows)
    write_json(stage_dir / "histories.json", {label: history for label, history in histories})
    summary = {
        "model": "vgg",
        "learning_rate": float(b1["selected_learning_rate"]),
        "selected_batch_size": selected_batch,
        "selection_seed": SELECTION_SEED,
        "selection_criterion": "lowest validation classification error; validation loss tie-break",
        "best_epoch": int(selected["best_epoch"]),
        "validation": {
            key.removeprefix("validation_"): value
            for key, value in selected.items()
            if key.startswith("validation_")
        },
        "test": test_metrics,
        "checkpoint": str(final_checkpoint),
    }
    write_json(stage_dir / "summary.json", summary)
    return summary


def run_b3(
    data: PartBData,
    output_root: Path,
    device: torch.device,
    *,
    quick: bool,
    num_workers: int,
) -> dict:
    b1 = read_json(output_root / "b1" / "summary.json")
    b2 = read_json(output_root / "b2" / "summary.json")
    config = PartBTrainingConfig(
        learning_rate=float(b1["selected_learning_rate"]),
        batch_size=int(b2["selected_batch_size"]),
        seed=SELECTION_SEED,
        max_epochs=2 if quick else 20,
        num_workers=num_workers,
    )
    result = _train_candidate("resnet", data, config, device)
    test_metrics = evaluate_classifier(result["model"], data.test, config, device)
    checkpoint = output_root / "b3" / "selected_model.pt"
    save_checkpoint(checkpoint, result["model"])
    write_csv(output_root / "b3" / "history.csv", result["history"])

    summary = {
        "model": "resnet",
        "learning_rate": config.learning_rate,
        "batch_size": config.batch_size,
        "selection_seed": SELECTION_SEED,
        "best_epoch": result["best_epoch"],
        "validation": result["validation"],
        "test": test_metrics,
        "checkpoint": str(checkpoint),
    }
    write_json(output_root / "b3" / "summary.json", summary)

    comparison = []
    for model_name, stage in (("alexnet", "b1"), ("vgg", "b2"), ("resnet", "b3")):
        stage_summary = read_json(output_root / stage / "summary.json")
        model = build_part_b_model(model_name)
        comparison.append(
            {
                "model": model_name,
                "accuracy": stage_summary["test"]["accuracy"],
                "sensitivity": stage_summary["test"]["sensitivity"],
                "specificity": stage_summary["test"]["specificity"],
                "classification_error": stage_summary["test"]["classification_error"],
                "trainable_parameters": count_trainable_parameters(model),
                "conv_linear_flops": count_conv_linear_flops(model),
            }
        )
    write_csv(output_root / "b3" / "architecture_comparison.csv", comparison)
    write_json(
        output_root / "b3" / "flop_convention.json",
        {
            "definition": "two FLOPs per multiply-accumulate",
            "included": ["Conv2d", "Linear"],
            "excluded": ["BatchNorm", "ReLU", "pooling", "residual addition"],
            "input_shape": [1, 1, 64, 64],
        },
    )
    return summary


def _gradcam_for_model(model, images, device):
    model.eval()
    images = images.to(device)
    captured = {}

    def capture_activations(_module, _inputs, output):
        captured["activations"] = output
        output.retain_grad()

    handle = model.gradcam_layer.register_forward_hook(capture_activations)
    try:
        model.zero_grad(set_to_none=True)
        logits = model(images)
        logits.sum().backward()
        activations = captured["activations"]
        gradients = activations.grad
        if gradients is None:
            raise RuntimeError("Grad-CAM target layer did not retain gradients")
        channel_weights = gradients.mean(dim=(2, 3), keepdim=True)
        attribution = torch.relu((channel_weights * activations).sum(dim=1, keepdim=True))
        attribution = F.interpolate(
            attribution,
            size=images.shape[-2:],
            mode="bilinear",
            align_corners=False,
        )
    finally:
        handle.remove()

    attribution = attribution.detach().cpu().squeeze(1)
    flat = attribution.flatten(1)
    minima = flat.min(dim=1).values[:, None, None]
    maxima = flat.max(dim=1).values[:, None, None]
    return (attribution - minima) / (maxima - minima).clamp_min(1e-12)


def run_b4(data: PartBData, output_root: Path, device: torch.device) -> dict:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from .part_b_plots import plot_validation_curves

    plot_specs = (
        ("b1", "B1 AlexNet-like learning-rate search"),
        ("b2", "B2 VGG-like batch-size search"),
    )
    for stage, title in plot_specs:
        histories = read_json(output_root / stage / "histories.json")
        labelled_histories = list(histories.items())
        plot_validation_curves(
            labelled_histories,
            output_root / "figures" / f"{stage}_validation_loss.png",
            metric="loss",
            ylabel="Validation BCE loss",
            title=title,
        )
        plot_validation_curves(
            labelled_histories,
            output_root / "figures" / f"{stage}_validation_accuracy.png",
            metric="accuracy",
            ylabel="Validation accuracy",
            title=title,
        )

    test_images, test_labels = data.test.tensors
    pneumonia_indices = torch.where(test_labels == 1)[0].numpy()
    rng = np.random.default_rng(GRADCAM_SEED)
    selected_indices = np.sort(rng.choice(pneumonia_indices, size=5, replace=False))
    selected_images = test_images[selected_indices]
    display_images = selected_images * data.train_std + data.train_mean
    display_images = display_images.clamp(0.0, 1.0).squeeze(1).numpy()

    model_specs = (("alexnet", "b1"), ("vgg", "b2"), ("resnet", "b3"))
    heatmaps = {}
    for model_name, stage in model_specs:
        summary = read_json(output_root / stage / "summary.json")
        model = load_checkpoint(summary["checkpoint"], model_name, device)
        heatmaps[model_name] = _gradcam_for_model(model, selected_images, device).numpy()

    fig, axes = plt.subplots(3, 5, figsize=(13, 7.6))
    for row, (model_name, _) in enumerate(model_specs):
        for column in range(5):
            axes[row, column].imshow(display_images[column], cmap="gray", vmin=0, vmax=1)
            axes[row, column].imshow(
                heatmaps[model_name][column], cmap="jet", alpha=0.42, vmin=0, vmax=1
            )
            axes[row, column].axis("off")
            if row == 0:
                axes[row, column].set_title(f"Test index {selected_indices[column]}")
            if column == 0:
                axes[row, column].annotate(
                    f"{model_name}\nlike",
                    xy=(-0.10, 0.5),
                    xycoords="axes fraction",
                    ha="right",
                    va="center",
                    fontsize=11,
                    fontweight="bold",
                    annotation_clip=False,
                )
    fig.suptitle("B4 Grad-CAM on the same five pneumonia test images")
    fig.tight_layout()
    figure_path = output_root / "figures" / "b4_gradcam_comparison.png"
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_path, dpi=220, bbox_inches="tight")
    plt.close(fig)

    summary = {
        "selection_seed": GRADCAM_SEED,
        "label_definition": {"0": "normal/healthy", "1": "pneumonia"},
        "test_indices": selected_indices.tolist(),
        "models": [name for name, _ in model_specs],
        "figure": str(figure_path),
    }
    write_json(output_root / "b4" / "summary.json", summary)
    return summary


def run_smoke(
    data: PartBData,
    output_root: Path,
    device: torch.device,
    num_workers: int,
) -> dict:
    train_subset = Subset(data.train, range(min(256, len(data.train))))
    validation_subset = Subset(
        data.validation, range(min(128, len(data.validation)))
    )
    config = PartBTrainingConfig(
        learning_rate=1e-3,
        batch_size=64,
        max_epochs=1,
        patience=1,
        num_workers=num_workers,
    )
    result = train_classifier(
        build_part_b_model("alexnet"),
        train_subset,
        validation_subset,
        config,
        device,
    )
    summary = {
        "device": str(device),
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda,
        "gpu_name": (
            torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        ),
        "training_config": asdict(config),
        "validation": result["validation"],
        "status": "passed",
    }
    write_json(output_root / "smoke" / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SC4001 PA1 Part B experiments")
    parser.add_argument(
        "--stage",
        choices=["smoke", "b1", "b2", "b3", "b4", "train", "all"],
        default="smoke",
    )
    parser.add_argument("--device", default="auto", help="auto, cpu, mps, or cuda")
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--num-workers", type=int, default=0)
    args = parser.parse_args()

    device = resolve_device(args.device)
    data = load_part_b_data(args.data)
    set_part_b_seed(SELECTION_SEED)
    output_root = Path("outputs/smoke/part_b") if args.quick else OUTPUT_ROOT
    output_root.mkdir(parents=True, exist_ok=True)
    write_json(
        output_root / "data_summary.json",
        {
            "train_rows": len(data.train),
            "validation_rows": len(data.validation),
            "test_rows": len(data.test),
            "train_mean_scaled": data.train_mean,
            "train_population_std_scaled": data.train_std,
            "label_definition": {"0": "normal/healthy", "1": "pneumonia"},
        },
    )
    write_json(
        output_root / f"runtime_{args.stage}.json",
        {
            "python_version": platform.python_version(),
            "torch_version": torch.__version__,
            "torch_cuda_build": torch.version.cuda,
            "device": str(device),
            "cuda_available": torch.cuda.is_available(),
            "gpu_name": (
                torch.cuda.get_device_name(0) if device.type == "cuda" else None
            ),
            "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
    )

    if args.stage == "smoke":
        result = run_smoke(data, output_root, device, args.num_workers)
        print(json.dumps(result, indent=2))
        return
    if args.stage in {"b1", "train", "all"}:
        run_b1(
            data,
            output_root,
            device,
            quick=args.quick,
            num_workers=args.num_workers,
        )
    if args.stage in {"b2", "train", "all"}:
        run_b2(
            data,
            output_root,
            device,
            quick=args.quick,
            num_workers=args.num_workers,
        )
    if args.stage in {"b3", "train", "all"}:
        run_b3(
            data,
            output_root,
            device,
            quick=args.quick,
            num_workers=args.num_workers,
        )
    if args.stage in {"b4", "all"}:
        run_b4(data, output_root, device)
    print(f"Part B stage '{args.stage}' completed on {device}: {output_root}")


if __name__ == "__main__":
    main()
