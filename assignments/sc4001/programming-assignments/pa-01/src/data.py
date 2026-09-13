from collections import Counter

import pandas as pd
import torch
from torch.utils.data import TensorDataset

from .config import Config


def make_dataset(rows, category_maps, means, stds, config):
    categorical = torch.tensor(
        [
            [
                category_maps[name].get(row[name], 0)
                for name in config.categorical_features
            ]
            for row in rows
        ],
        dtype=torch.long,
    )
    continuous = torch.tensor(
        [[float(row[name]) for name in config.continuous_features] for row in rows],
        dtype=torch.float32,
    )
    continuous = (continuous - means) / stds

    target = torch.tensor(
        [float(row["resale_price"]) for row in rows], dtype=torch.float32
    )
    return TensorDataset(categorical, continuous, target)


def _fit_preprocessor(rows, config):
    category_maps = {}
    category_baselines = []
    for name in config.categorical_features:
        values = sorted({row[name] for row in rows})
        category_maps[name] = {value: index + 1 for index, value in enumerate(values)}

        counts = Counter(row[name] for row in rows)
        mode = min(counts, key=lambda value: (-counts[value], str(value)))
        category_baselines.append(category_maps[name][mode])

    continuous = torch.tensor(
        [
            [float(row[name]) for name in config.continuous_features]
            for row in rows
        ],
        dtype=torch.float32,
    )
    means = continuous.mean(dim=0)
    stds = continuous.std(dim=0).clamp_min(1e-8)

    target = torch.tensor(
        [float(row["resale_price"]) for row in rows], dtype=torch.float32
    )
    target_mean = target.mean().item()
    target_std = target.std(unbiased=False).clamp_min(1e-8).item()

    return {
        "category_maps": category_maps,
        "category_baselines": torch.tensor(category_baselines, dtype=torch.long),
        "continuous_means": means,
        "continuous_stds": stds,
        "target_mean": target_mean,
        "target_std": target_std,
    }


def prepare_data(csv_path, config: Config, fit_on_combined: bool = False):
    """Prepare the temporal split without using 2022 test data for preprocessing.

    During model selection, preprocessing is fitted on 2017--2020 only. During
    final retraining, ``fit_on_combined=True`` refits the same preprocessing
    procedure on 2017--2021, after all hyperparameters and the epoch budget have
    already been selected.
    """

    data = pd.read_csv(csv_path)
    rows = data.to_dict(orient="records")

    train_rows = [row for row in rows if int(row["year"]) in config.train_years]
    validation_rows = [
        row for row in rows if int(row["year"]) == config.validation_year
    ]
    test_rows = [row for row in rows if int(row["year"]) == config.test_year]
    combined_rows = train_rows + validation_rows

    fit_rows = combined_rows if fit_on_combined else train_rows
    fitted = _fit_preprocessor(fit_rows, config)
    maps = fitted["category_maps"]
    means = fitted["continuous_means"]
    stds = fitted["continuous_stds"]

    return {
        "train": make_dataset(train_rows, maps, means, stds, config),
        "validation": make_dataset(validation_rows, maps, means, stds, config),
        "combined": make_dataset(combined_rows, maps, means, stds, config),
        "test": make_dataset(test_rows, maps, means, stds, config),
        "cardinalities": [
            len(maps[name]) + 1 for name in config.categorical_features
        ],
        "category_maps": maps,
        "category_baselines": fitted["category_baselines"],
        "continuous_means": means,
        "continuous_stds": stds,
        "target_mean": fitted["target_mean"],
        "target_std": fitted["target_std"],
    }
