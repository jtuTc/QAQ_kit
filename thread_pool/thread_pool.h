#include <pthread.h>
#include <stdlib.h>

#ifndef THREAD_POOL_H_INCLUDED
#define THREAD_POOL_H_INCLUDED


struct thread_pool_job_s{
    void (*callback)(void*);
    void *arg;
    struct thread_pool_job_s *next;
};

struct thread_pool_s{
    unsigned int wait_num;
    pthread_mutex_t pmt;
    pthread_t *pools;
    struct thread_pool_job_s *head;
    struct thread_pool_job_s *tail;
};

extern int initThreadPool(struct thread_pool_s *pool);

extern void addJobToThreadPool(struct thread_pool_s *pool,void (*callback)(void*),void* arg);

extern int destroyThreadPool(struct thread_pool_s**);

#endif // THREAD_POOL_H_INCLUDED
