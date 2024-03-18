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
#include "./MusicServer.h"

static user_t users[MAX_USERS];
static int userCount = 0;
volatile sig_atomic_t terminate = 0;

void error(const char *msg) {
	perror(msg);
	exit(1);
}

void* userThread(void *args) {
	int newSocket = *((int *) args);
	user_t *user = &users[userCount - 1];
	user->id = newSocket;
	if (read(user->sockfd, &user->request, sizeof(char)) < 0) error("[userThread] Error in reading request");
	printf("Request: %c\n", user->request);
	close(user->sockfd);
	pthread_exit(NULL);
	return NULL;
}

void sigint_handler(int sig) {
	if (sig == 2) terminate = 1;
    exit(EXIT_SUCCESS);
}

int main() {
	if (signal(SIGINT, sigint_handler) == SIG_ERR) error("signal");

	int sockfd, newSockfd;

	struct sockaddr_in servAddr;
	struct sockaddr_storage cliAddr;
	socklen_t cliLen;

	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0) error("Error in opening socket");
	bzero((char *) &servAddr, sizeof(servAddr));

	servAddr.sin_family = AF_INET;
	servAddr.sin_addr.s_addr = INADDR_ANY;
	servAddr.sin_port = htons(PORT); // host to network short

	if (bind(sockfd, (struct sockaddr*) &servAddr, sizeof(servAddr)) < 0) error("Binding failed");

	if (listen(sockfd, 5) == 0) printf("Listening to PORT %d\n", PORT);
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
