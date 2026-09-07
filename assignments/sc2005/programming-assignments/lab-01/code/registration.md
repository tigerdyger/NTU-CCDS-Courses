# `getproccount()` 注册项

这些片段应合并到课程 xv6 `lab1` branch 的对应位置，不能机械追加到文件末尾。

## `user/user.h`

```c
int getproccount(void);
```

## `user/usys.pl`

```perl
entry("getproccount");
```

## `kernel/syscall.h`

```c
#define SYS_getproccount 22
```

编号 `22` 适用于 2026-09-07 检查的 `lab1` branch；合并到其他版本前必须确认没有 number collision（编号冲突）。

## `kernel/syscall.c`

```c
extern uint64 sys_getproccount(void);
```

在 `syscalls[]` 中加入：

```c
[SYS_getproccount] sys_getproccount,
```

## `kernel/defs.h`

在 `// proc.c` declarations（声明）中加入：

```c
int getproccount(void);
```

## `Makefile`

在 `UPROGS` 中加入：

```make
$U/_pingpong\
$U/_proccount\
$U/_two_pipes\
```

每一项都必须位于 `UPROGS` continuation（续行）中；除最后一项外保留行末反斜杠。
