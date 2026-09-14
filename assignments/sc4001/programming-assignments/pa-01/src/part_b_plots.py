from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


COLORS = ["#2457A6", "#D57A1F", "#3A8D5D", "#8A55A0", "#B33A3A"]


def plot_validation_curves(
    histories: list[tuple[str, list[dict]]],
    output_path: str | Path,
    *,
    metric: str,
    ylabel: str,
    title: str,
) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for color, (label, history) in zip(COLORS, histories):
        ax.plot(
            [row["epoch"] for row in history],
            [row[f"validation_{metric}"] for row in history],
            marker="o",
            markersize=3,
            color=color,
            label=label,
        )
    ax.set_xlabel("Epoch")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
