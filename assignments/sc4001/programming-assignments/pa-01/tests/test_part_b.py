import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch
from torch import nn

from src.part_b_data import load_part_b_data
from src.part_b_models import (
    AlexNetLike,
    ResNetLike,
    VGGLike,
    count_conv_linear_flops,
    count_trainable_parameters,
)
from src.part_b_training import (
    PartBTrainingConfig,
    binary_metrics_from_logits,
    train_classifier,
)
from src.run_part_b import _gradcam_for_model


class PartBDataTests(unittest.TestCase):
    def test_normalisation_is_fitted_on_training_images_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "small.npz"
            train_images = np.stack(
                [np.zeros((64, 64), dtype=np.uint8), np.full((64, 64), 255, np.uint8)]
            )
            validation_images = np.full((2, 64, 64), 64, dtype=np.uint8)
            test_images = np.full((2, 64, 64), 192, dtype=np.uint8)
            labels = np.array([0, 1], dtype=np.int64)
            np.savez(
                path,
                train_images=train_images,
                train_labels=labels,
                val_images=validation_images,
                val_labels=labels,
                test_images=test_images,
                test_labels=labels,
            )
            data = load_part_b_data(path)

        train_tensor, _ = data.train.tensors
        self.assertAlmostEqual(data.train_mean, 0.5)
        self.assertAlmostEqual(data.train_std, 0.5)
        self.assertAlmostEqual(float(train_tensor.mean()), 0.0, places=6)
        self.assertAlmostEqual(float(train_tensor.std(unbiased=False)), 1.0, places=6)
        self.assertEqual(tuple(train_tensor.shape), (2, 1, 64, 64))


class PartBModelTests(unittest.TestCase):
    def test_all_models_return_one_raw_logit_per_image(self):
        images = torch.randn(3, 1, 64, 64)
        for model in (AlexNetLike(), VGGLike(), ResNetLike()):
            with self.subTest(model=type(model).__name__):
                output = model(images)
                self.assertEqual(tuple(output.shape), (3,))
                self.assertFalse(isinstance(list(model.modules())[-1], nn.Sigmoid))

    def test_dropout_is_used_only_in_b1_hidden_fully_connected_layers(self):
        alexnet_dropouts = [m for m in AlexNetLike().modules() if isinstance(m, nn.Dropout)]
        vgg_dropouts = [m for m in VGGLike().modules() if isinstance(m, nn.Dropout)]
        resnet_dropouts = [m for m in ResNetLike().modules() if isinstance(m, nn.Dropout)]
        self.assertEqual([layer.p for layer in alexnet_dropouts], [0.5, 0.5])
        self.assertEqual(vgg_dropouts, [])
        self.assertEqual(resnet_dropouts, [])

    def test_parameter_and_flop_counts_are_positive_and_ordered(self):
        models = [AlexNetLike(), VGGLike(), ResNetLike()]
        parameter_counts = [count_trainable_parameters(model) for model in models]
        flop_counts = [count_conv_linear_flops(model) for model in models]
        self.assertTrue(all(value > 0 for value in parameter_counts))
        self.assertTrue(all(value > 0 for value in flop_counts))
        self.assertGreater(parameter_counts[0], parameter_counts[1])

    def test_gradcam_targets_are_not_registered_as_duplicate_parameters(self):
        images = torch.randn(2, 1, 64, 64)
        for model in (AlexNetLike(), VGGLike(), ResNetLike()):
            with self.subTest(model=type(model).__name__):
                self.assertFalse(
                    any(key.startswith("last_conv.") for key in model.state_dict())
                )
                heatmaps = _gradcam_for_model(model, images, torch.device("cpu"))
                self.assertEqual(tuple(heatmaps.shape), (2, 64, 64))
                self.assertTrue(torch.isfinite(heatmaps).all())
                self.assertGreaterEqual(float(heatmaps.min()), 0.0)
                self.assertLessEqual(float(heatmaps.max()), 1.0)

    def test_resnet_gradcam_targets_the_final_convolutional_branch(self):
        model = ResNetLike()
        self.assertIs(model.gradcam_layer, model.blocks[2].conv2)

    def test_fixed_input_models_do_not_use_adaptive_average_pooling(self):
        for model in (AlexNetLike(), VGGLike(), ResNetLike()):
            with self.subTest(model=type(model).__name__):
                self.assertFalse(
                    any(isinstance(layer, nn.AdaptiveAvgPool2d) for layer in model.modules())
                )

    def test_every_convolution_is_immediately_followed_by_bn_and_relu(self):
        for model in (AlexNetLike(), VGGLike(), ResNetLike()):
            checked_convolutions = 0
            for container in model.modules():
                children = list(container.children())
                for index, child in enumerate(children):
                    if not isinstance(child, nn.Conv2d):
                        continue
                    checked_convolutions += 1
                    self.assertLess(index + 2, len(children))
                    self.assertIsInstance(children[index + 1], nn.BatchNorm2d)
                    self.assertIsInstance(children[index + 2], nn.ReLU)
                    self.assertIsNone(child.bias)
            with self.subTest(model=type(model).__name__):
                self.assertGreater(checked_convolutions, 0)


