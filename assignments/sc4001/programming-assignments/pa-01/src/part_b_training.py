import copy
import random
from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset


@dataclass(frozen=True)
class PartBTrainingConfig:
    learning_rate: float
    batch_size: int
    seed: int = 42
    max_epochs: int = 20
    patience: int = 4
    minimum_improvement: float = 1e-4
    num_workers: int = 0


def set_part_b_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    if torch.backends.cudnn.is_available():
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True


def resolve_device(requested: str) -> torch.device:
    if requested == "auto":
        if torch.cuda.is_available():
            requested = "cuda"
        elif torch.backends.mps.is_available():
            requested = "mps"
        else:
            requested = "cpu"
    device = torch.device(requested)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but torch.cuda.is_available() is false")
    if device.type == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS was requested but torch.backends.mps.is_available() is false")
    return device


def make_loader(
    dataset: Dataset,
    batch_size: int,
    *,
    shuffle: bool,
    seed: int,
    num_workers: int,
) -> DataLoader:
    generator = torch.Generator().manual_seed(seed)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        generator=generator if shuffle else None,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
        persistent_workers=num_workers > 0,
    )


def binary_metrics_from_logits(logits: torch.Tensor, labels: torch.Tensor) -> dict:
    logits = logits.detach().cpu().flatten()
    labels = labels.detach().cpu().to(torch.int64).flatten()
    predictions = (logits >= 0.0).to(torch.int64)
    true_positive = int(((predictions == 1) & (labels == 1)).sum())
    true_negative = int(((predictions == 0) & (labels == 0)).sum())
    false_positive = int(((predictions == 1) & (labels == 0)).sum())
    false_negative = int(((predictions == 0) & (labels == 1)).sum())
    positives = true_positive + false_negative
    negatives = true_negative + false_positive
    if positives == 0 or negatives == 0:
        raise ValueError("Sensitivity and specificity require both classes")
    count = len(labels)
    accuracy = (true_positive + true_negative) / count
    return {
        "accuracy": accuracy,
        "classification_error": 1.0 - accuracy,
        "sensitivity": true_positive / positives,
        "specificity": true_negative / negatives,
        "true_positive": true_positive,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "false_negative": false_negative,
    }


@torch.no_grad()
def evaluate_classifier(
    model: nn.Module,
    dataset: Dataset,
    config: PartBTrainingConfig,
    device: torch.device,
) -> dict:
    model.eval()
    loss_function = nn.BCEWithLogitsLoss(reduction="sum")
    logits = []
    labels = []
    total_loss = 0.0
    loader = make_loader(
        dataset,
        config.batch_size,
        shuffle=False,
        seed=config.seed,
        num_workers=config.num_workers,
    )
    for images, batch_labels in loader:
        images = images.to(device, non_blocking=True)
        batch_labels = batch_labels.to(device, non_blocking=True)
        batch_logits = model(images)
        total_loss += float(loss_function(batch_logits, batch_labels))
        logits.append(batch_logits.cpu())
        labels.append(batch_labels.cpu())
    all_logits = torch.cat(logits)
    all_labels = torch.cat(labels)
    return {
        "loss": total_loss / len(all_labels),
        **binary_metrics_from_logits(all_logits, all_labels),
    }


def _train_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimiser: torch.optim.Optimizer,
    device: torch.device,
) -> float:
    model.train()
    loss_function = nn.BCEWithLogitsLoss(reduction="sum")
    total_loss = 0.0
    row_count = 0
    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        optimiser.zero_grad(set_to_none=True)
        logits = model(images)
        loss = loss_function(logits, labels)
        (loss / len(labels)).backward()
        optimiser.step()
        total_loss += float(loss.detach())
        row_count += len(labels)
    return total_loss / row_count


def train_classifier(
    model: nn.Module,
    train_data: Dataset,
    validation_data: Dataset,
    config: PartBTrainingConfig,
    device: torch.device,
) -> dict:
    """Train with early stopping and checkpoint selection by validation loss.

    B1/B2 hyperparameters are selected separately from the returned
    checkpoints by validation classification error. The test split is
    deliberately absent from this function.
    """

    set_part_b_seed(config.seed)
    model.to(device)
    loader = make_loader(
        train_data,
        config.batch_size,
        shuffle=True,
        seed=config.seed,
        num_workers=config.num_workers,
    )
    optimiser = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    best_validation_loss = float("inf")
    best_weights = None
    best_epoch = 0
    epochs_without_improvement = 0
    history = []

    for epoch in range(1, config.max_epochs + 1):
        train_loss = _train_epoch(model, loader, optimiser, device)
        validation = evaluate_classifier(model, validation_data, config, device)
        history.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                **{f"validation_{key}": value for key, value in validation.items()},
            }
        )
        loss_improved = (
            validation["loss"]
            < best_validation_loss - config.minimum_improvement
        )
        if best_weights is None or loss_improved:
            best_validation_loss = validation["loss"]
            best_weights = copy.deepcopy(model.state_dict())
            best_epoch = epoch
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= config.patience:
                break

    if best_weights is None:
        raise RuntimeError("Training completed without recording a checkpoint")
    model.load_state_dict(best_weights)
    selected_validation = evaluate_classifier(model, validation_data, config, device)
    return {
        "model": model,
        "history": history,
        "best_epoch": best_epoch,
        "validation": selected_validation,
    }
