"""Reconstruct Tutorial 4 Q2 decision regions from the published parameters.

Source parameters: ``tute4_ans.pdf``, PDF page 31 (SC4001 Tutorial 4).
The script also verifies that all six training samples are classified correctly.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


OUTPUT_PATH = Path(__file__).with_name("source") / "tutorial-04-q2-decision-regions.png"


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


def predict(inputs: np.ndarray) -> np.ndarray:
    # Rows index incoming units and columns index outgoing units.
    hidden_weights = np.array(
        [[-1.81, 0.32, 0.08], [-1.40, 2.92, 1.91]], dtype=float
    )
    hidden_bias = np.array([4.36, 0.73, -1.71], dtype=float)
    output_weights = np.array(
        [
            [2.93, -5.33, 3.12],
            [2.80, 1.20, -3.87],
            [0.09, 4.55, -3.47],
        ],
        dtype=float,
    )
    output_bias = np.array([-1.94, -0.06, 2.01], dtype=float)

    hidden = sigmoid(inputs @ hidden_weights + hidden_bias)
    logits = hidden @ output_weights + output_bias
    return np.argmax(logits, axis=1)


def main() -> None:
    training_inputs = np.array(
        [[1, 1], [0, 1], [3, 4], [2, 2], [2, -2], [-2, -3]], dtype=float
    )
    training_labels = np.array([0, 0, 1, 1, 2, 2])
    predicted_labels = predict(training_inputs)
    if not np.array_equal(predicted_labels, training_labels):
        raise RuntimeError(
            f"Published parameters misclassify training data: {predicted_labels}"
        )

    resolution = 801
    coordinates = np.linspace(-4, 4, resolution)
    grid_x, grid_y = np.meshgrid(coordinates, coordinates[::-1])
    grid = np.column_stack((grid_x.ravel(), grid_y.ravel()))
    regions = predict(grid).reshape(grid_x.shape)

    region_colors = np.array(
        [[220, 235, 250], [248, 226, 203], [221, 241, 223]], dtype=np.uint8
    )
    plot_array = region_colors[regions]
    boundary = np.zeros_like(regions, dtype=bool)
    boundary[:, 1:] |= regions[:, 1:] != regions[:, :-1]
    boundary[1:, :] |= regions[1:, :] != regions[:-1, :]
    plot_array[boundary] = np.array([39, 55, 70], dtype=np.uint8)

    canvas_width, canvas_height = 1120, 980
    left, top, plot_size = 120, 65, 800
    image = Image.new("RGB", (canvas_width, canvas_height), "white")
    plot = Image.fromarray(plot_array, mode="RGB").resize(
        (plot_size, plot_size), Image.Resampling.NEAREST
    )
    image.paste(plot, (left, top))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=20)
    small_font = ImageFont.load_default(size=17)
    draw.rectangle(
        (left, top, left + plot_size, top + plot_size), outline="#17202A", width=3
    )

    def to_pixel(point: np.ndarray) -> tuple[float, float]:
        x_value, y_value = point
        x_pixel = left + (x_value + 4) / 8 * plot_size
        y_pixel = top + (4 - y_value) / 8 * plot_size
        return x_pixel, y_pixel

    for tick in range(-4, 5):
        x_pixel, y_zero = to_pixel(np.array([tick, -4]))
        draw.line((x_pixel, top + plot_size, x_pixel, top + plot_size + 8), fill="#17202A", width=2)
        draw.text((x_pixel - 9, top + plot_size + 14), str(tick), fill="#17202A", font=small_font)
        x_zero, y_pixel = to_pixel(np.array([-4, tick]))
        draw.line((left - 8, y_pixel, left, y_pixel), fill="#17202A", width=2)
        draw.text((left - 39, y_pixel - 10), str(tick), fill="#17202A", font=small_font)

    draw.text((left + plot_size / 2 - 15, top + plot_size + 54), "x1", fill="#17202A", font=font)
    draw.text((42, top + plot_size / 2 - 12), "x2", fill="#17202A", font=font)

    labels = ["class A", "class B", "class C"]
    for class_index, label in enumerate(labels):
        selected = training_labels == class_index
        for point in training_inputs[selected]:
            x_pixel, y_pixel = to_pixel(point)
            radius = 10
            if class_index == 0:
                draw.ellipse(
                    (x_pixel - radius, y_pixel - radius, x_pixel + radius, y_pixel + radius),
                    fill="white",
                    outline="#17202A",
                    width=3,
                )
            elif class_index == 1:
                draw.rectangle(
                    (x_pixel - radius, y_pixel - radius, x_pixel + radius, y_pixel + radius),
                    fill="white",
                    outline="#17202A",
                    width=3,
                )
            else:
                draw.polygon(
                    [
                        (x_pixel, y_pixel - radius - 2),
                        (x_pixel - radius - 2, y_pixel + radius),
                        (x_pixel + radius + 2, y_pixel + radius),
                    ],
                    fill="white",
                    outline="#17202A",
                )

        legend_y = top + 40 + class_index * 48
        draw.rectangle(
            (left + plot_size + 45, legend_y, left + plot_size + 75, legend_y + 30),
            fill=tuple(region_colors[class_index]),
            outline="#17202A",
            width=2,
        )
        draw.text(
            (left + plot_size + 88, legend_y + 4), label, fill="#17202A", font=small_font
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT_PATH, optimize=True)


if __name__ == "__main__":
    main()
