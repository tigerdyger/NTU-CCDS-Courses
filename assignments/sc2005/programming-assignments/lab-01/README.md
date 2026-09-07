# SC2005-LAB01 — Exploring xv6 and Adding a System Call

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 课程 | SC2005 Operating Systems |
| 类型 | xv6 system call（系统调用）与 pipe（管道）实验 |
| 实验日期 | 2026-09-07 |
| 环境 | 课程 xv6 仓库的 `lab1` branch（分支）、RISC-V、QEMU、实验室 Linux 主机 |
| 状态 | 核心任务已完成并在实验室环境运行核对；提前关闭 pipe endpoint（管道端点）的扩展实验未执行 |
| 相关讲义知识点 | `SC2005-L02-T05`、`SC2005-L03-T02`、`SC2005-L04-T01`--`SC2005-L04-T03` |

## 实验目标

1. 熟悉 host shell（宿主机命令行）与 xv6 shell（xv6 命令行）的边界，并完成 xv6 的编译、启动和测试。
2. 通过 `forktest`、`usertests`、`pingpong` 与 `zombie` 观察 process（进程）的创建、退出和状态变化。
3. 沿 `getpid()` 的完整调用路径理解 user API（用户接口）、trap（陷阱）、system-call dispatch（系统调用分派）和 kernel handler（内核处理函数）。
4. 新增 `getproccount()` system call，并正确同步 user/kernel declarations（用户态/内核态声明）、system-call number（系统调用号）与 dispatch table（分派表）。
5. 使用两条 unidirectional pipes（单向管道）实现 parent/child（父/子进程）双向通信。

## 完成与验证

| 任务 | 结果 | 主要证据 |
| --- | --- | --- |
| 环境与基线测试 | 通过 | `make qemu` 正常进入 xv6；`forktest` 输出 `fork test OK`；`usertests` 输出 `ALL TESTS PASSED` |
| `pingpong` 外部程序 | 通过 | 加入 `UPROGS` 后可由 xv6 shell 启动，并交替输出 `received ping` / `received pong` |
| Zombie process（僵尸进程）观察 | 通过 | 父进程 sleep 时可同时观察 sleeping parent 与 zombie child；父进程退出后两者消失；临时修改已恢复 |
| `getpid()` 调用路径 | 已核对 | 从 `user/user.h`、`user/usys.pl` 追踪至 trap、dispatch table 与 `sys_getpid()` |
| `getproccount()` | 通过 | 运行时输出 `process count: 3`；随后 `Ctrl-P` 快照显示 2 个进程，差异来自采样时刻及命令自身 |
| 双管道 IPC | 通过 | child PID 4 收到 `ping`，parent PID 3 收到 `pong`，方向和执行顺序正确 |

上述 PID 与 process count（进程数）只是一次运行的动态结果，不是固定答案。

## 文件说明

- [`getpid-trace.md`](getpid-trace.md)：`getpid()` 从 user space（用户空间）进入 kernel space（内核空间）再返回的调用链。
- [`implementation-notes.md`](implementation-notes.md)：`getproccount()` 与 two-pipe IPC（双管道进程间通信）的设计、验证和常见错误。
- [`code/`](code/)：本次新增的 user programs（用户程序）、kernel snippets（内核片段）与 system-call registration（系统调用注册项）。

## 复现入口

以下命令均在课程 xv6 仓库根目录的 host shell 中运行：

```text
git checkout lab1
make clean
make qemu
```

进入 xv6 shell 后运行 `forktest`、`usertests`、`pingpong`、`proccount` 或 `two_pipes`。退出 QEMU 使用 `Ctrl-A`，再按 `X`。

## 提交与隐私

现有 Lab 1 manual（实验手册）与 lab guidelines（实验说明）未列出需要单独上传的 Lab 1 deliverable（提交物）；本次代码主要用于课堂检查和后续 Lab Quiz 1 复习。若 NTULearn 后续公告另有要求，应以最新公告为准。

公开仓库不保存学号、登录凭据、实验室主机地址、终端截图、官方实验手册或课程仓库完整副本。`code/` 只保留本次实验新增的增量代码；这些文件依据实验过程重建，运行行为已经核对，但不是实验室远端 working tree（工作树）的逐字节快照。


## 来源

- SC2005, *Lab 1 Manual*, pp. 1--15（2026-09-07 本地核对）。
- SC2005, *Lab Guidelines*（2026-09-07 本地核对）。
- Russ Cox, Frans Kaashoek, Robert Morris, *xv6: a simple, Unix-like teaching operating system*, RISC-V rev. 3，相关部分：§§1.1--1.3、2.2、4.3、7.7。
