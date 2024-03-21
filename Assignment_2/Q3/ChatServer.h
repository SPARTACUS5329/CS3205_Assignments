#pragma once
#include <pthread.h>
#define MAX_USERS 5
#define MAX_MESSAGE_LENGTH 100
#define MAX_TIMEOUT 10

typedef struct user {
	char name[MAX_MESSAGE_LENGTH];
	int id;
	int sockfd;
	pthread_t thread;
} user_t;


typedef struct message {
	char text[MAX_MESSAGE_LENGTH];
	user_t sender;
} message_t;

typedef struct thread_args {
	int id;
	int sockfd;
} thread_args_t;

void removeUser(int id);
char *listUsers(int id); 
void *userThread(void *args);
