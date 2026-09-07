# Implementation Notes

## 1. 修改面

| 文件 | 操作 | 作用 |
| --- | --- | --- |
| `user/user.h` | 修改 | 声明 `getproccount()` user API |
| `user/usys.pl` | 修改 | 生成 `getproccount` assembly stub |
| `kernel/syscall.h` | 修改 | 分配唯一的 system-call number |
| `kernel/syscall.c` | 修改 | 声明 `sys_getproccount()` 并加入 dispatch table |
| `kernel/sysproc.c` | 修改 | 实现 kernel-side wrapper（内核侧包装函数） |
| `kernel/defs.h` | 修改 | 声明 kernel helper（内核辅助函数） |
| `kernel/proc.c` | 修改 | 遍历 process table（进程表）并统计非 `UNUSED` entries（表项） |
| `user/proccount.c` | 新建 | 调用 system call 并打印结果 |
| `user/two_pipes.c` | 新建 | 使用两条 pipe 完成 parent/child 双向通信 |
| `Makefile` | 修改 | 把 `_pingpong`、`_proccount`、`_two_pipes` 加入 `UPROGS` |

`user/usys.S` 是 build-time generated file（构建时生成文件），只检查、不直接编辑。

## 2. `getproccount()`

### Contract（接口约定）

- 输入：无。
- 输出：调用瞬间处于非 `UNUSED` state（状态）的 process-table entries 数量。
- 注意：结果是 snapshot（快照），会随进程创建、退出和 scheduler timing（调度时机）变化。

### 核心逻辑

```text
count = 0
for each process-table entry p:
    acquire p.lock
    if p.state is not UNUSED:
        count += 1
    release p.lock
return count
```

读取 `p->state` 时需要持有对应 `p->lock`，否则其他 CPU 可能同时改变该 entry，产生 data race（数据竞争）或不一致快照。逐项加锁保证单个 entry 的读取安全，但并不冻结整个 process table，因此它仍不是一个全局同一时刻的绝对快照。

### 运行结果解释

`proccount` 输出 3，而随后 `Ctrl-P` 显示 2，并不矛盾：执行 system call 时，`proccount` 自己也占一个 process-table entry；命令结束后再触发 `Ctrl-P`，该进程可能已退出并被回收。

## 3. Two-pipe IPC（双管道进程间通信）

一条 xv6 pipe 是 unidirectional（单向）的。要实现 parent 发 `ping`、child 回 `pong`，需要两条 pipe：

| Process | 保留 | 关闭 |
| --- | --- | --- |
| Parent | `p2c[1]` 写端、`c2p[0]` 读端 | `p2c[0]`、`c2p[1]` |
| Child | `p2c[0]` 读端、`c2p[1]` 写端 | `p2c[1]`、`c2p[0]` |

顺序为：

```text
parent writes "ping"
  -> child reads and prints
  -> child writes "pong"
  -> parent reads and prints
  -> parent waits for child
```

关闭 unused endpoints（未使用端点）既能减少 descriptor leak（描述符泄漏），也决定 pipe 的 EOF/error semantics（文件结束/错误语义）：所有写端关闭后，reader 才能观察 EOF；所有读端关闭后，xv6 的 `write()` 会返回 `-1`。

## 4. 验证记录

| 检查 | 结果 |
| --- | --- |
| `make qemu` | 正常启动 xv6 shell |
| `forktest` | `fork test OK` |
| `usertests` | `ALL TESTS PASSED` |
| `pingpong` | 交替收到 `ping` / `pong` |
| Zombie experiment | 可观察 sleeping parent 与 zombie child；父进程退出后二者消失 |
| `proccount` | 输出 3；与随后 2-process `Ctrl-P` 快照的差异可解释 |
| `two_pipes` | child PID 4 收到 `ping`；parent PID 3 收到 `pong` |

## 5. 本次遇到的错误

- 在 xv6 shell 中运行 `cd ..`、`ls` 会出现 `exec ... failed`；这些是 host utilities（宿主工具），应先退出 QEMU 再运行。
- `pingpong` 出现 `exec pingpong failed`，原因是程序尚未加入 `UPROGS`，没有被编译并放入 `fs.img`。
- `UPROGS not found` 来自把 `Makefile` 写成小写；Linux filename（文件名）区分大小写。
- shell 出现续行提示符 `>`，原因是输入了未闭合的单引号；使用 `Ctrl-C` 取消当前命令。
- `main(int argc, char *argc[])` 把两个参数都命名为 `argc`，导致 conflicting types（类型冲突）；第二个参数应命名为 `argv`。
- 新增 system call 时，API declaration、stub、number、dispatch entry 与 handler 任一处遗漏或命名不一致，都会造成 compile、link 或 runtime failure（编译、链接或运行失败）。

## 6. 未执行项

Lab manual 中通过提前关闭 pipe endpoint 来观察 blocked `read()` 被唤醒的扩展实验未在本次课内执行。因此这里只记录其预期语义，不把预期输出写成已验证结果。
