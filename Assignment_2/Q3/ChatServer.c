#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>

char clientMessage[2000];
char buffer[1024];
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

void error(const char *msg) {
	perror(msg);
	exit(1);
}

void* socketThread(void *args) {
	int newSocket = *((int *) args);	
//	recv(newSocket, clientMessage, 2000, 0);	

//	pthread_mutex_lock(&lock);
	char *message = malloc(sizeof(clientMessage) + 20);
	strcpy(message,"Hello Client : ");
	strcat(message, clientMessage);
	strcat(message, "\n");
	strcpy(buffer, message);
 
 	do {
 		bzero(buffer, 255);
 		if (read(newSocket, buffer, 255) < 0) {
 			error("Error in reading");
 		}
 
 		printf("Client: %s\n", buffer);
 		bzero(buffer, 255);
 		fgets(buffer, 255, stdin);
 
 		if (write(newSocket, buffer, strlen(buffer)) < 0) {
 			error("Error in writing");
 		}
 	} while (strncmp("Bye", buffer, 3));
 
	free(message);
//	pthread_mutex_unlock(&lock);
	sleep(1);
	send(newSocket, buffer, 13, 0);
	printf("Exit socketThread \n");
	close(newSocket);
	pthread_exit(NULL);
	return NULL;
}

int main(int argc, char *argv[]) {
	if (argc < 2) {
		error("Not enough input arguments\n");
	}
	
	int sockfd, newSockfd, portno;
	char buffer[255];

	struct sockaddr_in servAddr;
	struct sockaddr_storage cliAddr;
	socklen_t cliLen;

	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0) {
		error("Error in opening socket");
	}
	bzero((char *) &servAddr, sizeof(servAddr));
	portno = atoi(argv[1]);

	servAddr.sin_family = AF_INET;
	servAddr.sin_addr.s_addr = INADDR_ANY;
	servAddr.sin_port = htons(portno); // host to network short

	if (bind(sockfd, (struct sockaddr*) &servAddr, sizeof(servAddr)) < 0) {
		error("Binding failed");
	}

	if (listen(sockfd, 5) == 0) printf("Listening to PORT %d\n", portno);
	else error("[Error in listening]");
	
	pthread_t clientIDs[5];
	int i = 0;

	while (1) {
		cliLen = sizeof(cliAddr);
		newSockfd = accept(sockfd, (struct sockaddr*) &cliAddr, &cliLen);
		printf("Reaching\n");
		if (pthread_create(&clientIDs[i++], NULL, socketThread, &newSockfd) != 0) error("[Thread creation]\n");
		if (i >= 5) {
			i = 0;
			while (i < 5) {
				pthread_join(clientIDs[i++], NULL);
			}
			i = 0;
		}
	}

	close(sockfd);

	return 0;
}
