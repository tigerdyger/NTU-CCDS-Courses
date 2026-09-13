import argparse
import csv
import json
import statistics
from dataclasses import replace
from pathlib import Path

import torch
from captum.attr import FeatureAblation
from ray import tune

from .config import Config
from .data import prepare_data
from .model import PriceModel, WideDeepPriceModel
from .part_a_plots import (
    attribution_bars,
    block_diagram,
    grid_heatmap,
    lambda_curve,
    learning_curve,
    model_comparison,
)
from .training import (
    count_trainable_parameters,
    set_seed,
    train_fixed_epochs,
    train_with_validation,
)


DATA_PATH = Path("hdb_price_prediction.csv")
FULL_OUTPUT_ROOT = Path("outputs/part_a")
SEEDS = [42, 123, 456, 789, 2026]


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows available for {path}")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_config(hidden_width, embedding_dim, seed, max_epochs=20):
    return replace(
        Config(),
        hidden_width=int(hidden_width),
        embedding_dims=(int(embedding_dim),) * 4,
        seed=int(seed),
        max_epochs=int(max_epochs),
    )


def build_baseline(data, config, activation="relu", use_categorical=True):
    return PriceModel(
        data["cardinalities"],
        data["target_mean"],
        data["target_std"],
        config,
        activation=activation,
        use_categorical=use_categorical,
    )


def build_wide_deep(data, config, wide_weight):
    return WideDeepPriceModel(
        data["cardinalities"],
        data["target_mean"],
        data["target_std"],
        config,
        wide_weight=wide_weight,
    )


def a1_trial(search_config, data_path, max_epochs):
    torch.set_num_threads(1)
    config = build_config(
        search_config["hidden_width"],
        search_config["embedding_dim"],
        seed=42,
        max_epochs=max_epochs,
    )
    set_seed(config.seed)
    data = prepare_data(data_path, config, fit_on_combined=False)
    result = train_with_validation(
        build_baseline(data, config),
        data["train"],
        data["validation"],
        config,
        torch.device("cpu"),
    )
    tune.report(
        {
            "best_validation_rmse": result["best_validation_rmse"],
            "best_epoch": result["best_epoch"],
        }
    )


