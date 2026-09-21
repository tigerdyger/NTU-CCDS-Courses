# SC2005-LAB02 — Processes, Scheduling, and User Threads

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 课程 | SC2005 Operating Systems |
| 类型 | xv6 process（进程）、priority scheduling（优先级调度）与 cooperative user threads（协作式用户线程） |
| 实验日期 | 2026-09-21，Week 7 |
| 环境 | 课程 xv6 `lab2` branch（分支）、RISC-V、QEMU、实验室 Linux 虚拟机 |
| 状态 | 核心实现与课堂运行已完成；备份源码已核对；可选 GDB、FCFS 和额外回归测试未执行 |
| 相关讲义知识点 | `SC2005-L03-T02--T03`、`SC2005-L04-T01,T04--T05`、`SC2005-L06-T02` |

## 实验目标

1. 区分 process table（进程表）、saved kernel context（保存的内核上下文）、trapframe（陷阱帧）和 user address space（用户地址空间）。
2. 从 shell 的 `fork()` 追踪新子进程成为 `RUNNABLE`，第一次经 `swtch()` 进入 `forkret()`。
3. 理解 timer interrupt（时钟中断）如何经 `yield()`、`sched()` 返回调度器。
4. 实现 runnable even-PID（就绪偶数 PID）严格优先，并区分观察到的推迟与可能无限持续的 starvation（饥饿）。
5. 完成用户线程上下文、初始栈与汇编切换，在恢复原调度器后验证单核运行和三核复测。

## 完成与验证

| 任务 | 结果及证据 |
| --- | --- |
| 未修改的用户线程基线 | `uthread_test` 无输出，直接返回 xv6 shell |
| 原调度器的 `schedtest` | PID 5、6、7、8 各完成四轮，打印 `all children finished` |
| 原调度器的 `starvetest` | 快照分别观察到奇数 PID 11、偶数 PID 10 处于 `run` |
| 严格优先级的 `schedtest` | 此次打印顺序为偶数 PID 4、6 完成后，奇数 PID 5、7 才运行完成 |
| 严格优先级的 `starvetest` | 三次快照均为 PID 10 `run`、PID 9 `runble` |
| 调度器恢复 | 备份包中的工作 `kernel/proc.c` 与原始备份及核对过的官方版本逐字节一致；优先级版本另存 |
| 用户线程实现与复测 | 按 `CPUS=1` 和 `CPUS=3` 流程分别运行；两次结尾均显示三个线程各 `exit after 100`，随后返回 shell |
| 本地备份 | 下载的 Lab 2 压缩包通过 gzip 完整性检查；关键源码、测试文件与独立调度器版本齐全 |

PID 是本次运行的动态编号，不是固定测试答案。运行结论来自课堂命令执行记录和用户提供的截图；线程截图覆盖输出尾部，不能据此声称已逐行审计完整的 0--99 输出。备份中没有完整终端日志。本地整理执行了源码与文件一致性检查，没有重新运行 xv6。

## 文件说明

- [process-scheduling-trace.md](process-scheduling-trace.md)：进程状态、首次调度、时钟抢占和内核上下文的源码阅读路线。
- [implementation-notes.md](implementation-notes.md)：优先级策略、用户线程设计、实验结果解释与易错点。
- [code/](code/)：备份中的两个实际用户线程文件、优先级调度器函数，以及安装和复测说明。

## 复现入口

使用独立的课程 xv6 `lab2` checkout；本文核对的官方提交为：

`a96181124bd890f840e1829d4c7a8a77515336fc`

先按 [code/README.md](code/README.md) 区分原版基线、优先级实验和线程实现，不能在最终线程版本上声称重新运行了“未修改基线”。

优先级实验必须在 `CPUS=1` 下比较；进入用户线程部分前恢复原版 `scheduler()`。最终在 Linux host shell（宿主终端）执行：

```bash
make clean
make CPUS=3 qemu
```

进入 xv6 shell 后执行 `uthread_test`。使用 Ctrl-A，松开后按 X 退出 QEMU。

## 提交与隐私

本次核对的 Lab 2 Manual 没有列出单独线上上传的文件、报告或截止时间；它要求保留 checkpoint evidence（检查证据），并能用自己的话解释源码与结果。末尾六问不要求另交书面答案。未核对 NTULearn 的额外公告或现场签核安排；如有，应另行遵守。

公开整理不包含学号、登录凭据、实验室地址、原始截图、完整课程源码副本或压缩包。原始备份保留在仓库外的学习资料目录。此目录中的代码仅为完成实验所需的有限文件与片段，保留上游许可；整理到本地不等于已获准公开提交，push 前仍应确认课程规则和发布范围。

## 来源

- SC2005, *Lab 2 Manual*, PDF pp. 1--14；核心 Parts 1--3 在 pp. 4--11，最终检查在 pp. 13--14；Part 4 为可选内容。
- [课程 xv6 lab2 源码快照](https://github.com/CPS-research-group/ntu-sc2005-xv6/tree/a96181124bd890f840e1829d4c7a8a77515336fc)。
- 2026-09-21 课堂运行截图及下载的 Lab 2 备份；截图与原始压缩包不进入公开仓库。
