# NTU CCDS 课程笔记

本仓库整理六门南洋理工大学计算与数据科学学院课程的 LaTeX 笔记。仓库采用单仓库结构，每门课程独立编译为一份 PDF，并共享排版配置。

## 课程列表

| 课程代码 | 课程名称 | 源文件目录 |
| --- | --- | --- |
| SC2005 | 操作系统 | `courses/sc2005/` |
| SC2008 | 计算机网络 | `courses/sc2008/` |
| SC3000 | 人工智能 | `courses/sc3000/` |
| SC4001 | 神经网络与深度学习 | `courses/sc4001/` |
| SC4002 | 自然语言处理 | `courses/sc4002/` |
| SC4061 | 计算机视觉人工智能 | `courses/sc4061/` |

`SC4000` 对应机器学习，`SC4001` 对应神经网络与深度学习。

## 仓库结构

```text
.
├── assignments/                 # 独立的书面与编程作业
│   └── scxxxx/
│       ├── written-assignments/
│       │   └── main.tex         # 该课程的书面作业册
│       └── programming-assignments/
│           └── lab-xx/          # Lab、PA 或课程项目
├── courses/
│   └── scxxxx/
│       ├── main.tex             # 课程 PDF 编译入口
│       ├── course-map.tex       # 讲义与习题对应表
│       ├── lectures/            # 讲义笔记
│       └── exercises/
│           ├── lecture-examples/  # 讲义例题与解答
│           └── tutorials/       # 习题课
├── shared/preamble.tex          # 共享 LaTeX 配置
└── templates/                   # 内容模板
```

讲义与习题分别存放，但编译进同一门课程的 PDF。相关内容通过稳定编号关联：

| 内容类型 | 编号示例 |
| --- | --- |
| 一次课 | `SC2005-L03` |
| 讲义知识点 | `SC2005-L03-T02` |
| 讲义例题 | `SC2005-L03-E01` |
| 习题课题目 | `SC2005-TUT02-Q04` |
| 手写作业题目 | `SC2005-HW01-Q03` |
| 编程作业 | `SC2005-LAB01` |

## 编译

编译需要安装包含 `latexmk` 和 XeLaTeX 的 TeX Live 或 MacTeX。

```bash
make sc2005       # 编译一门课程
make sc2005-written  # 编译该课程的书面作业册
make assignments  # 编译六门书面作业册
make all          # 编译全部课程
```

课程笔记生成在 `build/<course-code>/`，书面作业册生成在
`build/assignments/<course-code>/`；两者均不纳入 Git。

## 内容规范

仓库只收录原创讲解、推导和图表，不收录课程课件、录像、学习平台导出、答案册、凭据或其他受限材料。尚未核实的内容使用 `\verify{...}` 标记。
