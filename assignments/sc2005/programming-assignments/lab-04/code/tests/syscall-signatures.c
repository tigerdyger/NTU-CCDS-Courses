// Compile against the complete course checkout; this is not an xv6 user program.
#include "kernel/sysproc.c"

_Static_assert(
  __builtin_types_compatible_p(__typeof__(&sys_countvp), uint64 (*)(void)),
  "sys_countvp must match the uint64 syscall handler signature");

_Static_assert(
  __builtin_types_compatible_p(__typeof__(&sys_countpp), uint64 (*)(void)),
  "sys_countpp must match the uint64 syscall handler signature");
