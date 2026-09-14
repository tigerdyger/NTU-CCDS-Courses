# SC4001 PA1 Part B: Chest X-ray Classification

This archive contains the code required to reproduce Part B. Place the supplied
`chestxray_binary_64.npz` file in the archive root before running the commands
below. Generated files are written to `outputs/part_b/`.

## Labels and architecture rules

- Label 0 is normal/healthy; label 1 is pneumonia and is the positive class.
- B1 applies dropout p=0.5 only after ReLU in hidden `fc,64` and `fc,32`.
- B2 and B3 use no dropout.
- Every convolution is followed by batch normalization and ReLU and has no
  bias. Fully connected layers use bias.
- The final `fc,1` layer returns one raw logit, passed directly to
  `BCEWithLogitsLoss` without sigmoid.

## Local environment and checks

The project supports Python 3.11--3.14. `pyproject.toml` and `uv.lock` specify
the local environment; the core dependencies are PyTorch 2.x, NumPy 2.x, and
Matplotlib 3.11+.

```bash
uv sync
uv run python -m pytest -q
uv run python -m src.run_part_b --stage smoke --device auto
```

Model selection uses seed 42 and Grad-CAM sampling uses seed 2026. Adam is used
for at most 20 epochs. Early stopping monitors validation BCE loss with patience
4 and minimum improvement 1e-4. B1 learning rate and B2 batch size are selected
by validation classification error at their loss-selected checkpoints, with
validation loss as a deterministic tie-break. The test split is evaluated only
after selection.

## TC1 GPU reproduction

The verified TC1 environment is Python 3.11.14, PyTorch 2.5.1+cu118, CUDA build
11.8, NumPy 2.1.3, and one Tesla V100 32 GB. From the project directory on TC1,
submit each job only after the previous job has completed successfully and its
corresponding `.err` file in `outputs/slurm/` is empty:

```bash
mkdir -p outputs/slurm
sbatch cluster/tc1_setup_env.sbatch
sbatch cluster/tc1_environment_probe.sbatch
sbatch cluster/tc1_gpu_smoke.sbatch
sbatch cluster/tc1_part_b.sbatch
```

The final job trains B1--B3. Copy `outputs/part_b/` back to the local project,
then generate the validation plots and B4 Grad-CAM figure from the saved
checkpoints:

```bash
rsync -av USER@TC1_HOST:~/sc4001-pa1/outputs/part_b/ outputs/part_b/
uv run python -m src.run_part_b --stage b4 --device cpu
```

On a CUDA-capable local system, the whole pipeline can instead be run with:

```bash
uv run python -m src.run_part_b --stage all --device auto
```
