# 仓库协作规范

本规范适用于维护课程笔记的贡献者和自动化工具。

## 仓库范围

- 六门课程统一保存在本仓库中，每门课程的笔记以 `courses/<course-code>/main.tex` 作为 PDF 编译入口。
- 每门课程的书面作业以 `assignments/<course-code>/written-assignments/main.tex` 作为独立 PDF 编译入口。
- 讲义、讲义例题、习题课、书面作业和编程作业必须存放在各自目录中。
- 共享 LaTeX 配置统一放在 `shared/preamble.tex`。
- 保留官方课程代码和课程名称。

## 来源与准确性

- 与课程相关的结论应以注明的讲义、录像、教学大纲或教材为依据。
- 每个讲义文件都要记录课堂编号、来源名称或版本、准确页码范围和核验状态。
- 补全的推导和外部背景必须明确标注，不得冒充教师原话或课件原文。
- 尚未确认的定义、假设、公式、复杂度、单位或解释使用 `\verify{...}` 标记。
- 以总结和解释为主，避免大段复制来源材料。

## 内容组织与交叉引用

- 讲义文件：`courses/<course>/lectures/NN-topic.tex`。
- 讲义例题：`courses/<course>/exercises/lecture-examples/NN-topic.tex`。
- 习题课文件：`courses/<course>/exercises/tutorials/tutorial-NN.tex`。
- 已核对的书面作业：`assignments/<course>/written-assignments/main.tex`。
- 编程作业：`assignments/<course>/programming-assignments/<assignment-id>/`。
- 稳定编号分别采用 `SCxxxx-LNN-TNN`、`SCxxxx-LNN-ENN`、`SCxxxx-TUTNN-QNN`、`SCxxxx-HWNN-QNN` 以及课程规定的实验或编程作业编号。
- 使用 `\lecturetopic`、`\exercisequestion`、`\relatedtopic` 和 `\relatedexercise` 建立 PDF 内部引用。
- 新增课程内容时同步更新 `course-map.tex` 和对应的 `index.tex`；新增作业时更新该课程的作业 README。

帮助理解概念的微型例子可以保留在讲义中；完整题目和完整解答应放入对应的习题目录。
已完成并核对的书面作业必须保留足以独立理解的题干、条件和必要选项，不能只记录答案字母。

## 受限材料

- 不得加入课程课件、录像、转写稿、学习平台导出、答案册、正式考试、成绩、学号、凭据或尚未完成并核对的受考核答案。
- 原始材料应保存在已被忽略的本地材料目录中。
- 图片必须为原创或具有适当许可，并记录来源。
- 不得加入 `build/` 或 LaTeX 中间文件。

## 验证要求

- 新内容从 `templates/` 中对应模板开始，并替换所有占位符。
- 优先使用共享命令和常用 LaTeX 宏包。
- 修改单门课程笔记后运行 `make <course-code>`；修改书面作业后运行 `make <course-code>-written`；修改共享配置后运行 `make all`。
- 编译成功只说明排版通过，不能证明内容正确。
