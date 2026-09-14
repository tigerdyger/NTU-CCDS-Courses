# SC4001 Programming Assignment 1

本目录用于完成 SC4001 Programming Assignment 1，包括：

- Part A：HDB resale price prediction（组屋转售价格预测）
- Part B：Chest X-ray binary classification（胸部 X 光二分类）

## 当前结构

```text
pa-01/
├── src/                         # 起始代码与后续实现
├── hdb_price_prediction.csv     # 本地数据，不纳入 Git
├── chestxray_binary_64.npz      # 本地数据，不纳入 Git
├── outputs/                     # 训练输出，不纳入 Git
├── submission/                  # 最终提交文件，不纳入 Git
├── pyproject.toml
└── uv.lock
```

## 环境与依赖

本地实验使用 Python 3.12；项目支持 Python 3.11--3.14。精确依赖由
`pyproject.toml` 和 `uv.lock` 固定，主要依赖为 PyTorch 2.x、NumPy 2.x、
Pandas 3.x、Matplotlib 3.11+、Ray Tune 2.58+、Captum 0.9+，测试使用
pytest 8--9。

```bash
uv sync
uv run python -m pytest -q
```

起始基线可用以下命令运行：

```bash
uv run python -m src.baseline
```

## Part A 实验

先运行快速检查：

```bash
uv run python -m pytest -q
uv run python -m src.run_part_a --quick --stage all --workers 2
```

再运行完整实验：

```bash
uv run python -m src.run_part_a --stage all --workers 4
```

所有原始指标、汇总表和报告图片生成在 `outputs/part_a/`。A1 的 2022 test
curve（测试曲线）仅按题目要求记录，不用于选择 epoch、模型或超参数。

Part A 的模型选择使用 seed 42；多次运行使用 seeds 42、123、456、789、
2026。实验记录随机种子、超参数、最佳 epoch（轮次）、validation metrics
（验证指标）与 test metrics（测试指标），并确保 test set（测试集）不参与模型选择。

## Part B 实验

课程讨论区已明确以下实现边界：

- label 0 表示 normal/healthy，label 1 表示 pneumonia；计算 sensitivity 时以 pneumonia 为 positive class。
- 只有 B1 AlexNet-like 使用 dropout：分别放在 `fc,64` 和 `fc,32` 的 ReLU 后，`p=0.5`。
- B2 VGG-like 与 B3 ResNet-like 不使用 dropout。
- 三个模型的最终 `fc,1` 都输出 raw logit；不接 ReLU、dropout 或 sigmoid，直接传给 `BCEWithLogitsLoss`。

本地 CPU/MPS smoke test：

```bash
uv run python -m pytest -q
uv run python -m src.run_part_b --stage smoke --device auto
```

完整实验应在确认学校 TC1 当前 QoS 后，通过 Compute Node 执行。首次运行时
依次提交环境安装、环境探针和 smoke test，确认各作业成功且 `.err` 为空后再
提交完整训练：

```bash
mkdir -p outputs/slurm
sbatch cluster/tc1_setup_env.sbatch
sbatch cluster/tc1_environment_probe.sbatch
sbatch cluster/tc1_gpu_smoke.sbatch
sbatch cluster/tc1_part_b.sbatch
```

`cluster/*.sbatch` 中的 partition、QoS、memory 和 wall time 已于 2026-09-13
使用 `MyTCInfo` 核对。Head Node 只用于登录、文件传输和 `sbatch`，不得直接运行训练。

TC1 当前的 `CZ4042_v6` 使用 PyTorch 2.7/CUDA 12.8，无法在 V100（compute capability 7.0）执行 kernel；`v4/v5` 又存在 `iJIT_NotifyEvent` 链接错误。因此先用 `tc1_setup_env.sbatch` 在个人 home 中创建最小 `torch==2.5.1+cu118` 环境，再运行 probe/smoke。集群脚本只运行 `--stage train`（B1--B3）；同步 checkpoint 和 JSON/CSV 回本机后，运行 `--stage b4`，以原生 PyTorch Grad-CAM 同时生成 B1/B2 曲线和 B4 图。

例如，从本机仓库根目录同步远端输出（替换用户名和主机）并生成 B4：

```bash
rsync -av USER@TC1_HOST:~/sc4001-pa1/outputs/part_b/ outputs/part_b/
uv run python -m src.run_part_b --stage b4 --device cpu
```

如果本机具备 CUDA，也可直接运行完整流水线：

```bash
uv run python -m src.run_part_b --stage all --device auto
```

Part B 流水线以 validation BCE loss 监控 early stopping 并保存每个候选模型的最佳 epoch checkpoint；B1 learning rate 和 B2 batch size 再按该 checkpoint 的 validation classification error 选择，validation loss 只用于超参数并列时的确定性 tie-break。选定后才各评估一次 test split；所有输出保存在 `outputs/part_b/`。

为保证超参数比较公平，随机种子在每个候选模型构建前设置，因此同一架构的候选从相同初始权重开始。TC1 脚本同时设置 `CUBLAS_WORKSPACE_CONFIG=:4096:8` 并启用 PyTorch deterministic algorithms；固定 64x64 输入使用等价的固定 average pooling，避免 adaptive pooling 的非确定性 CUDA backward。

Part B 的模型选择 seed 为 42，Grad-CAM 抽样 seed 为 2026。已验证的 TC1
运行环境为 Python 3.11.14、PyTorch 2.5.1+cu118、CUDA build 11.8、
NumPy 2.1.3 和 Tesla V100 32 GB。

## 提交要求摘要

- 分别提交 Part A 与 Part B 的 PDF report（报告）和 code ZIP（代码压缩包）。
- 每份报告少于 6 页。
- 使用 Adam optimizer（Adam 优化器），最多训练 20 epochs（轮次）。
- early stopping（提前停止）的 patience（耐心值）为 4，minimum improvement（最小改进量）为 `1e-4`。
- 报告开头声明生成式 AI 工具的用途以及人工核验方式。
