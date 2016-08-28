#include "thread_pool.h"

#define MAX_THREAD_NUMBER 5

void* _thread_pool_init_func(void* arg){
    struct thread_pool_s *tpool = (struct thread_pool_s*)arg;
    while(1){
        pthread_mutex_lock(&tpool->pmt);
        struct thread_pool_job_s *ptj = tpool->head->next;
        if(ptj != NULL){
            tpool->head->next = ptj->next;
            tpool->wait_num--;
            if(0 == tpool->wait_num){
                tpool->tail = tpool->head;
            }
        }
        pthread_mutex_unlock(&tpool->pmt);
        if(ptj != NULL){
            ptj->callback(ptj->arg);
            free(ptj);
        }
    }
}

int initThreadPool(struct thread_pool_s *pool){
    if(pool == NULL){
        return -1;
    }
    if(pthread_mutex_init(&pool->pmt,NULL)){
        return -2;
    }
    pool->pools = (pthread_t*)malloc(sizeof(pthread_t) * MAX_THREAD_NUMBER);
    if(pool->pools == NULL){
        goto error_init_tp;
    }
    pool->head = (struct thread_pool_job_s*)malloc(sizeof(struct thread_pool_job_s));
    if(pool->head == NULL){
        goto error_init_tp;
    }
    pool->tail = pool->head;
    pool->tail->next = NULL;
    for(int i = 0; i < MAX_THREAD_NUMBER; ++i){
        if(pthread_create(&pool->pools[i],NULL,_thread_pool_init_func,pool)){
            goto error_init_tp;
        }
    }
    pool->wait_num = 0;
    return 0;

error_init_tp:
    free(pool->pools);
    free(pool->head);
    return -6;
}

void addJobToThreadPool(struct thread_pool_s *pool,void (*callback)(void*),void* arg){
    if(pool == NULL || callback == NULL){
        return;
    }
    struct thread_pool_job_s *tjob = (struct thread_pool_job_s*)malloc(sizeof(struct thread_pool_job_s));
    if(tjob == NULL){
        return;
    }
    tjob->callback = callback;
    tjob->arg = arg;
    tjob->next = NULL;

    pthread_mutex_lock(&pool->pmt);
    pool->tail->next = tjob;
    pool->tail = tjob;
    pool->wait_num++;
    pthread_mutex_unlock(&pool->pmt);
}

int destroyThreadPool(struct thread_pool_s **pool){
    struct thread_pool_s *ppool = *pool;
    pthread_mutex_lock(&ppool->pmt);
    if(ppool->wait_num != 0){
        pthread_mutex_unlock(&ppool->pmt);
        return -1;
    }
    struct thread_pool_job_s *ptpj = ppool->head->next;
    while(ptpj){
        struct thread_pool_job_s *ptpj_t = ptpj;
        ptpj = ptpj->next;
        free(ptpj_t);
    }
    free(ppool->head);
    for(int i = 0; i < MAX_THREAD_NUMBER; ++i){
        pthread_cancel(ppool->pools[i]);
    }
    free(ppool->pools);
    free(ppool);
    pthread_mutex_unlock(&(*pool)->pmt);
    pthread_mutex_destroy(&(*pool)->pmt);
    *pool = NULL;
    return 0;
}