def run_a1(output_root, quick=False, workers=4):
    a1_dir = output_root / "a1"
    figures = output_root / "figures"
    widths = [16, 32] if quick else [16, 32, 64, 128, 256]
    dimensions = [2, 4] if quick else [2, 4, 8, 12, 16]
    max_epochs = 3 if quick else 20

    trainable = tune.with_parameters(
        a1_trial, data_path=str(DATA_PATH.resolve()), max_epochs=max_epochs
    )
    trainable = tune.with_resources(trainable, {"cpu": 1})
    tuner = tune.Tuner(
        trainable,
        param_space={
            "hidden_width": tune.grid_search(widths),
            "embedding_dim": tune.grid_search(dimensions),
        },
        tune_config=tune.TuneConfig(max_concurrent_trials=workers),
        run_config=tune.RunConfig(
            name="a1_grid",
            storage_path=str((output_root / "ray").resolve()),
            verbose=0,
        ),
    )
    result_grid = tuner.fit()

    rows = []
    errors = []
    for result in result_grid:
        if result.error:
            errors.append(str(result.error))
            continue
        rows.append(
            {
                "hidden_width": int(result.config["hidden_width"]),
                "embedding_dim": int(result.config["embedding_dim"]),
                "best_epoch": int(result.metrics["best_epoch"]),
                "best_validation_rmse": float(
                    result.metrics["best_validation_rmse"]
                ),
            }
        )
    if errors:
        raise RuntimeError("Ray trials failed:\n" + "\n".join(errors))
    if len(rows) != len(widths) * len(dimensions):
        raise RuntimeError(
            f"Expected {len(widths) * len(dimensions)} trials, got {len(rows)}"
        )
    rows.sort(key=lambda row: (row["hidden_width"], row["embedding_dim"]))
    write_csv(a1_dir / "grid_results.csv", rows)

    selected = min(rows, key=lambda row: row["best_validation_rmse"])
    config = build_config(
        selected["hidden_width"],
        selected["embedding_dim"],
        seed=42,
        max_epochs=max_epochs,
    )
    set_seed(config.seed)
    selection_data = prepare_data(DATA_PATH, config, fit_on_combined=False)
    selected_run = train_with_validation(
        build_baseline(selection_data, config),
        selection_data["train"],
        selection_data["validation"],
        config,
        torch.device("cpu"),
    )
    write_csv(a1_dir / "selected_learning_curve.csv", selected_run["history"])

    final_epochs = selected_run["best_epoch"]
    set_seed(config.seed)
    final_data = prepare_data(DATA_PATH, config, fit_on_combined=True)
    final_model = build_baseline(final_data, config)
    final_run = train_fixed_epochs(
        final_model,
        final_data["combined"],
        final_data["test"],
        config,
        final_epochs,
        torch.device("cpu"),
    )
    torch.save(
        final_run["model"].cpu().state_dict(), a1_dir / "final_model_seed_42.pt"
    )
    write_csv(a1_dir / "final_learning_curve.csv", final_run["history"])

    default_config = Config()
    default_data = prepare_data(DATA_PATH, default_config, fit_on_combined=False)
    default_model = build_baseline(default_data, default_config)
    summary = {
        "baseline_trainable_parameters": count_trainable_parameters(default_model),
        "selected_hidden_width": config.hidden_width,
        "selected_embedding_dimension": config.embedding_dims[0],
        "selected_epoch_budget": final_epochs,
        "best_validation_rmse": float(selected["best_validation_rmse"]),
        "selected_rerun_validation_rmse": selected_run[
            "best_validation_rmse"
        ],
        "final_test_rmse": final_run["test"]["rmse"],
        "final_test_r2": final_run["test"]["r2"],
        "selection_seed": 42,
        "preprocessing_fit_for_selection": "2017-2020",
        "preprocessing_fit_for_final_model": "2017-2021",
        "test_year": 2022,
    }
    write_json(a1_dir / "summary.json", summary)

    block_diagram(figures / "a1_baseline_block_diagram.png")
    grid_heatmap(rows, figures / "a1_grid_search_heatmap.png")
    learning_curve(
        selected_run["history"],
        "validation_rmse",
        "Validation",
        "A1 selected configuration: training and validation RMSE",
        figures / "a1_selection_learning_curve.png",
    )
    learning_curve(
        final_run["history"],
        "test_rmse",
        "Test (not used for selection)",
        "A1 final retraining: training and test RMSE",
        figures / "a1_final_learning_curve.png",
    )
    return summary


def summarise_runs(runs, model_order):
    summary = []
    for model in model_order:
        selected = [row for row in runs if row["model"] == model]
        rmse = [float(row["test_rmse"]) for row in selected]
        r2 = [float(row["test_r2"]) for row in selected]
        summary.append(
            {
                "model": model,
                "rmse_mean": statistics.mean(rmse),
                "rmse_sample_std": statistics.stdev(rmse),
                "r2_mean": statistics.mean(r2),
                "r2_sample_std": statistics.stdev(r2),
                "n_seeds": len(selected),
            }
        )
    return summary


