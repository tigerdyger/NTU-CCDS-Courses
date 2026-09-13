from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BLUE = "#2457A6"
ORANGE = "#D57A1F"
GREY = "#5C6670"


def _finish(fig, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def block_diagram(output_path):
    fig, ax = plt.subplots(figsize=(10, 2.8))
    ax.axis("off")
    boxes = [
        (0.02, "4 categorical\nfeatures"),
        (0.20, "4 embedding\ntables"),
        (0.39, "Concatenate with\n6 continuous features"),
        (0.61, "Linear + LayerNorm\n+ ReLU"),
        (0.81, "Linear(64, 1)"),
    ]
    widths = [0.14, 0.14, 0.18, 0.16, 0.14]
    for (x, label), width in zip(boxes, widths):
        ax.add_patch(
            plt.Rectangle(
                (x, 0.35),
                width,
                0.30,
                facecolor="#EAF0F8",
                edgecolor=BLUE,
                lw=1.5,
            )
        )
        ax.text(x + width / 2, 0.50, label, ha="center", va="center", fontsize=9)
    for index in range(len(boxes) - 1):
        start = boxes[index][0] + widths[index]
        end = boxes[index + 1][0]
        ax.annotate(
            "", xy=(end, 0.50), xytext=(start, 0.50), arrowprops={"arrowstyle": "->"}
        )
    ax.text(
        0.88,
        0.24,
        "standardised output -> SGD",
        ha="center",
        fontsize=9,
        color=GREY,
    )
    _finish(fig, output_path)


def grid_heatmap(rows, output_path):
    widths = sorted({int(row["hidden_width"]) for row in rows})
    dims = sorted({int(row["embedding_dim"]) for row in rows})
    matrix = np.full((len(dims), len(widths)), np.nan)
    for row in rows:
        i = dims.index(int(row["embedding_dim"]))
        j = widths.index(int(row["hidden_width"]))
        matrix[i, j] = float(row["best_validation_rmse"]) / 1000.0

    fig, ax = plt.subplots(figsize=(7, 4.8))
    image = ax.imshow(matrix, cmap="Blues_r", aspect="auto")
    for i in range(len(dims)):
        for j in range(len(widths)):
            ax.text(j, i, f"{matrix[i, j]:.1f}", ha="center", va="center", fontsize=9)
    ax.set_xticks(range(len(widths)), widths)
    ax.set_yticks(range(len(dims)), dims)
    ax.set_xlabel("Hidden-layer width")
    ax.set_ylabel("Common embedding dimension")
    ax.set_title("A1 grid search: best validation RMSE (thousand SGD)")
    fig.colorbar(image, ax=ax, label="Validation RMSE (thousand SGD)")
    _finish(fig, output_path)


def learning_curve(history, second_key, second_label, title, output_path):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    epochs = [row["epoch"] for row in history]
    ax.plot(
        epochs,
        [row["train_rmse"] for row in history],
        marker="o",
        color=BLUE,
        label="Training",
    )
    ax.plot(
        epochs,
        [row[second_key] for row in history],
        marker="s",
        color=ORANGE,
        label=second_label,
    )
    ax.set_xlabel("Epoch")
    ax.set_ylabel("RMSE (SGD)")
    ax.set_title(title)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    _finish(fig, output_path)


def model_comparison(summary_rows, title, output_path):
    labels = [row["model"] for row in summary_rows]
    x = np.arange(len(labels))
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    axes[0].bar(
        x,
        [row["rmse_mean"] for row in summary_rows],
        yerr=[row["rmse_sample_std"] for row in summary_rows],
        color=BLUE,
        alpha=0.88,
        capsize=4,
    )
    axes[0].set_ylabel("Test RMSE (SGD)")
    axes[0].set_xticks(x, labels, rotation=18, ha="right")
    axes[0].set_title("RMSE: mean +/- sample SD")
    axes[1].bar(
        x,
        [row["r2_mean"] for row in summary_rows],
        yerr=[row["r2_sample_std"] for row in summary_rows],
        color=ORANGE,
        alpha=0.88,
        capsize=4,
    )
    axes[1].set_ylabel("Test R-squared")
    axes[1].set_xticks(x, labels, rotation=18, ha="right")
    axes[1].set_title("R-squared: mean +/- sample SD")
    fig.suptitle(title)
    _finish(fig, output_path)


def lambda_curve(rows, output_path):
    rows = sorted(rows, key=lambda row: float(row["lambda"]))
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.plot(
        [float(row["lambda"]) for row in rows],
        [float(row["best_validation_rmse"]) for row in rows],
        marker="o",
        color=BLUE,
    )
    ax.set_xlabel("lambda")
    ax.set_ylabel("Best validation RMSE (SGD)")
    ax.set_title("A3 wide-and-deep lambda selection")
    ax.grid(alpha=0.25)
    _finish(fig, output_path)


def attribution_bars(rows, output_path):
    models = ["baseline", "wide_deep"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
    for ax, model in zip(axes, models):
        selected = sorted(
            [row for row in rows if row["model"] == model],
            key=lambda row: float(row["importance_sgd"]),
        )
        ax.barh(
            [row["feature"] for row in selected],
            [float(row["importance_sgd"]) for row in selected],
            color=BLUE if model == "baseline" else ORANGE,
            alpha=0.9,
        )
        ax.set_xlabel("Mean absolute attribution (SGD)")
        ax.set_title("Baseline" if model == "baseline" else "Wide-and-deep")
        ax.grid(axis="x", alpha=0.2)
    fig.suptitle("A4 global FeatureAblation importance")
    _finish(fig, output_path)
