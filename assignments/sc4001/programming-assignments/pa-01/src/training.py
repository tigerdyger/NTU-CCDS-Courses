import copy
import random
from dataclasses import asdict

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader


def set_seed(seed: int) -> None:
    # Ray trials and local retraining must use the same CPU reduction order.
    # Otherwise identical seeds can still give slightly different results.
    torch.set_num_threads(1)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)


def count_trainable_parameters(model: nn.Module) -> int:
    return sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )


@torch.no_grad()
def evaluate_model(model, dataset, batch_size: int, device: torch.device) -> dict:
    model.eval()
    predictions = []
    targets = []
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    for categorical, continuous, target in loader:
        categorical = categorical.to(device)
        continuous = continuous.to(device)
        predictions.append(model.predict_price(categorical, continuous).cpu())
        targets.append(target.cpu())

    prediction = torch.cat(predictions)
    target = torch.cat(targets)
    squared_error = (prediction - target).square()
    rmse = squared_error.mean().sqrt().item()
    denominator = (target - target.mean()).square().sum()
    r2 = (1.0 - squared_error.sum() / denominator).item()
    return {"rmse": rmse, "r2": r2}


def _train_epoch(model, loader, optimiser, loss_function, device) -> float:
    model.train()
    squared_error = 0.0
    row_count = 0
    for categorical, continuous, target in loader:
        categorical = categorical.to(device)
        continuous = continuous.to(device)
        target = target.to(device)

        optimiser.zero_grad()
        standard_prediction = model(categorical, continuous)
        standard_target = (target - model.target_mean) / model.target_std
        loss = loss_function(standard_prediction, standard_target)
        loss.backward()
        optimiser.step()

        prediction = standard_prediction.detach() * model.target_std + model.target_mean
        squared_error += (prediction - target).square().sum().item()
        row_count += len(target)
    return (squared_error / row_count) ** 0.5


def _training_loader(dataset, batch_size: int, seed: int) -> DataLoader:
    generator = torch.Generator().manual_seed(seed)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        generator=generator,
    )


def train_with_validation(model, train_data, validation_data, config, device):
    model.to(device)
    loader = _training_loader(train_data, config.batch_size, config.seed)
    optimiser = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    loss_function = nn.MSELoss()

    best_rmse = float("inf")
    best_weights = None
    best_epoch = 0
    epochs_without_improvement = 0
    history = []

    for epoch in range(1, config.max_epochs + 1):
        train_rmse = _train_epoch(model, loader, optimiser, loss_function, device)
        validation = evaluate_model(
            model, validation_data, config.batch_size, device
        )
        history.append(
            {
                "epoch": epoch,
                "train_rmse": train_rmse,
                "validation_rmse": validation["rmse"],
            }
        )

        if best_weights is None or validation["rmse"] < (
            best_rmse - config.early_stopping_threshold
        ):
            best_rmse = validation["rmse"]
            best_weights = copy.deepcopy(model.state_dict())
            best_epoch = epoch
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= config.early_stopping_patience:
                break

    if best_weights is None:
        raise RuntimeError("Training completed without recording model weights")
    model.load_state_dict(best_weights)
    return {
        "model": model,
        "history": history,
        "best_epoch": best_epoch,
        "best_validation_rmse": best_rmse,
        "config": asdict(config),
    }


def train_fixed_epochs(model, train_data, test_data, config, epochs: int, device):
    """Retrain after selection; the test curve is logged but never used to stop."""

    model.to(device)
    loader = _training_loader(train_data, config.batch_size, config.seed)
    optimiser = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    loss_function = nn.MSELoss()
    history = []

    for epoch in range(1, epochs + 1):
        train_rmse = _train_epoch(model, loader, optimiser, loss_function, device)
        test = evaluate_model(model, test_data, config.batch_size, device)
        history.append(
            {
                "epoch": epoch,
                "train_rmse": train_rmse,
                "test_rmse": test["rmse"],
                "test_r2": test["r2"],
            }
        )

    return {
        "model": model,
        "history": history,
        "test": evaluate_model(model, test_data, config.batch_size, device),
        "epochs": epochs,
        "config": asdict(config),
    }