def run_a2(output_root, quick=False):
    a1 = read_json(output_root / "a1" / "summary.json")
    seeds = SEEDS[:2] if quick else SEEDS
    epochs = int(a1["selected_epoch_budget"])
    max_epochs = 3 if quick else 20
    runs = []
    variants = [
        ("baseline_relu", "relu", True),
        ("continuous_only", "relu", False),
        ("baseline_sigmoid", "sigmoid", True),
    ]
    for model_name, activation, use_categorical in variants:
        for seed in seeds:
            config = build_config(
                a1["selected_hidden_width"],
                a1["selected_embedding_dimension"],
                seed,
                max_epochs,
            )
            set_seed(seed)
            data = prepare_data(DATA_PATH, config, fit_on_combined=True)
            result = train_fixed_epochs(
                build_baseline(data, config, activation, use_categorical),
                data["combined"],
                data["test"],
                config,
                epochs,
                torch.device("cpu"),
            )
            runs.append(
                {
                    "model": model_name,
                    "seed": seed,
                    "epochs": epochs,
                    "test_rmse": result["test"]["rmse"],
                    "test_r2": result["test"]["r2"],
                }
            )

    summary = summarise_runs(runs, [name for name, _, _ in variants])
    write_csv(output_root / "a2" / "runs.csv", runs)
    write_csv(output_root / "a2" / "summary.csv", summary)
    model_comparison(
        summary,
        "A2 ablation results across five seeds",
        output_root / "figures" / "a2_ablation_comparison.png",
    )
    return summary


def run_a3(output_root, quick=False):
    a1 = read_json(output_root / "a1" / "summary.json")
    seeds = SEEDS[:2] if quick else SEEDS
    lambdas = [0.0, 0.25] if quick else [0.0, 0.25, 0.5, 1.0, 2.0]
    max_epochs = 3 if quick else 20
    search_rows = []
    for wide_weight in lambdas:
        config = build_config(
            a1["selected_hidden_width"],
            a1["selected_embedding_dimension"],
            42,
            max_epochs,
        )
        set_seed(config.seed)
        data = prepare_data(DATA_PATH, config, fit_on_combined=False)
        result = train_with_validation(
            build_wide_deep(data, config, wide_weight),
            data["train"],
            data["validation"],
            config,
            torch.device("cpu"),
        )
        search_rows.append(
            {
                "lambda": wide_weight,
                "best_epoch": result["best_epoch"],
                "best_validation_rmse": result["best_validation_rmse"],
            }
        )

    selected = min(search_rows, key=lambda row: row["best_validation_rmse"])
    write_csv(output_root / "a3" / "lambda_search.csv", search_rows)
    lambda_curve(search_rows, output_root / "figures" / "a3_lambda_search.png")

    runs = []
    epochs = int(a1["selected_epoch_budget"])
    for seed in seeds:
        config = build_config(
            a1["selected_hidden_width"],
            a1["selected_embedding_dimension"],
            seed,
            max_epochs,
        )
        set_seed(seed)
        data = prepare_data(DATA_PATH, config, fit_on_combined=True)
        result = train_fixed_epochs(
            build_wide_deep(data, config, selected["lambda"]),
            data["combined"],
            data["test"],
            config,
            epochs,
            torch.device("cpu"),
        )
        if seed == 42:
            torch.save(
                result["model"].cpu().state_dict(),
                output_root / "a3" / "final_model_seed_42.pt",
            )
        runs.append(
            {
                "model": "wide_deep",
                "seed": seed,
                "lambda": selected["lambda"],
                "epochs": epochs,
                "test_rmse": result["test"]["rmse"],
                "test_r2": result["test"]["r2"],
            }
        )
    write_csv(output_root / "a3" / "runs.csv", runs)
    wide_summary = summarise_runs(runs, ["wide_deep"])[0]

    baseline_runs_path = output_root / "a2" / "runs.csv"
    with baseline_runs_path.open(encoding="utf-8") as stream:
        baseline_runs = [
            row
            for row in csv.DictReader(stream)
            if row["model"] == "baseline_relu"
        ]
    baseline_summary = summarise_runs(baseline_runs, ["baseline_relu"])[0]
    comparison = [baseline_summary, wide_summary]
    write_csv(output_root / "a3" / "comparison_summary.csv", comparison)
    selected_summary = {
        "selected_lambda": selected["lambda"],
        "selection_best_validation_rmse": selected["best_validation_rmse"],
        "selection_seed": 42,
        "final_epoch_budget": epochs,
        "five_seed_summary": wide_summary,
    }
    write_json(output_root / "a3" / "summary.json", selected_summary)
    model_comparison(
        comparison,
        "A3 baseline versus wide-and-deep",
        output_root / "figures" / "a3_model_comparison.png",
    )
    return selected_summary


