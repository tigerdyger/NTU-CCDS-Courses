# SC3000 Lab 1 — Teaching NanoGPT to Do Math

## 当前状态

截至 2026-09-17，本作业仍在进行中：学生已实现核心训练函数与两阶段主流程，局部训练、模型保存与重载检查通过。数据、批处理和验证接口的单 notebook 整合及完整运行仍待完成，尚未达到提交状态。

本目录只公开项目说明、环境依赖和集群启动脚本，不公开正在评估的作业实现、实验数据或结果。公开仓库不是完整可运行或可提交的作业副本。

## 公开与本地内容

| 公开文件 | 用途 |
| --- | --- |
| `.gitignore` | 隔离本地作业与生成文件 |
| `requirements.in` | macOS 本地依赖声明 |
| `requirements-macos.lock` | 已解析的本地依赖版本 |
| `cluster/*.sbatch` | TC1 上的 Slurm 启动脚本，不包含训练实现或凭据 |

以下目录和文件仅在本地保存，不进入公开 Git：

- `work/`：教师 starter 工作副本、学生 notebook、数据与原始模型。
- `tests-local/`：独立诊断与接口测试。
- `outputs/`、`checkpoints/`：实验记录、日志和模型权重。
- `submission/`：最终提交材料。
- `.venv/`、`.jupyter/` 及 notebook 缓存。

详细实验记录保留在本地 `work/LOCAL_PROGRESS.md`，不随公开仓库发布。

## 本地环境

本地调试使用 Python 3.11。在本目录执行：

```bash
uv venv --python 3.11 .venv
uv pip sync --python .venv/bin/python requirements-macos.lock
```

准备好本地教师材料后，可从 `work/dpo/` 使用本实验的 Python 启动 Jupyter：

```bash
cd work/dpo
../../.venv/bin/python -m jupyterlab dpo.ipynb
```

依赖锁文件用于 macOS 本地环境，不能直接视为学校 Linux/CUDA 环境的安装清单。

## TC1 启动脚本

`cluster/` 中的脚本需要提前准备被忽略的工作文件、数据、独立诊断代码和已验证的 GPU Python 环境，仅克隆公开仓库无法运行。

脚本通过 Slurm 申请计算资源，保留调度器设置的 `CUDA_VISIBLE_DEVICES`。可使用 `SC3000_PYTHON` 指定 Python；默认复用已准备的 `~/sc4001-venv/bin/python`，不会修改该环境或 SC4001 的作业文件。提交前需确认当前账号的 partition、QoS 和资源配额仍适用，并创建 `outputs/slurm/` 日志目录。

## 教师 starter 来源

- [NanoGPT-Math 教师仓库](https://github.com/zhouyuan888888/NanoGPT-Math)
- 本地准备时锁定提交：`7e96102c0459e0b3d92a7cbd2a75526ad6754a30`。

教师材料、学生实现与辅助诊断保持区分；具体作业要求以课程发布的正式文件为准。