class PartBMetricTests(unittest.TestCase):
    def test_binary_metrics_use_pneumonia_as_positive_class(self):
        logits = torch.tensor([2.0, -2.0, 1.0, -1.0])
        labels = torch.tensor([1, 0, 0, 1])
        metrics = binary_metrics_from_logits(logits, labels)
        self.assertEqual(metrics["true_positive"], 1)
        self.assertEqual(metrics["true_negative"], 1)
        self.assertEqual(metrics["false_positive"], 1)
        self.assertEqual(metrics["false_negative"], 1)
        self.assertEqual(metrics["accuracy"], 0.5)
        self.assertEqual(metrics["sensitivity"], 0.5)
        self.assertEqual(metrics["specificity"], 0.5)


class PartBTrainingTests(unittest.TestCase):
    def test_best_epoch_and_early_stopping_monitor_validation_loss(self):
        model = nn.Linear(1, 1, bias=False)
        with torch.no_grad():
            model.weight.zero_()
        dataset = torch.utils.data.TensorDataset(
            torch.zeros(1, 1), torch.zeros(1)
        )
        validation_by_epoch = {
            1: (0.50, 0.20),
            2: (0.40, 0.30),
            3: (0.45, 0.10),
        }

        def fake_train_epoch(candidate, *_args, **_kwargs):
            with torch.no_grad():
                candidate.weight.add_(1.0)
            return 0.0

        def fake_evaluate(candidate, *_args, **_kwargs):
            epoch = int(round(float(candidate.weight.item())))
            loss, classification_error = validation_by_epoch[epoch]
            return {
                "loss": loss,
                "accuracy": 1.0 - classification_error,
                "classification_error": classification_error,
                "sensitivity": 1.0,
                "specificity": 1.0,
                "true_positive": 1,
                "true_negative": 1,
                "false_positive": 0,
                "false_negative": 0,
            }

        config = PartBTrainingConfig(
            learning_rate=1e-3,
            batch_size=1,
            max_epochs=3,
            patience=3,
        )
        with (
            patch("src.part_b_training._train_epoch", side_effect=fake_train_epoch),
            patch("src.part_b_training.evaluate_classifier", side_effect=fake_evaluate),
        ):
            result = train_classifier(
                model, dataset, dataset, config, torch.device("cpu")
            )

        self.assertEqual(result["best_epoch"], 2)
        self.assertAlmostEqual(float(result["model"].weight.item()), 2.0)
        self.assertEqual(result["validation"]["loss"], 0.40)
        # Epoch 3 has the better classification error but the worse loss, so
        # it must not replace the early-stopping checkpoint.
        self.assertEqual(result["validation"]["classification_error"], 0.30)


if __name__ == "__main__":
    unittest.main()
