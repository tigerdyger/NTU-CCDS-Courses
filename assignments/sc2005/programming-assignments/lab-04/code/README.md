# Lab 4 代码与复现

## 源码基线与文件

[lab4.patch](lab4.patch) 是相对课程 [lab4 固定快照](https://github.com/CPS-research-group/ntu-sc2005-xv6/tree/8fc7997d972903622f802c1c5666852b93aee992) 的完整修改补丁。应用后保留原目录结构，无需手工拼接函数。上游许可见 [LICENSE](LICENSE)。

| 补丁修改的位置 | 用途 |
| --- | --- |
| `kernel/sysproc.c` | 页计数与惰性 `sbrk()` |
| `kernel/syscall.c`、`kernel/syscall.h`、`user/usys.pl` | 系统调用注册与用户入口 |
| `kernel/proc.h`、`kernel/proc.c`、`kernel/exec.c` | 记录、初始化和继承堆下界 |
| `kernel/trap.c` | 验证缺页原因、按需分配并重试 |
| `kernel/vm.c` | 回收时跳过未分配空洞 |
| `user/lazytest.c` | 移除本地计数占位函数，保留完整 30 页测试 |

原始备份包含该快照的全部 79 个受版本控制文件：69 个逐字节一致，上表 10 个文件不同。备份不含 `.git`，这只能确定文件内容的比较关系，不能证明实验室 checkout 的提交历史。

本地修正版与原始备份相比，仅将 `kernel/sysproc.c` 中 `sys_countpp()` 的定义返回类型由 `uint` 改为 `uint64`。`user/user.h` 的用户接口仍为 `int`；这里修正的是内核处理函数与 `syscall.c` 中 `uint64 (*)(void)` 调度表之间的类型不一致。补丁保留源文件原有空白；没有为美化格式扩大代码改动。

## 从干净 checkout 重建

以下命令中的 `/path/to/lab-04/code/` 要替换为本目录的实际绝对路径。使用独立目录，避免覆盖其他 lab：

```bash
git clone --branch lab4 https://github.com/CPS-research-group/ntu-sc2005-xv6.git xv6-lab4
cd xv6-lab4
git checkout --detach 8fc7997d972903622f802c1c5666852b93aee992
git apply --check /path/to/lab-04/code/lab4.patch
git apply /path/to/lab-04/code/lab4.patch
```

需要课程 Linux 环境中的 RISC-V GCC/binutils、GNU make 和 `qemu-system-riscv64`。在宿主终端运行：

```bash
make clean
make CPUS=3 qemu
```

然后在 xv6 shell 运行：

```text
fault read
fault write
lazytest
```

两种 `fault` 访问都应被终止，不能出现 `ERROR: access returned`；`lazytest` 预留后应为 `ΔVP=30, ΔPP=0`，触碰全部页面后应为 `ΔPP=30`。以同一次运行的差值为准，不要求所有编译环境的初始页数都等于 4。Ctrl-A，松开后按 X 退出 QEMU。

若复查部分触碰与回收，仅在临时副本把循环改为一次，保留 30 页预留量，检查 `ΔPP=1` 及正常退出；再在退出前检查 `sbrk(-size)` 的结果和页计数。原测试的“至少增加 30”条件不适用于这个临时版本，完成后恢复完整循环。

## 本地检查与证据边界

2026-10-26 在 Mac 上完成：原包 gzip 校验、全部基线文件比较、补丁可应用性检查，以及以下 RISC-V 目标语法检查。命令从已应用补丁的完整 checkout 执行：

```bash
clang --target=riscv64-unknown-elf -std=gnu11 -ffreestanding -fno-builtin \
  -Wall -Werror -Wno-gnu-designator -fsyntax-only -I. \
  kernel/sysproc.c kernel/trap.c kernel/proc.c kernel/exec.c \
  kernel/vm.c kernel/syscall.c user/lazytest.c user/fault.c
perl -c user/usys.pl
clang --target=riscv64-unknown-elf -std=gnu11 -ffreestanding -fno-builtin \
  -Wall -Werror -fsyntax-only -I. \
  /path/to/lab-04/code/tests/syscall-signatures.c
```

[syscall-signatures.c](tests/syscall-signatures.c) 用编译期断言检查计数处理函数的真实定义类型。对原始备份运行时，`sys_countpp` 断言失败；对修正版运行时通过。单独编译两个 C 文件通常不会发现跨文件声明不一致，所以保留这个小回归检查。

`-Wno-gnu-designator` 仅适配课程骨架中 `[SYS_x] handler` 的 GNU 初始化写法，没有屏蔽返回类型或格式字符串检查。`usys.pl` 语法检查通过，重新生成的系统调用入口与备份中的 `usys.S` 一致。

以上不是完整链接或 QEMU 执行。课堂截图属于修正前的运行，修正版仍需在具备课程工具链的环境中执行上述运行测试。惰性 `fork()`、未触碰页上的内核复制和自动栈增长不在本次实现范围内。

## 本地备份

仓库外的学习资料目录保留原始 `sc2005-lab4-20261026.tar.gz`，另存 `sc2005-lab4-20261026-corrected-source.tar.gz`。后者仅含修正后的 79 个源码、配置及许可文件，不携带旧二进制或文件系统镜像，使用前需要重新构建。完整工作副本位于被忽略的 `../xv6-local/`。

可提交范围仅为补丁、这个类型检查、许可和学习记录；原始手册、完整源码包、截图及编译产物保持本地。上游许可证不替代课程对答案发布范围的规定。
