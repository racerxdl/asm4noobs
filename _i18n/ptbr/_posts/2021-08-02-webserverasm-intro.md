---
title: "Introdução: Servidor web em assembly"
date: 2020-08-02T12:33:00-03:00
author: Lucas Teske
layout: page
permalink: /webserver/intro
description: Introdução de como fazer um servidor web em assembly
tags:
  - x86
  - arm
  - apple
  - webserver
  - html
  - intel
  - amd
---

O objetivo deste tutorial é dar uma abordagem mais prática à programação em assembly. Os dois melhores jeitos de se aprender assembly é por engenharia reversa ou programando algo. Aqui iremos fazer um servidor web totalmente em assembly que irá rodar como um aplicativo normal em seu sistema operacional. A ideia é criar um programa totalmente em assembly próximo ao equivalente em C no final desta página. Como a linguagem assembly é totalmente dependende de arquitetura e as chamadas de sistema dependem do sistema operacional, algumas alternativas de tutoriais estarão aqui dispostas.

* Windows (x86) **TODO**
* Linux (x86) **TODO**
* Linux (ARM64) **TODO**
* Linux (RISC-V) **TODO**
* MacOSX (x86) **TODO**
* MacOSX (ARM64) **TODO**


```c
// Servidor Web usado como exemplo alternativo em C
#include <unistd.h>
#include <stdio.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <string.h>

char *response = "<html>\
<head><title>Hello World</title></head>\
<body bgcolor=\"white\">\
<center><h1>This is a hello world!</h1></center>\
<hr><center>nginx/1.10.3 (Ubuntu) [ Just kidding ]</center>\
</body>\
</html>";

void sendHeader(int new_socket, int status_code, int content_length) {
  char buffer[1024];

  sprintf(buffer, "HTTP/1.1 %d\r\n", status_code);
  send(new_socket, buffer, strlen(buffer), 0);
  sprintf(buffer, "Content-Type: text/html\r\n");
  send(new_socket, buffer, strlen(buffer), 0);
  sprintf(buffer, "Connection: close\r\n");
  send(new_socket, buffer, strlen(buffer), 0);
  sprintf(buffer, "Content-Length: %d\r\n", content_length);
  send(new_socket, buffer, strlen(buffer), 0);

  sprintf(buffer, "\r\n");
  send(new_socket, buffer, strlen(buffer), 0);
}

void parseRequest(int new_socket) {
    char buffer[10240];
    int valread = read(new_socket, buffer, 10240);
    printf("%s\n", buffer );

    sendHeader(new_socket, 200, strlen(response));
    send(new_socket, response , strlen(response), 0 );

    printf("Response sent\n");
}

int main(int argc, char const *argv[]) {
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    int server_fd, new_socket;
    int opt = 1;

    printf("ADDRLEN: %d\n", addrlen);

    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // Forcefully attaching socket to the port 8081
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    printf("SOCKANDO: %d %d\n", SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT);

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons( 8081 );

    printf("PORTA INVERSA: %d\n", address.sin_port);

    // Forcefully attaching socket to the port 8081
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address))<0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
    if (listen(server_fd, 3) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }
    if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen))<0) {
        perror("accept");
        exit(EXIT_FAILURE);
    }
    parseRequest(new_socket);
    return 0;
}
```