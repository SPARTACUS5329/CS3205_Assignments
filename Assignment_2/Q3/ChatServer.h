#pragma once
#include <pthread.h>
#define MAX_MESSAGE_LENGTH 100

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
	user_t *users;
} thread_args_t;

void removeUser(int id, user_t users[]);
char *listUsers(int id, user_t users[]); 
void *userThread(void *args);
