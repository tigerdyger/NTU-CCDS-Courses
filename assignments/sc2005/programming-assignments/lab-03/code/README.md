# Lab 3 代码与复现

## 文件对应关系

| 本目录文件 | 放入课程 checkout 的位置 |
| --- | --- |
| [semaphore.c](semaphore.c) | `kernel/semaphore.c` |
| [race_test.c](race_test.c) | `user/race_test.c` |

两个文件来自 2026-10-12 下载的实验室备份，仅清理行尾空白并统一文件结束换行，未改变已测试的逻辑。保留了课程骨架原有的 TODO 提示，相关实现已写在其附近。本目录不是完整工程，不能直接运行 xv6 构建。

上游代码许可见 [LICENSE](LICENSE)。比较基线为课程仓库 `lab3` 的提交 `269bf05bba7f92f667dd76af37aa8db22ce2f195`。备份中的 81 个上游受版本控制文件全部存在，其中 79 个逐字节相同，仅上述两个文件不同。备份没有 `.git`，因此这是文件内容比较，不是对实验室提交历史的证明。

## 运行环境与使用顺序

需要 Linux 上的 RISC-V C 工具链、GNU make 和 `qemu-system-riscv64`，沿用实验室环境或课程提供的安装说明。所有测试使用 `CPUS=3`。

1. 在独立目录准备 [课程 lab3 checkout](https://github.com/CPS-research-group/ntu-sc2005-xv6/tree/269bf05bba7f92f667dd76af37aa8db22ce2f195)，固定到上述提交。不要覆盖仍在使用的其他 lab 工作目录。
2. 阅读原版 `kernel/spinlock.c`、`kernel/proc.c`、`kernel/ucnt.c`、`kernel/ubuf.c`，保留原文件和测试断言。原版信号量包含待完成逻辑，不能把它当成已经通过的基线。
3. 将本目录两个文件分别放到表中对应位置。其他源码和 Makefile 使用原版，尤其保留 `ubuf_read/write` 中的 `yield()`。
4. 在 Linux host shell（宿主终端）中重新构建并启动：

```bash
make clean
make CPUS=3 qemu
```

5. 进入 xv6 shell 后执行：

```text
race_test
```

本版本入口依次调用 `sem_basic()`、`race_test()` 和 `producer_consumer()`；预期关键输出见 [实验记录](../README.md#构建与测试)。Ctrl-A，松开后按 X 退出 QEMU。

若按手册逐部分排查，只在临时 checkout 的 `main()` 中启用目标测试调用，保留其余函数和断言；最后恢复三项调用并综合复测。未加锁的计数器是另一个实验阶段，不能用本目录最终同步版本的输出冒充原始失败基线。

## 验证范围

本目录保存课堂实际运行过的实现；整理时核对了备份完整性、与上游的改动范围及两个文件的内容一致性，并以 `clang --target=riscv64-unknown-elf -fsyntax-only` 配合上述课程快照的头文件通过语法检查。这不是完整的链接或 Linux/QEMU 运行。非预期提前退出后应重启 QEMU，再复测；`sem_free()` 不支持释放仍被其他进程使用的信号量。

许可证保留源代码的使用条件，不替代课程对答案发布范围的规定。原始手册、截图、完整源码快照和压缩包不随这些有限文件上传。
