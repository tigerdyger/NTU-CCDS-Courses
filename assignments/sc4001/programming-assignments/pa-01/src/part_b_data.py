from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import TensorDataset


EXPECTED_KEYS = (
    "train_images",
    "train_labels",
    "val_images",
    "val_labels",
    "test_images",
    "test_labels",
)


@dataclass(frozen=True)
class PartBData:
    train: TensorDataset
    validation: TensorDataset
    test: TensorDataset
    train_mean: float
    train_std: float


def _validate_split(images: np.ndarray, labels: np.ndarray, split: str) -> None:
    if images.ndim != 3 or images.shape[1:] != (64, 64):
        raise ValueError(
            f"{split}_images must have shape [N, 64, 64], got {images.shape}"
        )
    if labels.shape != (len(images),):
        raise ValueError(
            f"{split}_labels must have shape [{len(images)}], got {labels.shape}"
        )
    if images.dtype != np.uint8:
        raise ValueError(f"{split}_images must use uint8, got {images.dtype}")
    unique_labels = set(np.unique(labels).tolist())
    if not unique_labels.issubset({0, 1}):
        raise ValueError(f"{split}_labels contain values outside {{0, 1}}")


def _make_dataset(
    images: np.ndarray,
    labels: np.ndarray,
    mean: float,
    std: float,
) -> TensorDataset:
    image_tensor = torch.from_numpy(images.astype(np.float32) / 255.0).unsqueeze(1)
    image_tensor = (image_tensor - mean) / std
    label_tensor = torch.from_numpy(labels.astype(np.float32))
    return TensorDataset(image_tensor, label_tensor)


def load_part_b_data(npz_path: str | Path) -> PartBData:
    """Load the official split and fit normalisation on training images only.

    The course discussion board confirms that label 0 is normal/healthy and
    label 1 is pneumonia. No data augmentation is applied because the handout
    does not request one.
    """

    with np.load(npz_path, allow_pickle=False) as archive:
        missing = sorted(set(EXPECTED_KEYS) - set(archive.files))
        unexpected = sorted(set(archive.files) - set(EXPECTED_KEYS))
        if missing or unexpected:
            raise ValueError(
                f"Unexpected NPZ schema: missing={missing}, unexpected={unexpected}"
            )
        arrays = {key: archive[key] for key in EXPECTED_KEYS}

    for split, prefix in (("train", "train"), ("validation", "val"), ("test", "test")):
        _validate_split(arrays[f"{prefix}_images"], arrays[f"{prefix}_labels"], split)

    scaled_train = arrays["train_images"].astype(np.float64) / 255.0
    train_mean = float(scaled_train.mean())
    train_std = float(scaled_train.std(ddof=0))
    if not np.isfinite(train_std) or train_std <= 0.0:
        raise ValueError(f"Training-image standard deviation is invalid: {train_std}")

    return PartBData(
        train=_make_dataset(
            arrays["train_images"], arrays["train_labels"], train_mean, train_std
        ),
        validation=_make_dataset(
            arrays["val_images"], arrays["val_labels"], train_mean, train_std
        ),
        test=_make_dataset(
            arrays["test_images"], arrays["test_labels"], train_mean, train_std
        ),
        train_mean=train_mean,
        train_std=train_std,
    )
