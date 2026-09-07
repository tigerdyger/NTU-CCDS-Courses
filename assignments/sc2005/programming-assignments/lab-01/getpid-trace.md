# `getpid()` System-call Trace

本页记录 `getpid()` 如何从 user space（用户空间）进入 kernel space（内核空间）并返回。行号来自 2026-09-07 检查的课程 xv6 `lab1` branch；仓库更新后行号可能变化，应以 symbol name（符号名）为准。

## 调用链

| 顺序 | 文件与位置 | 作用 |
| --- | --- | --- |
| 1 | `user/user.h:21` | 声明 user API：`int getpid(void);` |
| 2 | `user/usys.pl:9--15,35` | `entry("getpid")` 生成 assembly stub（汇编桩代码） |
| 3 | `Makefile:107--111` | 由 `user/usys.pl` 生成 `user/usys.S`；后者是 generated file（生成文件），不应手改 |
| 4 | 生成的 `getpid` stub | 把 system-call number 放进 register `a7`，再执行 `ecall` |
| 5 | `kernel/trampoline.S:22` | `uservec` 保存 user registers（用户寄存器）并转入 kernel trap path（内核陷阱路径） |
| 6 | `kernel/trap.c:53--67` | `usertrap()` 识别来自 user mode（用户态）的 `ecall`，推进 `epc` 并调用 `syscall()` |
| 7 | `kernel/syscall.h:12` | 定义 `SYS_getpid` 的 system-call number |
| 8 | `kernel/syscall.c:93,118,137--141` | 声明 handler、在 dispatch table 中建立映射，并从 `a7` 读取编号 |
| 9 | `kernel/sysproc.c:19--21` | `sys_getpid()` 返回 `myproc()->pid` |
| 10 | `kernel/syscall.c:141` | 把返回值写入 trapframe（陷阱帧）的 `a0`，供 user program 读取 |

可以把整个过程压缩为：

```text
user program
  -> generated getpid stub
  -> a7 = SYS_getpid; ecall
  -> uservec / usertrap
  -> syscall dispatcher
  -> sys_getpid()
  -> a0 = return value
  -> user program
```

## 关键理解

- `a7` 携带 system-call number（系统调用号），告诉 kernel 要调用哪个 handler。
- `a0` 携带 return value（返回值）；有参数时，它也参与 RISC-V calling convention（调用约定）的参数传递。
- `myproc()` 返回当前 CPU 正在执行的 `struct proc`，所以 `myproc()->pid` 是调用者自己的 PID。
- `user/usys.S` 由 `user/usys.pl` 生成。新增 system call 时应修改 generator source（生成源）而不是生成结果，否则下一次 build（构建）会覆盖手工修改。

## 与 `getproccount()` 的对应关系

`getproccount()` 沿用相同骨架，只替换 API 名称、system-call number、dispatch entry（分派项）与 kernel implementation（内核实现）。因此新增 system call 的难点不是 `ecall` 本身，而是确保调用链每一层的名称和编号一致。
