# SC3000 Lab 2 Introduction to Prolog

使用 SWI-Prolog 学习事实、规则、递归查询和执行追踪。代码、测试、trace 与报告保留在本地；本目录仅公开项目说明和忽略规则。

## 当前状态

实验、报告与提交包检查已完成。19 项本地回归测试通过，提交代码的规则顺序与循环依赖实验结果已与报告核对，三页 PDF 已逐页检查。邮件提交和回执详情记录在本地工作计划中。

公开仓库不包含完整可运行或可直接提交的作业副本。

## 本地目录

- `work/`：Prolog 程序与本地工作计划。
- `tests-local/`：不参与提交的回归测试。
- `outputs/`：实际查询输出和 trace。
- `report/`：报告源文件及本地构建产物。
- `submission/`：已核对的一份 PDF 报告与三个 Prolog 源文件。
- 本目录下的 ZIP：邮件附件，内容与 `submission/` 中的四个文件逐字节一致。

实验覆盖事实与规则、递归依赖、规则顺序和循环依赖。提交要求以课程讲义及最新公告为准。

## 运行环境

使用 [SWI-Prolog 官方稳定版](https://www.swi-prolog.org/download/stable)。macOS 应用包的命令行入口位于 `SWI-Prolog.app/Contents/MacOS/swipl`；无需修改系统 PATH 即可通过完整路径运行。
