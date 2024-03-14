#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include "./ChatServer.h"

char clientMessage[2000];
user_t users[MAX_USERS];
char buffer[1024];

void error(const char *msg) {
	perror(msg);
	exit(1);
}

void* userThread(void *args) {
	int newSocket = *((int *) args);	

 	do {
 		bzero(buffer, 255);
 		if (read(newSocket, buffer, 255) < 0) {
 			error("Error in reading");
 		}
 
 		printf("Client: %s\n", buffer);
 		bzero(buffer, 255);
 		fgets(buffer, 255, stdin);
 
// 		if (write(newSocket, buffer, strlen(buffer)) < 0) error("Error in writing");
 	} while (strncmp("Bye", buffer, 3));
 
	send(newSocket, buffer, 13, 0);
	printf("Exit userThread \n");
	close(newSocket);
	pthread_exit(NULL);
	return NULL;
}

int main(int argc, char *argv[]) {
	if (argc < 2) error("Not enough input arguments\n");
	
	int sockfd, newSockfd, portno;
	char buffer[255];

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
	
	pthread_t userThreads[MAX_USERS];
	int i = 0;

	while (1) {
		cliLen = sizeof(cliAddr);
		newSockfd = accept(sockfd, (struct sockaddr*) &cliAddr, &cliLen);
		if (pthread_create(&userThreads[i++], NULL, userThread, &newSockfd) != 0) error("[Thread creation]\n");
		if (i >= MAX_USERS) {
			i = 0;
			while (i < MAX_USERS) {
				pthread_join(userThreads[i++], NULL);
			}
			i = 0;
		}
	}

	close(sockfd);
	return 0;
}
