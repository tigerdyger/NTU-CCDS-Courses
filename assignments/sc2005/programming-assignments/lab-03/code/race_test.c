#include "user.h"

#define T_ASSERT(cond) \
    do { \
        if (!(cond)) { \
            printf("Assertion failed at %s:%d: %s\n", __FILE__, __LINE__, #cond); \
            exit(1); \
        } \
    } while (0)


int N = 1000;

void sem_basic() {
    printf("[sem_basic] Initializing semaphore to 1...\n");
    int semid = sem_init(1);
    T_ASSERT(sem_getvalue(semid) == 1);

    printf("[sem_basic] Waiting (should decrement to 0)...\n");
    sem_wait(semid);
    T_ASSERT(sem_getvalue(semid) == 0);

    printf("[sem_basic] Posting (should increment to 1)...\n");
    sem_signal(semid);
    T_ASSERT(sem_getvalue(semid) == 1);

    sem_free(semid);
    printf("[sem_basic] PASS: Basic semaphore operations work.\n");
}

void do_work(int pid, int semid) {
    for (int i = 0; i < N; i++) {
        // TODO: increment a shared counter, making sure to use avoid race condition.
        // Tip: use a semaphore.
        T_ASSERT(sem_wait(semid) == 0);

        int val = ucnt_get(0);
        ucnt_set(0, val + 1);

        T_ASSERT(sem_signal(semid) == 0);
    }
}

void race_test() {
    ucnt_set(0, 0);
    int semid = sem_init(1); // TODO: create semaphore properly
    T_ASSERT(semid >= 0);

    int pid = fork();
    T_ASSERT(pid >= 0);
    if (pid == 0) { // child
        do_work(pid, semid);
        exit(0);
    } else { // parent
        do_work(getpid(), semid);
        wait(0);
        int final = ucnt_get(0);
        printf("[race_test] final counter=%d (expected %d)\n", final, 2*N);
        T_ASSERT(final == 2*N);
        printf("[race_test] PASS: consistent counter\n");
    }

    T_ASSERT(sem_free(semid) == 0);
}

struct buf_sem {
    // TODO: add semaphores as required
    int empty;
    int full;
    int mutex;
};

void consumer(struct buf_sem b, int loops, int valid[]) {
    char tmp;
    for(int i = 0; i < loops; i++) {
        // TODO: wait buffer slot full and signal empty slot
        T_ASSERT(sem_wait(b.full) == 0);
        T_ASSERT(sem_wait(b.mutex) == 0);

        tmp = ubuf_read();

        T_ASSERT(sem_signal(b.mutex) == 0);
        T_ASSERT(sem_signal(b.empty) == 0);

        T_ASSERT(valid[(unsigned char)tmp]);
    }
}

void producer(const char* msg, struct buf_sem b) {
    for (const char* p = msg; *p != '\0'; p++) {
        // TODO: wait buffer slot emtpy and signal used slot
        T_ASSERT(sem_wait(b.empty) == 0);
        T_ASSERT(sem_wait(b.mutex) == 0);

        ubuf_write(*p);

        T_ASSERT(sem_signal(b.mutex) == 0);
        T_ASSERT(sem_signal(b.full) == 0);
    }
}

void producer_consumer() {
    #define MSG_SIZE 48
    const char msg[MSG_SIZE + 1] = "cafefacefacefacefacefacefacefacefacecafecafecafe";
    const int NUM_PROD = 2;
    int valid[256] = {0};
    for (const char* p = msg; *p != '\0'; p++) {
        unsigned char uc = (unsigned char)*p;
        valid[uc] = 1;
    }

    struct buf_sem b;
    // TODO init semaphores as required
    b.empty = sem_init(UBUF_SIZE);
    T_ASSERT(b.empty >= 0);

    b.full = sem_init(0);
    T_ASSERT(b.full >= 0);

    b.mutex = sem_init(1);
    T_ASSERT(b.mutex >= 0);

    for (int i = 0; i < NUM_PROD; i++) {
        int pid = fork();
        T_ASSERT(pid >= 0);
        if (pid == 0) { // child
            producer(msg, b);
            exit(0);
        }
    }

    consumer(b, MSG_SIZE * NUM_PROD, valid);
    for (int i = 0; i < NUM_PROD; i++) {
        wait(0);
    }
    printf("[producer_consumer] PASS: message delivered\n");
    // TODO clean-up semaphores
    T_ASSERT(sem_free(b.empty) == 0);
    T_ASSERT(sem_free(b.full) == 0);
    T_ASSERT(sem_free(b.mutex) == 0);
}



int main() {
    sem_basic();

    race_test();

    producer_consumer();

    printf("ALL TESTS PASSED\n");

    exit(0);
}
