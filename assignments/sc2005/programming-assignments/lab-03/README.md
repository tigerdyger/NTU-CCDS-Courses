# SC2005-LAB03 — Synchronization and Semaphores

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 课程 | SC2005 Operating Systems |
| 类型 | xv6 synchronization（同步）、semaphore（信号量）与 bounded buffer（有界缓冲区） |
| 实验日期 | 2026-10-12，Week 9 |
| 环境 | 课程 xv6 `lab3` 分支、RISC-V、QEMU、实验室 Linux 虚拟机，`CPUS=3` |
| 状态 | 核心任务已完成；课堂综合测试通过；下载备份及关键源码已核对 |
| 相关讲义知识点 | `SC2005-L08-T04--T05`、`SC2005-L09-T01--T05`、`SC2005-L10-T01--T03` |

## 任务概述

本实验把 lecture 中的 mutual exclusion（互斥）和 producer–consumer（生产者–消费者）落实到多核 xv6。先阅读 spinlock（自旋锁）与 sleep/wakeup（睡眠与唤醒）的配合，再完成内核信号量，最后用它保护共享计数器和容量为 16 的环形缓冲区。

`fork()` 后普通用户内存各有副本；这里操作的是课程提供的共享内核对象。父子进程使用同一 semaphore ID，才能同步对这些对象的访问。

## 完成与验证

| 任务 | 结果及证据 |
| --- | --- |
| Part 1：阅读同步原语 | 核对 `kernel/spinlock.c` 的原子操作、关中断及内存屏障；追踪 `kernel/proc.c` 的锁交接与进程状态变化 |
| Part 2：内核信号量 | 完成 `sem_wait`、`sem_signal`、`sem_getvalue`；课堂 `sem_basic` 检查 1 → 0 → 1 并输出 PASS |
| Part 3：共享计数器 | 未保护版本的一次运行得到 1935，而非预期 2000；保护完整读改写后得到 2000，断言通过 |
| Part 4：生产者–消费者 | 两个生产者各写入 48 个字符，父进程消费 96 个字符；按 `empty/full/mutex` 同步后输出 PASS |
| 最终综合运行 | 三项测试在 `CPUS=3` 下依次运行，输出 `ALL TESTS PASSED` 并返回 xv6 shell |
| 本地备份核验 | gzip 与 tar 检查通过；对照已固定的官方源码快照，81 个受版本控制文件均存在，只有两个实验文件不同 |

运行结果来自课堂操作记录和截图。1935 是一次未同步运行的实际结果，不是每次必然出现的值。`sem_basic` 不覆盖阻塞等待；缓冲区测试只检查读出字符属于消息使用的字符集合，不能单凭 PASS 证明逐字符顺序、频次及所有并发交错均正确。此次本地整理没有重新启动 xv6，也不代表已经通过额外压力测试或 TA 签核。

## 文件说明

- [synchronization-trace.md](synchronization-trace.md)：Part 1 的源码阅读路线、原子操作与 lost wakeup（丢失唤醒）。
- [implementation-notes.md](implementation-notes.md)：Parts 2–4 的设计、同步顺序、结果解释和边界条件。
- [code/](code/)：课堂备份中的两个修改文件、上游许可证和复现说明。

## 构建与测试

本目录不是完整的 xv6 工程。先按 [代码复现说明](code/README.md) 准备独立课程 checkout，并将两个文件放到各自的 `kernel/` 和 `user/` 位置。Linux host shell（宿主终端）中运行：

```bash
make clean
make CPUS=3 qemu
```

进入 xv6 shell 后运行：

```text
race_test
```

当前保存的 `main()` 会依次执行三项测试。最终课堂输出的关键行是：

```text
[sem_basic] PASS: Basic semaphore operations work.
[race_test] final counter=2000 (expected 2000)
[race_test] PASS: consistent counter
[producer_consumer] PASS: message delivered
ALL TESTS PASSED
```

## 提交与公开范围

本次核对的 Lab 3 Manual 没有列出单独线上上传的文件清单、报告或截止时间；要求能够解释实现并展示检查证据。这里不据此推断 NTULearn 没有额外公告，也不记录未经确认的现场签核。

原始压缩包保留在仓库外的学习资料目录。公开目录只保留学习总结、两个已核对的修改文件及许可证，不上传整份 xv6、手册、截图、编译产物、学号或凭据。目录采用白名单忽略规则，后续新增文件须经检查后才能纳入版本控制。

## 来源

- SC2005, *Lab 3 Manual*, PDF pp. 1–10；Part 1 pp. 4–5，Part 2 pp. 6–7，Part 3 p. 8，Part 4 pp. 9–10。
- [课程 xv6 lab3 源码快照](https://github.com/CPS-research-group/ntu-sc2005-xv6/tree/269bf05bba7f92f667dd76af37aa8db22ce2f195)。该提交是整理时核对的比较基线；备份不含 `.git`，不能据此证明实验室 checkout 的提交记录。
- 2026-10-12 课堂运行截图及下载的 Lab 3 备份；原始材料不进入公开仓库。