class PriceOutput(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, categorical, continuous):
        return self.model.predict_price(categorical.long(), continuous)


def feature_ablation_importance(model, data, config):
    model.eval()
    wrapper = PriceOutput(model)
    ablation = FeatureAblation(wrapper)
    categorical, continuous, _ = data["test"].tensors
    category_baseline = data["category_baselines"].unsqueeze(0)
    continuous_baseline = torch.zeros((1, len(config.continuous_features)))
    categorical_mask = torch.arange(len(config.categorical_features)).unsqueeze(0)
    continuous_mask = (
        torch.arange(len(config.continuous_features)).unsqueeze(0)
        + len(config.categorical_features)
    )

    total = torch.zeros(10)
    batch_size = config.batch_size
    for start in range(0, len(categorical), batch_size):
        end = min(start + batch_size, len(categorical))
        attr_categorical, attr_continuous = ablation.attribute(
            (categorical[start:end], continuous[start:end]),
            baselines=(category_baseline, continuous_baseline),
            feature_mask=(categorical_mask, continuous_mask),
            perturbations_per_eval=10,
        )
        batch_attribution = torch.cat([attr_categorical, attr_continuous], dim=1)
        total += batch_attribution.abs().sum(dim=0)
    return total / len(categorical)


def run_a4(output_root):
    a1 = read_json(output_root / "a1" / "summary.json")
    a3 = read_json(output_root / "a3" / "summary.json")
    config = build_config(
        a1["selected_hidden_width"],
        a1["selected_embedding_dimension"],
        seed=42,
    )
    data = prepare_data(DATA_PATH, config, fit_on_combined=True)

    baseline = build_baseline(data, config)
    baseline.load_state_dict(
        torch.load(
            output_root / "a1" / "final_model_seed_42.pt", weights_only=True
        )
    )
    wide_deep = build_wide_deep(data, config, a3["selected_lambda"])
    wide_deep.load_state_dict(
        torch.load(
            output_root / "a3" / "final_model_seed_42.pt", weights_only=True
        )
    )

    features = list(config.categorical_features) + list(config.continuous_features)
    rows = []
    for model_name, model in [("baseline", baseline), ("wide_deep", wide_deep)]:
        importance = feature_ablation_importance(model, data, config)
        rows.extend(
            {
                "model": model_name,
                "feature": feature,
                "importance_sgd": float(score),
            }
            for feature, score in zip(features, importance)
        )
    write_csv(output_root / "a4" / "feature_importance.csv", rows)
    write_json(
        output_root / "a4" / "baseline_definition.json",
        {
            "categorical_baseline": "training-set mode for each feature",
            "continuous_baseline": (
                "training-set mean, represented by zero after standardisation"
            ),
            "preprocessing_fit": "2017-2021 combined training data",
            "attribution_output_unit": "Singapore dollars",
            "test_samples": len(data["test"]),
        },
    )
    attribution_bars(rows, output_root / "figures" / "a4_feature_importance.png")
    return rows


def main():
    parser = argparse.ArgumentParser(description="Run SC4001 Part A experiments")
    parser.add_argument(
        "--stage", choices=["a1", "a2", "a3", "a4", "all"], default="all"
    )
    parser.add_argument("--quick", action="store_true", help="Run a small smoke test")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    output_root = Path("outputs/smoke/part_a") if args.quick else FULL_OUTPUT_ROOT
    output_root.mkdir(parents=True, exist_ok=True)

    if args.stage in {"a1", "all"}:
        run_a1(output_root, quick=args.quick, workers=args.workers)
    if args.stage in {"a2", "all"}:
        run_a2(output_root, quick=args.quick)
    if args.stage in {"a3", "all"}:
        run_a3(output_root, quick=args.quick)
    if args.stage in {"a4", "all"}:
        run_a4(output_root)
    print(f"Part A stage '{args.stage}' completed. Results: {output_root}")


if __name__ == "__main__":
    main()
