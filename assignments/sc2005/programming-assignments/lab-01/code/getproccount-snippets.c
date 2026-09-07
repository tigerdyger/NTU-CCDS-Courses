/* Insert this helper into kernel/proc.c. This file is not standalone. */
int
getproccount(void)
{
  struct proc *p;
  int count = 0;

  for(p = proc; p < &proc[NPROC]; p++){
    acquire(&p->lock);
    if(p->state != UNUSED)
      count++;
    release(&p->lock);
  }

  return count;
}

/* Insert this system-call wrapper into kernel/sysproc.c. */
uint64
sys_getproccount(void)
{
  return getproccount();
}
