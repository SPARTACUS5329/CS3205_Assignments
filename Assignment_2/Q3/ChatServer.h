#pragma once
#include <pthread.h>
#define MAX_USERS 5
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

void *userThread(void *args);
