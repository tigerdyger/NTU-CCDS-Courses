# Process and Scheduling Trace

本页对应 Lab 2 Manual 的 Parts 1--2。以下符号与行为已对照官方 `lab2` 提交 `a96181124bd890f840e1829d4c7a8a77515336fc` 核对；优先按函数名查找，不依赖修改后可能偏移的行号。

## 1. 四种不同的状态载体

| 对象 | 源码位置 | 保存什么、由谁使用 |
| --- | --- | --- |
| `struct proc` 与 `proc[]` | `kernel/proc.h`、`kernel/proc.c` | 每个进程的状态、PID、页表、内核栈及上下文等内核元数据 |
| `p->context` | `struct context` | 进程内核执行的 `ra`、`sp` 和 `s0--s11`，供切换后继续执行 |
| `c->context` | `struct cpu` | 每个 CPU 的调度器上下文；与进程上下文是两个保存位置 |
| `p->trapframe` | `struct trapframe` | 陷入内核时保存的用户寄存器及返回所需状态，另有内核入口信息 |
| user address space（用户地址空间） | `p->pagetable` 所描述的映射 | 用户代码、数据与栈等内存映射，不等同于保存寄存器的结构体 |

`procdump()` 在内核中运行，能够读取内核进程表；普通用户程序不能直接解引用 `proc[]`，根本原因是页表映射和访问权限边界，而不是用户程序“不知道变量名”。

## 2. 三个关键状态赋值

| 情境 | 函数 | 状态赋值 |
| --- | --- | --- |
| 子进程创建准备完成 | `kernel/proc.c: fork()` | `np->state = RUNNABLE` |
| 调度器选中就绪进程 | `scheduler()` | `p->state = RUNNING` |
| 当前进程让出 CPU | `yield()` | `p->state = RUNNABLE` |

`RUNNABLE` 表示可以被选择，不代表已经获得 CPU。实际切入进程还需要更新 `c->proc` 并执行 `swtch()`。进程还可能因等待或退出进入其他状态，本表只覆盖本实验要求的三种转换。

## 3. 从 shell 到新子进程第一次运行

以 `ls` 为例：

```text
user/sh.c: fork1() -> fork()
  -> kernel/proc.c: allocproc()
       初始化 context.ra = forkret
       初始化 context.sp = 内核栈顶
  -> fork(): 复制用户内存与 trapframe；设置 child a0 = 0
  -> child state = RUNNABLE
  -> scheduler(): state = RUNNING
  -> swtch(调度器上下文, 子进程上下文)
  -> forkret(): 释放交接过来的进程锁
  -> usertrapret(): 返回子进程的用户态
  -> shell 子进程看到 fork() 返回 0
  -> runcmd() / exec(): 装入并执行 ls
```

新进程没有真实的“上一次运行位置”，因此 `allocproc()` 构造第一次恢复使用的上下文。`kernel/swtch.S` 恢复 `ra` 和 `sp` 后执行 `ret`，于是进入 `forkret()`。不能把这个过程写成 `swtch()` 直接跳到 `ls`。

`fork()` 创建进程；`exec()` 替换现有进程的用户程序，不再次创建进程。子进程 trapframe 的 `a0=0` 决定它在用户态看到的 fork 返回值。

## 4. 一次时钟抢占与两个 swtch 调用点

`kernel/trap.c` 的 `usertrap()` 在识别到 timer interrupt（时钟中断）时调用 `yield()`；`kerneltrap()` 也有针对当前进程的时钟让出路径。

1. `yield()` 获取当前进程锁，将状态设为 `RUNNABLE`，调用 `sched()`。
2. `sched()` 执行 `swtch(&p->context, &mycpu()->context)`：保存进程的内核上下文，恢复 CPU 调度器。
3. 调度器从先前暂停的 `swtch()` 之后继续，清空 `c->proc`，按策略寻找下一进程。
4. `scheduler()` 执行 `swtch(&c->context, &p->context)`：保存调度器，恢复选中进程。
5. 对于被暂停后恢复的进程，执行从其原来 `sched()` 内的切换调用之后继续，再返回 `yield()` 和陷阱处理路径。首次运行的新子进程则走 `forkret()`。

调度器不一定立即重新选择刚才的进程。`sched()` 也服务于睡眠、退出等非时钟路径，不能把它等同于时钟中断处理函数。

### 锁与中断不变量

- 进入 `sched()` 时，必须持有当前进程锁，状态不能仍为 `RUNNING`，中断必须关闭，并满足只持有相应锁的约束。
- `p->lock` 跨上下文切换交接，不能随意在 `swtch()` 前释放。首次运行由 `forkret()` 释放，后续运行沿原控制流处理。
- 修改调度策略只改变“选谁”，不应破坏锁、状态、`c->proc` 或原有中断与空闲处理。
- 本版本原调度器每次切回后继续当前进程表扫描；不是每次都从表头重新开始。本次严格优先级实现则有意在每次调度返回后重新开始优先级判断。

## 5. Ctrl-P 不是完整调度轨迹

`kernel/console.c: consoleintr()` 在 Ctrl-P 分支调用 `kernel/proc.c: procdump()`。输出列依次为 PID、state（状态）、name（名称）：

- `run`：`RUNNING`；
- `runble`：`RUNNABLE`；
- `sleep`：`SLEEPING`。

`procdump()` 为调试便利不获取整套进程锁，输出是观察快照，不是全局原子快照，也没有记录两次按键之间的全部调度事件。因此，“三次都看到偶数运行”要结合策略与工作负载解释，不能仅靠有限快照证明无限饥饿。
