#include "kernel/types.h"
#include "user/user.h"

int
main(int argc, char *argv[])
{
  int p2c[2], c2p[2];
  int pid, n, status;
  char buf[5];

  if(pipe(p2c) < 0 || pipe(c2p) < 0){
    printf("pipe failed\n");
    exit(1);
  }

  pid = fork();
  if(pid < 0){
    printf("fork failed\n");
    exit(1);
  }

  if(pid == 0){
    close(p2c[1]);
    close(c2p[0]);

    n = read(p2c[0], buf, 4);
    if(n != 4)
      exit(1);
    buf[4] = 0;
    printf("%d: received %s\n", getpid(), buf);

    if(write(c2p[1], "pong", 4) != 4)
      exit(1);

    close(p2c[0]);
    close(c2p[1]);
    exit(0);
  }

  close(p2c[0]);
  close(c2p[1]);

  if(write(p2c[1], "ping", 4) != 4)
    exit(1);
  close(p2c[1]);

  n = read(c2p[0], buf, 4);
  if(n != 4)
    exit(1);
  buf[4] = 0;
  printf("%d: received %s\n", getpid(), buf);

  close(c2p[0]);

  if(wait(&status) < 0)
    exit(1);
  exit(status);
}
