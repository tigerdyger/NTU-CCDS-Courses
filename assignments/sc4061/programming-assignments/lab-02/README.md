# SC4061 Lab 2

Image Segmentation and Depth Computation：文档图像分割与 SSD 立体匹配。实验、英文报告及配套代码已完成并核验；2026-10-18 经用户确认已提交，尚无评分结果。

## 文件边界

沿用 Lab 1 的默认忽略规则，只允许本说明、`.gitignore` 和 [`tools/check_environment.m`](tools/check_environment.m) 进入公开 Git。`work/`、`outputs/`、`report/`、`tests-local/`、`submission/` 及其他新增文件默认只留在本地。原始手册、图片与标注保留在学习资料目录，不复制到公开仓库。

本地代码与输出不会随公开仓库备份；最终提交材料已另存一份到学习资料目录，迁移电脑或清理目录前仍须另做私有备份。不能使用 `git add -f` 绕过规则，截止后也不自动公开答案。

## 环境与交付

沿用 MATLAB 与 Image Processing Toolbox，本次不需要 GPU。通用环境检查：

```matlab
addpath('tools');
environment = check_environment();
```

报告单独上传 PDF，不与其他文件一起压缩；代码可附在报告末尾或单独上传。本次提交为一份 PDF 和两份 MATLAB 源文件，本地副本保存在被忽略的 `submission/`；任务清单和核验记录位于 `work/LOCAL_PLAN.md`。提交状态依据用户确认，公开目录不包含报告或解题实现。
