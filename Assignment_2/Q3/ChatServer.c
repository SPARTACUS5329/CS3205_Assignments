#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/_types/_fd_def.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include <sys/time.h>
#include "./ChatServer.h"

static user_t users[MAX_USERS];
static int userCount = 0;
volatile sig_atomic_t terminate = 0;

void error(const char *msg) {
	perror(msg);
	exit(1);
}

void* userThread(void *args) {
	int newSocket = *((int *) args);
	char buffer[MAX_MESSAGE_LENGTH];
	char tempBuffer[MAX_MESSAGE_LENGTH];
	user_t *user = &users[userCount - 1];
	user->id = newSocket;
	char usersString[MAX_USERS * MAX_MESSAGE_LENGTH];
	strcpy(usersString, "Online users: \n"); 
	bool firstUser = true;
	for (int i = 0; i < MAX_USERS; i++) {
		if (!users[i].id || users[i].id == user->id) continue;
		firstUser = false;
		strcat(usersString, users[i].name);
		strcat(usersString, "\n");
	}
	if (firstUser) strcpy(usersString, "No online users\n");
	strcat(usersString, "Enter your username: ");	
	send(user->sockfd, usersString, strlen(usersString), 0);
 	if (read(newSocket, user->name, MAX_MESSAGE_LENGTH) < 0) error("Error in reading");
 	bzero(tempBuffer, MAX_MESSAGE_LENGTH);
	strcpy(tempBuffer, user->name);
	strcat(tempBuffer, " joined the chat\n");
	for (int i = 0; i < MAX_USERS; i++) {
		if (users[i].id == user->id) continue;
		send(users[i].sockfd, tempBuffer, MAX_MESSAGE_LENGTH, 0);
	}
 	bzero(tempBuffer, MAX_MESSAGE_LENGTH);
	fd_set readfs;
	FD_ZERO(&readfs);
	FD_SET(user->sockfd, &readfs);
	struct timeval timeout;
	timeout.tv_sec = MAX_TIMEOUT;
	timeout.tv_usec = 0;

 	do {
 		bzero(buffer, MAX_MESSAGE_LENGTH);
		strcpy(buffer, user->name); 
		strcat(buffer, ": "); 
		int retval = select(user->sockfd + 1, &readfs, NULL, NULL, &timeout);
		if (retval == -1) error("[userThread] Error in select");
		if (retval == 0) {
			printf("Timeout occurred for %s\n", user->name);
			send(user->sockfd, "Timeout occurred", 16, 0);
			goto close_user_socket;
		}

 		if (read(newSocket, tempBuffer, MAX_MESSAGE_LENGTH) < 0) error("Error in reading");
		strcat(buffer, tempBuffer);
		for (int i = 0; i < MAX_USERS; i++) {
			if (users[i].id == user->id) continue;
			send(users[i].sockfd, buffer, MAX_MESSAGE_LENGTH, 0);
		}
 	} while (strncmp("Bye", buffer, 3));
 
close_user_socket:
	close(user->sockfd);
	pthread_exit(NULL);
	return NULL;
}

void sigint_handler(int sig) {
	if (sig == 2) terminate = 1;
    exit(EXIT_SUCCESS);
}

int main(int argc, char *argv[]) {
	if (argc < 2) error("Not enough input arguments\n");
	if (signal(SIGINT, sigint_handler) == SIG_ERR) error("signal");

	int sockfd, newSockfd, portno;
	char buffer[MAX_MESSAGE_LENGTH];

	struct sockaddr_in servAddr;
	struct sockaddr_storage cliAddr;
	socklen_t cliLen;

	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0) error("Error in opening socket");
	bzero((char *) &servAddr, sizeof(servAddr));
	portno = atoi(argv[1]);

	servAddr.sin_family = AF_INET;
	servAddr.sin_addr.s_addr = INADDR_ANY;
	servAddr.sin_port = htons(portno); // host to network short

	if (bind(sockfd, (struct sockaddr*) &servAddr, sizeof(servAddr)) < 0) error("Binding failed");

	if (listen(sockfd, 5) == 0) printf("Listening to PORT %d\n", portno);
	else error("[Error in listening]");
	
	while (!terminate) {
		cliLen = sizeof(cliAddr);
		newSockfd = accept(sockfd, (struct sockaddr*) &cliAddr, &cliLen);
		if (newSockfd < 0) {
			printf("[client_connection] Error in accepting client connection\n");
			continue;
		}
		users[userCount].sockfd = newSockfd;
		users[userCount].id = newSockfd;
		if (pthread_create(&users[userCount++].thread, NULL, userThread, &newSockfd) != 0) error("[Thread creation]\n");
		if (userCount >= 5) {
			userCount = 0;
			while (userCount < 5) {
				pthread_join(users[userCount++].thread, NULL);
			}
			userCount = 0;
		}
	}

	close(sockfd);

	return 0;
}
