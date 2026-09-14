from collections.abc import Callable

import torch
from torch import nn


class ConvBnRelu(nn.Sequential):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        *,
        stride: int = 1,
    ) -> None:
        padding = kernel_size // 2
        super().__init__(
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size,
                stride=stride,
                padding=padding,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=False),
        )


class AlexNetLike(nn.Module):
    """Figure B1, with dropout only after the two hidden FC ReLUs."""

    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            ConvBnRelu(1, 16, 5),
            nn.MaxPool2d(2),
            ConvBnRelu(16, 32, 5),
            nn.MaxPool2d(2),
            ConvBnRelu(32, 64, 3),
            nn.MaxPool2d(2),
        )
        # The input is fixed at 64x64, so the feature map is 8x8 here.
        # Fixed pooling is equivalent to adaptive 4x4 pooling and has a
        # deterministic CUDA backward implementation.
        self.average_pool = nn.AvgPool2d(kernel_size=2)
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 4 * 4, 64),
            nn.ReLU(inplace=False),
            nn.Dropout(p=0.5),
            nn.Linear(64, 32),
            nn.ReLU(inplace=False),
            nn.Dropout(p=0.5),
            nn.Linear(32, 1),
        )

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        features = self.average_pool(self.features(images))
        return self.classifier(features).squeeze(1)

    @property
    def gradcam_layer(self) -> nn.Module:
        """Return the final activated convolutional feature map."""

        return self.features[4]


class VGGLike(nn.Module):
    """Figure B2. The course clarification specifies no dropout."""

    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            ConvBnRelu(1, 8, 3),
            ConvBnRelu(8, 8, 3),
            nn.MaxPool2d(2),
            ConvBnRelu(8, 16, 3),
            ConvBnRelu(16, 16, 3),
            nn.MaxPool2d(2),
            ConvBnRelu(16, 32, 3),
            ConvBnRelu(32, 32, 3),
            nn.MaxPool2d(2),
        )
        self.average_pool = nn.AvgPool2d(kernel_size=8)
        self.output = nn.Linear(32, 1)

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        features = self.average_pool(self.features(images)).flatten(1)
        return self.output(features).squeeze(1)

    @property
    def gradcam_layer(self) -> nn.Module:
        return self.features[6]


class ResidualBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, stride: int) -> None:
        super().__init__()
        self.conv1 = ConvBnRelu(
            in_channels, out_channels, 3, stride=stride
        )
        # The handout requires BN and ReLU after every convolution, including
        # the second convolution in a residual branch.
        self.conv2 = ConvBnRelu(out_channels, out_channels, 3)
        if stride == 1 and in_channels == out_channels:
            self.skip = nn.Identity()
        else:
            # A projection is also a convolutional layer, so it follows the
            # same Conv-BN-ReLU rule as the main branch.
            self.skip = ConvBnRelu(
                in_channels, out_channels, 1, stride=stride
            )
        self.relu = nn.ReLU(inplace=False)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        residual = self.skip(inputs)
        features = self.conv2(self.conv1(inputs))
        return self.relu(features + residual)


class ResNetLike(nn.Module):
    """Figure B3. It has no dropout and returns one unrestricted logit."""

    def __init__(self) -> None:
        super().__init__()
        self.stem = nn.Sequential(ConvBnRelu(1, 16, 3), nn.MaxPool2d(2))
        self.blocks = nn.Sequential(
            ResidualBlock(16, 16, stride=1),
            ResidualBlock(16, 32, stride=2),
            ResidualBlock(32, 64, stride=2),
        )
        self.average_pool = nn.AvgPool2d(kernel_size=8)
        self.output = nn.Linear(64, 1)

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        features = self.blocks(self.stem(images))
        features = self.average_pool(features).flatten(1)
        return self.output(features).squeeze(1)

    @property
    def gradcam_layer(self) -> nn.Module:
        # Target the final activated convolutional feature map, before the
        # residual addition, consistently with B1 and B2.
        return self.blocks[2].conv2


MODEL_BUILDERS: dict[str, Callable[[], nn.Module]] = {
    "alexnet": AlexNetLike,
    "vgg": VGGLike,
    "resnet": ResNetLike,
}


def build_part_b_model(name: str) -> nn.Module:
    try:
        return MODEL_BUILDERS[name]()
    except KeyError as error:
        raise ValueError(f"Unknown Part B model: {name}") from error


def count_trainable_parameters(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)


def count_conv_linear_flops(model: nn.Module, input_shape=(1, 1, 64, 64)) -> int:
    """Count Conv2d/Linear FLOPs using two FLOPs per multiply-accumulate.

    BatchNorm, activation, pooling and residual-add costs are excluded. The
    convention is explicit because the handout does not define how FLOPs are
    counted.
    """

    total = 0
    hooks = []

    def conv_hook(module: nn.Conv2d, _inputs, output) -> None:
        nonlocal total
        output_elements = output.numel()
        kernel_ops = (
            module.kernel_size[0]
            * module.kernel_size[1]
            * module.in_channels
            // module.groups
        )
        total += 2 * output_elements * kernel_ops

    def linear_hook(module: nn.Linear, _inputs, output) -> None:
        nonlocal total
        total += 2 * output.numel() * module.in_features

    for layer in model.modules():
        if isinstance(layer, nn.Conv2d):
            hooks.append(layer.register_forward_hook(conv_hook))
        elif isinstance(layer, nn.Linear):
            hooks.append(layer.register_forward_hook(linear_hook))

    try:
        was_training = model.training
        model.eval()
        with torch.no_grad():
            model(torch.zeros(input_shape))
        model.train(was_training)
    finally:
        for hook in hooks:
            hook.remove()
    return total
