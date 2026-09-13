import unittest

import torch

from src.config import Config
from src.model import PriceModel, WideDeepPriceModel
from src.training import count_trainable_parameters


class PartAModelTests(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.cardinalities = [13, 27, 44, 18]

    def test_baseline_parameter_count(self):
        model = PriceModel(self.cardinalities, 500_000.0, 100_000.0, self.config)
        self.assertEqual(count_trainable_parameters(model), 3505)

    def test_model_output_shapes(self):
        categorical = torch.zeros((7, 4), dtype=torch.long)
        continuous = torch.zeros((7, 6))
        baseline = PriceModel(
            self.cardinalities, 500_000.0, 100_000.0, self.config
        )
        wide_deep = WideDeepPriceModel(
            self.cardinalities, 500_000.0, 100_000.0, self.config, 0.5
        )
        self.assertEqual(tuple(baseline(categorical, continuous).shape), (7,))
        self.assertEqual(tuple(wide_deep(categorical, continuous).shape), (7,))

    def test_continuous_only_removes_embeddings(self):
        model = PriceModel(
            self.cardinalities,
            500_000.0,
            100_000.0,
            self.config,
            use_categorical=False,
        )
        self.assertEqual(len(model.encoder.embeddings), 0)
        self.assertEqual(model.mlp[0].in_features, 6)


if __name__ == "__main__":
    unittest.main()
