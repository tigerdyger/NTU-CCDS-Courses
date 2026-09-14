# SC4001 PA1 Part A: HDB Price Prediction

This archive contains the code required to reproduce Part A. Place the supplied
`hdb_price_prediction.csv` file in the archive root before running the commands
below. Generated files are written to `outputs/part_a/`.

## Environment and dependencies

The submitted runs used Python 3.12.13. The project supports Python
3.11--3.14. `pyproject.toml` and `uv.lock` specify the reproducible environment;
the main dependencies are PyTorch 2.x, NumPy 2.x, Pandas 3.x, Matplotlib
3.11+, Ray Tune 2.58+, and Captum 0.9+.

Install [uv](https://docs.astral.sh/uv/), then run:

```bash
uv sync
PYTHONPATH=src uv run python -m unittest discover -s tests -v
```

## Reproduction commands

A quick end-to-end check is:

```bash
uv run python -m src.run_part_a --quick --stage all --workers 2
```

The full experiment used:

```bash
uv run python -m src.run_part_a --stage all --workers 4
```

Model selection uses seed 42. Repeated experiments use seeds 42, 123, 456,
789, and 2026. Adam is used for at most 20 epochs. Early stopping monitors
validation RMSE with patience 4 and minimum improvement 1e-4. A3 selects both
lambda and its final epoch budget on the validation split. The 2022 test
curve requested in A1 is recorded only after selection and is never used to
choose an epoch, model, or hyperparameter.

Raw metrics, aggregate tables, checkpoints, and report figures are written to
`outputs/part_a/`.
