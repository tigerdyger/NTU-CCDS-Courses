# SC4001 Programming Assignment 1

本作业包括 Part A（组屋转售价格预测）和 Part B（胸部 X 光二分类），已完成提交。本公开目录仅保留环境配置和通用环境脚本，不提供作业答案或完整可运行的实验副本。

## 发布范围

本目录采用默认忽略、逐项放行的规则，只公开以下文件：

- `README.md` 与 `.gitignore`。
- `.python-version`、`pyproject.toml` 与 `uv.lock`。
- `cluster/tc1_setup_env.sbatch` 与 `cluster/tc1_environment_probe.sbatch`。

作业代码、测试、报告源文件及 PDF、教师数据、实验输出、模型权重、提交包和详细实验说明继续保存在本地。新增文件也默认被忽略，扩大公开范围前须单独检查并明确修改白名单。

原有详细 README 原样保存在本地 `LOCAL_PROGRESS.md`；该文件不公开。公开 Git 不是上述本地材料的备份。

这些规则限制后续添加文件，不会删除已经存在于旧提交中的内容；本次整理不改写 Git 历史。

## 本地依赖配置

`.python-version` 指定本地 Python 3.12；依赖声明位于 `pyproject.toml`，解析后的版本位于 `uv.lock`。如需重建本地环境，可在本目录执行：

```bash
uv sync --locked
```

项目声明的 Python 版本范围不代表每种系统与设备组合都经过测试。依赖安装本身也不意味着能够运行作业：代码、数据及结果文件不随公开仓库提供。

## TC1 环境脚本

两个 Slurm 脚本仅用于安装最小 GPU 环境和检查 CUDA，不包含模型训练、评估或作业实现。

- `tc1_setup_env.sbatch`：加载集群 Python 3.11 与 uv，安装指定的 PyTorch CUDA 11.8 和 NumPy 版本。
- `tc1_environment_probe.sbatch`：申请一块 GPU，输出环境版本并执行简单张量运算。

这套集群环境与本地 `uv.lock` 是两套不同配置，不能混用。本次只检查脚本及发布范围，不重新安装环境、申请 GPU 或重跑实验。

使用前先确认当前账号的 partition、QoS、软件模块与资源配额仍适用，并在提交目录创建日志目录：

```bash
mkdir -p outputs/slurm
```

先提交安装作业，确认成功后再提交 GPU 检查作业：

```bash
sbatch cluster/tc1_setup_env.sbatch
```

```bash
sbatch cluster/tc1_environment_probe.sbatch
```

目标环境可通过 `SC4001_VENV` 指定，默认是 `~/sc4001-venv`。安装脚本会修改目标环境中的软件包；若该环境正被其他实验复用，不应随意重复运行安装。所有集群环境安装和 GPU 检查都通过 Slurm 计算节点执行。
