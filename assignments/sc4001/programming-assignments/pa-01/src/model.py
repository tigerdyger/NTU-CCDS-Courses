import torch
from torch import nn

from .config import Config


def _activation(name: str) -> nn.Module:
    if name == "relu":
        return nn.ReLU()
    if name == "sigmoid":
        return nn.Sigmoid()
    raise ValueError(f"Unsupported activation: {name}")


class FeatureEncoder(nn.Module):
    def __init__(
        self,
        cardinalities: list[int],
        config: Config,
        use_categorical: bool = True,
    ) -> None:
        super().__init__()
        self.use_categorical = use_categorical
        self.embeddings = nn.ModuleList()
        if use_categorical:
            self.embeddings = nn.ModuleList(
                nn.Embedding(cardinality, width)
                for cardinality, width in zip(cardinalities, config.embedding_dims)
            )
        self.output_width = len(config.continuous_features)
        if use_categorical:
            self.output_width += sum(config.embedding_dims)

    def forward(
        self, categorical: torch.Tensor, continuous: torch.Tensor
    ) -> torch.Tensor:
        if not self.use_categorical:
            return continuous
        embedded = [
            embedding(categorical[:, index])
            for index, embedding in enumerate(self.embeddings)
        ]
        return torch.cat(embedded + [continuous], dim=1)


class PriceModel(nn.Module):
    def __init__(
        self,
        cardinalities: list[int],
        target_mean: float,
        target_std: float,
        config: Config,
        *,
        activation: str = "relu",
        use_categorical: bool = True,
    ) -> None:
        super().__init__()
        self.encoder = FeatureEncoder(cardinalities, config, use_categorical)
        self.mlp = nn.Sequential(
            nn.Linear(self.encoder.output_width, config.hidden_width),
            nn.LayerNorm(config.hidden_width),
            _activation(activation),
            nn.Linear(config.hidden_width, 1),
        )
        self.target_mean = target_mean
        self.target_std = target_std

    def forward(
        self, categorical: torch.Tensor, continuous: torch.Tensor
    ) -> torch.Tensor:
        features = self.encoder(categorical, continuous)
        return self.mlp(features).squeeze(1)

    def predict_price(
        self, categorical: torch.Tensor, continuous: torch.Tensor
    ) -> torch.Tensor:
        return self(categorical, continuous) * self.target_std + self.target_mean


class WideDeepPriceModel(nn.Module):
    def __init__(
        self,
        cardinalities: list[int],
        target_mean: float,
        target_std: float,
        config: Config,
        wide_weight: float,
    ) -> None:
        super().__init__()
        self.encoder = FeatureEncoder(cardinalities, config, use_categorical=True)
        self.deep = nn.Sequential(
            nn.Linear(self.encoder.output_width, config.hidden_width),
            nn.LayerNorm(config.hidden_width),
            nn.ReLU(),
            nn.Linear(config.hidden_width, 1),
        )
        self.wide = nn.Linear(self.encoder.output_width, 1)
        self.wide_weight = float(wide_weight)
        self.target_mean = target_mean
        self.target_std = target_std

    def forward(
        self, categorical: torch.Tensor, continuous: torch.Tensor
    ) -> torch.Tensor:
        features = self.encoder(categorical, continuous)
        deep_output = self.deep(features)
        wide_output = self.wide(features)
        return (deep_output + self.wide_weight * wide_output).squeeze(1)

    def predict_price(
        self, categorical: torch.Tensor, continuous: torch.Tensor
    ) -> torch.Tensor:
        return self(categorical, continuous) * self.target_std + self.target_mean
