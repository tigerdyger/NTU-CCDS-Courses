# SC2008-LAB04 Analyzing Network Data Log

Lab 4 使用 Python 分析采样网络日志，统计主机、协议、目的端口和通信对，并按采样率估计监测期间的 IP 流量。本目录保留实验任务和复习要点。

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 课程 | SC2008 Computer Networks |
| 实验日期 | 2026-10-14，Week 9 |
| 环境 | 个人电脑、Python 3；绘图使用 Matplotlib 与 SciencePlots |
| 状态 | Exercise 4A–4F 已完成并核对 |
| 实验安排 | Lab 4 跨两个 session，使用同一份答案模板 |

## 任务与完成情况

| 任务 | 完成内容 |
| --- | --- |
| 4A 主机统计 | 分别统计源地址与目的地址的采样包数，列出前五名，并查询地址注册机构 |
| 4B 协议占比 | 筛选 IP 记录，统计 TCP、UDP 及其他 IP 协议，统一百分比的分母 |
| 4C 应用协议 | 统计 TCP/UDP 目的端口并查询注册服务名称 |
| 4D 流量估计 | 累加 IP packet size，按题目指定的采样率估计 15 秒内的流量，标明 MB 单位 |
| 4E 附加分析 | 分析有方向的源地址与目的地址组合，以一页表格、横向条形图和结论呈现 |
| 4F Python 代码 | 整理读取、统计和可选绘图入口，保留完整可运行脚本 |

详细方法见 [流量分析笔记](traffic-analysis-notes.md)。

## 本地文件与复现

正式分析使用 `Data_2.csv`；练习数据只用于熟悉格式，不替代评分数据。原始文件保存在仓库外的 SC2008 学习资料目录。

本地 `submission/` 保存最终三页报告和 `analyze_lab4.py`，`tests-local/` 保存构建脚本、核对记录、绘图依赖和预览。这两个目录均被 Git 忽略，克隆远程仓库不会取得其中内容。学习资料目录另存有最终 answer 副本。

持有本地脚本和课程数据时，可运行：

```bash
python3 submission/analyze_lab4.py /path/to/Data_2.csv
```

数值统计只依赖 Python 标准库。添加 `--figure /path/to/top_pairs.png` 可生成图表，需要 Matplotlib 和 SciencePlots；本次使用 SciencePlots 2.2.2 的 `science` 与 `no-latex` 样式。

## 核对情况

- 脚本已在正式数据上运行，报告中的计数、比例和流量估计与输出一致。
- 图表调整前后的数值输出一致；数据处理逻辑未因更换样式而改变。
- 最终报告三页均已检查，4E 附加分析单独占一页。
- 学习资料中的 answer 副本与本地提交版的 SHA-256 一致。

## 提交与公开范围

本次 TA 补充要求上传一份 DOCX/PDF 报告，并将 Python 源码复制为文本；提交界面提供 Text 栏。因此本地最终报告保留答案和图表，代码用于粘贴到 Text 栏。提交状态与文件校验值仅保存在本地。

远程仓库保留本页、流量分析笔记和白名单忽略规则。官方手册、答案模板、已填报告、完整解题代码、原始 CSV、实际地址排名、图表结果和个人信息不进入此次提交。

## 来源

- SC2008，*Lab 4 manual* 与 *Lab 4 answer template*，Exercise 4A–4F。
- 本次课程提供的 `Data_2.csv`、练习数据及 2026-10-14 用户转述的提交说明；原始材料留在本地。
- [SciencePlots](https://github.com/garrettj403/SciencePlots)：本次图表使用的开源 Matplotlib 样式库。
