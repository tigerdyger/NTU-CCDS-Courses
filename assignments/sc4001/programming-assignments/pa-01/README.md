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

## 环境与起始基线

```bash
uv sync
uv run python -m src.baseline
```

## Part A 实验

先运行快速检查：

```bash
PYTHONPATH=src uv run python -m unittest discover -s tests -v
uv run python -m src.run_part_a --quick --stage all --workers 2
```

再运行完整实验：

```bash
uv run python -m src.run_part_a --stage all --workers 4
```

所有原始指标、汇总表和报告图片生成在 `outputs/part_a/`。A1 的 2022 test
curve（测试曲线）仅按题目要求记录，不用于选择 epoch、模型或超参数。

实验应记录随机种子、超参数、最佳 epoch（轮次）、validation metrics（验证指标）与 test metrics（测试指标），并确保 test set（测试集）不参与模型选择。

## 提交要求摘要

- 分别提交 Part A 与 Part B 的 PDF report（报告）和 code ZIP（代码压缩包）。
- 每份报告少于 6 页。
- 使用 Adam optimizer（Adam 优化器），最多训练 20 epochs（轮次）。
- early stopping（提前停止）的 patience（耐心值）为 4，minimum improvement（最小改进量）为 `1e-4`。
- 报告开头声明生成式 AI 工具的用途以及人工核验方式。
