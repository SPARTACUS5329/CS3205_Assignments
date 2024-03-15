#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>

void error(const char *msg) {
	perror(msg);
	exit(1);
}

int main(int argc, char *argv[]) {
  if (argc < 3) error("Not enough input arguments\n");

	int sockfd, newsockfd, portno;
	struct sockaddr_in serv_addr;
  struct hostent *server;
	char buffer[255];

  portno = atoi(argv[2]);
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0) {
		error("Error in opening socket");
	}

  server = gethostbyname(argv[1]);
  if (server == NULL) {
    error("Error in connecting to server");
  }

  bzero((char *) &serv_addr, sizeof(serv_addr));
  serv_addr.sin_family = AF_INET;
  bcopy((char *) server->h_addr, (char *) &serv_addr.sin_addr.s_addr, server->h_length);
  serv_addr.sin_port = htons(portno); // host to network short
  if (connect(sockfd, (struct sockaddr*) &serv_addr, sizeof(serv_addr)) < 0) {
    error("Connection failed");
  }

  do {
    bzero(buffer, 255);
    fgets(buffer, 255, stdin);
    if (write(sockfd, buffer, strlen(buffer)) < 0) {
      error("Error in writing");
    }
    bzero(buffer, 255);
    if (read(sockfd, buffer, 255) < 0) {
        error("Error in reading");
    }
    printf("Server: %s\n", buffer);
  } while (strncmp("Bye", buffer, 3));

  close(sockfd);
	return 0;
}
