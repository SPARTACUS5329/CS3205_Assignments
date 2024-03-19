#pragma once
#include <pthread.h>
#define PORT 8800
#define MAX_BUFFER_SIZE 1000 
#define MAX_NAME_SIZE 20
#define MAX_USERS 5
#define BASE_DIR_PATH "./assets/"
#define MAX_REQUEST_SIZE 5

typedef struct user {
	int sockfd;
	int id;
	pthread_t thread;
	char name[MAX_NAME_SIZE];
	char request;
} user_t;

void *userThread(void *args);
