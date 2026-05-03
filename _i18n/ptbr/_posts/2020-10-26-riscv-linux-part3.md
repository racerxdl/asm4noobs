---
title: "[linux-riscv] Fazendo um servidor HTTP"
date: 2020-10-26T12:33:00-03:00
author: Lucas Teske
layout: page
permalink: /webserver/riscv/part3
tags:
  - riscv
  - risc-v
  - syscall
  - tcp
  - http
  - webserver
---

Na [parte anterior](/webserver/riscv/part2) aceitamos uma conexão TCP. Agora vamos transformar nosso programa em um servidor HTTP que um navegador consegue acessar!

### Syscall read

Para receber a requisição HTTP do cliente, usamos a syscall `read` (63 no RISC-V):

- **a0** = fd
- **a1** = ponteiro do buffer
- **a2** = tamanho máximo
- Retorno em **a0** = bytes lidos

Criamos um buffer na seção `.bss` (dados não inicializados):

```asm
.section .bss

buffer:
    .space 4096         # reserva 4096 bytes (equivalente a resb 4096 do NASM)
```

### A resposta HTTP

A resposta HTTP é uma string com status line, headers e corpo HTML. Montamos tudo no `.rodata`:

```asm
.section .rodata

resposta_200:
    .ascii "HTTP/1.1 200 OK\r\n"
    .ascii "Content-Type: text/html\r\n"
    .ascii "Connection: close\r\n"
    .ascii "\r\n"
    .ascii "<html>\r\n"
    .ascii "<head><title>Baixaria RISC-V HTTP</title></head>\r\n"
    .ascii "<body bgcolor=\"black\">\r\n"
    .ascii "<center><h1 style=\"color: #00ff00\">Ola mundo da baixaria no RISC-V!</h1></center>\r\n"
    .ascii "<hr>\r\n"
    .ascii "<center style=\"color: #00ff00\">asm4noobs — servidor RISC-V em assembly puro!</center>\r\n"
    .ascii "</body>\r\n"
    .ascii "</html>\r\n"
resposta_200_fim:
```

> No GNU assembler, as diretivas `.ascii` consecutivas são concatenadas na memória, formando uma única string contínua — o mesmo efeito de múltiplos `db` no NASM.

Repare que removemos o `Content-Length` e usamos `Connection: close`. O navegador sabe que recebeu tudo quando a conexão fecha. Isso evita ter que calcular o tamanho do HTML manualmente.

Para enviar a resposta, calculamos o tamanho subtraindo labels:

```asm
    la a1, resposta_200
    la t0, resposta_200_fim
    sub a2, t0, a1         # tamanho = resposta_200_fim - resposta_200
```

Isso evita usar `li a2, resposta_200_len` antes do assembler conhecer o valor do símbolo.

### Roteamento: 200 ou 404

Precisamos verificar se a requisição começa com `GET / `. Como RISC-V não tem comparação direta de memória com constante, fazemos byte a byte:

```asm
    # Verificar se buffer começa com "GET / "
    lb t0, 0(a1)        # buffer[0] == 'G'?
    li t1, 'G'
    bne t0, t1, .erro_404

    lb t0, 1(a1)        # buffer[1] == 'E'?
    li t1, 'E'
    bne t0, t1, .erro_404

    lb t0, 2(a1)        # buffer[2] == 'T'?
    li t1, 'T'
    bne t0, t1, .erro_404

    lb t0, 4(a1)        # buffer[4] == '/'?
    li t1, '/'
    bne t0, t1, .erro_404

    lb t0, 5(a1)        # buffer[5] == ' '?
    li t1, ' '
    bne t0, t1, .erro_404

    # É um GET / válido!
```

> O RISC-V não tem a "mágica" do NASM com `cmp dword [buffer], "GET "`. A comparação é sempre registrador vs registrador (ou registrador vs imediato pequeno). Para strings, usamos load byte + comparação.

### Código completo

