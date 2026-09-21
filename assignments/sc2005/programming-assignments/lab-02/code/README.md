# Lab 2 代码与复现

## 文件对应关系

| 本目录文件 | 放入课程 checkout 的位置 |
| --- | --- |
| [uthread.c](uthread.c) | `user/uthread.c` |
| [uthread_switch.S](uthread_switch.S) | `user/uthread_switch.S` |
| [scheduler-even-pid.c](scheduler-even-pid.c) | 只替换 `kernel/proc.c` 中的 `scheduler()`，不能覆盖整个 proc.c |

两个用户线程文件来自 2026-09-21 下载的实验室备份；除清理行尾空白外，内容保持一致。调度器文件是从独立保存的优先级版本提取的完整函数，同样仅清理行尾空白，不是可单独编译的翻译单元。未复制未修改的测试程序和整份内核源码。

上游代码许可见 [LICENSE](LICENSE)。本次核对使用课程仓库 `lab2` 提交 `a96181124bd890f840e1829d4c7a8a77515336fc`；许可证不替代课程的答案发布规则。

## 使用顺序

1. 准备独立的课程 `lab2` checkout，确认提交。先不应用本目录文件，用 `make clean`、`make CPUS=1 qemu` 运行原版 `uthread_test`、`schedtest` 和 `starvetest`，保存输出。
2. 备份原版 `scheduler()`，再只替换该函数。在 `CPUS=1` 下重新构建，比较两个调度测试。无限循环使用 Ctrl-A 后 X 退出。
3. 保留优先级函数及结果，恢复原版 `scheduler()`。不要以整体 reset 的方式丢弃其他实验修改。
4. 将本目录的两个用户线程文件分别放到上述对应位置。`Makefile` 与 `uthread_test.c` 沿用原版；不要把本目录直接当作完整 xv6 工程编译。
5. 先在 `CPUS=1` 下 clean build 并运行 `uthread_test`，再按手册在 `CPUS=3` 下 clean build 并复测。每次保留完整输出，而非仅截图尾部。

host shell（Linux 宿主终端）中的最终构建命令：

```bash
make clean
make CPUS=3 qemu
```

xv6 shell 中的测试命令：

```text
uthread_test
```

预期三个线程分别打印 0--99、各自 `exit after 100`，随后显示 `thread_schedule: no runnable threads` 并返回 shell。该最后提示是提供的测试结束路径，不是 panic。