```asm
.section .text
.global _start

enviar:
    # a0=fd, a1=buffer, a2=tamanho
    li a7, 64
    ecall
    ret

# Para manter o exemplo pequeno, fazemos apenas uma syscall write.
# Em um servidor robusto, seria preciso repetir caso write envie só parte do buffer.

tratar_cliente:
    # a0 = fd do cliente
    addi sp, sp, -16
    sd ra, 8(sp)
    sd s0, 0(sp)

    mv s0, a0           # s0 = fd do cliente

    # read(fd, buffer, 4096)
    li a7, 63           # syscall read
    mv a0, s0
    la a1, buffer
    li a2, 4096
    ecall
    # Ignoramos o retorno (bytes lidos) — só precisamos do conteúdo no buffer

    # Verificar "GET / "
    la a1, buffer

    lb t0, 0(a1)
    li t1, 'G'
    bne t0, t1, .erro_404

    lb t0, 1(a1)
    li t1, 'E'
    bne t0, t1, .erro_404

    lb t0, 2(a1)
    li t1, 'T'
    bne t0, t1, .erro_404

    lb t0, 4(a1)
    li t1, '/'
    bne t0, t1, .erro_404

    lb t0, 5(a1)
    li t1, ' '
    bne t0, t1, .erro_404

.rota_ok:
    mv a0, s0
    la a1, resposta_200
    la t0, resposta_200_fim
    sub a2, t0, a1
    call enviar
    j .fim

.erro_404:
    mv a0, s0
    la a1, resposta_404
    la t0, resposta_404_fim
    sub a2, t0, a1
    call enviar

.fim:
    ld ra, 8(sp)
    ld s0, 0(sp)
    addi sp, sp, 16
    ret

_start:
    # 1. socket
    li a7, 198
    li a0, 2
    li a1, 1
    li a2, 0
    ecall
    mv s0, a0

    # 2. bind
    li a7, 200
    mv a0, s0
    la a1, sockaddr_in
    li a2, 16
    ecall

    # 3. listen
    li a7, 201
    mv a0, s0
    li a1, 10
    ecall

    # 4. accept
    li a7, 202
    mv a0, s0
    li a1, 0
    li a2, 0
    ecall
    mv s1, a0           # guarda fd do cliente

    # 5. Tratar requisição
    mv a0, s1           # argumento: fd do cliente
    call tratar_cliente

    # 6. Fechar cliente
    li a7, 57
    mv a0, s1
    ecall

    # 7. Fechar servidor
    li a7, 57
    mv a0, s0
    ecall

    # 8. exit
    li a7, 93
    li a0, 0
    ecall


.section .data

sockaddr_in:
    .hword 2
    .hword 0x911F
    .word 0
    .dword 0

.section .bss

buffer:
    .space 4096

.section .rodata

resposta_200:
    .ascii "HTTP/1.1 200 OK\r\n"
    .ascii "Content-Type: text/html\r\n"
    .ascii "Connection: close\r\n"
    .ascii "\r\n"
    .ascii "<html>\r\n"
    .ascii "<head><title>Baixaria RISC-V HTTP</title></head>\r\n"
    .ascii "<body bgcolor=\"black\">\r\n"
    .ascii "<center><h1 style=\"color: #00ff00\">Ola mundo da baixaria no RISC-V!</h1></center>\r\n"
    .ascii "<hr>\r\n"
    .ascii "<center style=\"color: #00ff00\">asm4noobs — servidor RISC-V em assembly puro!</center>\r\n"
    .ascii "</body>\r\n"
    .ascii "</html>\r\n"
resposta_200_fim:

resposta_404:
    .ascii "HTTP/1.1 404 Not Found\r\n"
    .ascii "Content-Type: text/html\r\n"
    .ascii "Connection: close\r\n"
    .ascii "\r\n"
    .ascii "<html><head><title>404</title></head>\r\n"
    .ascii "<body bgcolor='black'><center>\r\n"
    .ascii "<h1 style='color: red'>404 — Nao achei a baixaria RISC-V!</h1>\r\n"
    .ascii "</center></body></html>\r\n"
resposta_404_fim:
```

### Testando

Compile e execute com QEMU:

```bash
make clean
make
qemu-riscv64 ./helloworld &

# Em outro terminal:
curl http://localhost:8081/
curl http://localhost:8081/invalido
```

Resposta 200:

```html
<html>
<head><title>Baixaria RISC-V HTTP</title></head>
<body bgcolor="black">
<center><h1 style="color: #00ff00">Ola mundo da baixaria no RISC-V!</h1></center>
<hr>
<center style="color: #00ff00">asm4noobs — servidor RISC-V em assembly puro!</center>
</body>
</html>
```

Resposta 404:

```html
<html><head><title>404</title></head>
<body bgcolor='black'><center>
<h1 style='color: red'>404 — Nao achei a baixaria RISC-V!</h1>
</center></body></html>
```

### Salvando o progresso

```bash
git add helloworld.S
git commit -am "Servidor HTTP RISC-V funcionando com rotas 200 e 404!"
```

### Conclusão da quarta parte

Temos um servidor HTTP funcional no RISC-V! Aprendemos:

- Syscall `read` (63) para receber dados do cliente
- `.space` para declarar buffers não inicializados (`.bss`)
- `.ascii` para strings com `\r\n` embutidos
- Comparação byte a byte para roteamento HTTP
- `Connection: close` para evitar calcular `Content-Length`

Na próxima e última parte: loop de conexões e toques finais!

[Conclusões do servidor RISC-V](/webserver/riscv/part4)
