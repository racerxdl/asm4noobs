---
title: "[linux-riscv] Aceitando uma conexão TCP"
date: 2020-10-19T12:33:00-03:00
author: Lucas Teske
layout: page
permalink: /webserver/riscv/part2
tags:
  - riscv
  - risc-v
  - syscall
  - tcp
  - socket
---

Na [parte anterior](/webserver/riscv/part1) criamos funções reutilizáveis e aprendemos a gerenciar a stack manualmente no RISC-V. Agora vamos fazer nosso programa conversar pela rede!

### Syscalls de rede no RISC-V

As syscalls de socket no RISC-V são as mesmas do `asm-generic` (comuns a várias arquiteturas modernas):

| Syscall | ID RISC-V | O que faz |
|---------|-----------|-----------|
| `socket` | 198 | Cria um socket |
| `bind` | 200 | Associa a uma porta |
| `listen` | 201 | Modo escuta |
| `accept` | 202 | Aceita conexão |
| `setsockopt` | 208 | Configura opções |

A convenção de chamada é a mesma: número da syscall em `a7`, argumentos em `a0`-`a5`, retorno em `a0`.

### Estrutura sockaddr_in

Montamos a estrutura no `.data`:

```asm
.section .data

sockaddr_in:
    .hword 2            # sin_family = AF_INET (IPv4) — halfword = 2 bytes
    .hword 0x911F       # sin_port = htons(8081) — bytes invertidos
    .word 0             # sin_addr.s_addr = INADDR_ANY = 0.0.0.0 — word = 4 bytes
    .dword 0            # sin_zero — padding 8 bytes
```

> `.hword` = 2 bytes, `.word` = 4 bytes, `.dword` = 8 bytes no RISC-V 64. O mesmo conceito de network byte order do tutorial x86 se aplica: `8081 = 0x1F91` → armazenamos `0x911F` para ficar em big-endian na memória.

### Criando uma função `enviar` genérica

Vamos criar uma função que envia dados por qualquer fd. Diferente do x86, não faremos a contagem de strings dentro dela — receberemos o tamanho diretamente. Isso simplifica o código:

```asm
# enviar(fd, buffer, tamanho)
# a0 = fd, a1 = buffer, a2 = tamanho
enviar:
    li a7, 64           # syscall write
    ecall
    ret
```

Simples assim! Como os argumentos já estão em `a0`, `a1`, `a2` (que são exatamente o que `write` espera), nem precisamos mover registradores.

### Nosso programa completo

```asm
.section .text
.global _start

enviar:
    # a0=fd, a1=buffer, a2=tamanho
    li a7, 64
    ecall
    ret

_start:
    # 1. socket(AF_INET, SOCK_STREAM, 0)
    li a7, 198          # syscall socket
    li a0, 2            # AF_INET = IPv4
    li a1, 1            # SOCK_STREAM = TCP
    li a2, 0            # protocolo = 0
    ecall
    mv s0, a0           # s0 = socket fd

    # 2. bind(socket_fd, &addr, 16)
    li a7, 200          # syscall bind
    mv a0, s0           # socket fd
    la a1, sockaddr_in  # ponteiro da struct
    li a2, 16           # sizeof(sockaddr_in)
    ecall

    # 3. listen(socket_fd, 10)
    li a7, 201          # syscall listen
    mv a0, s0           # socket fd
    li a1, 10           # backlog
    ecall

    # 4. accept(socket_fd, NULL, NULL)
    li a7, 202          # syscall accept
    mv a0, s0           # socket fd
    li a1, 0            # addr = NULL
    li a2, 0            # addrlen = NULL
    ecall
    mv s1, a0           # s1 = fd do cliente

    # 5. Enviar mensagem ao cliente
    mv a0, s1           # fd do cliente
    la a1, mensagem     # buffer
    li a2, 22           # "Ola da baixaria TCP!\r\n" = 22 bytes
    call enviar

    # 6. Fechar cliente
    li a7, 57           # syscall close
    mv a0, s1           # fd do cliente
    ecall

    # 7. Fechar socket servidor
    li a7, 57           # syscall close
    mv a0, s0           # fd do servidor
    ecall

    # 8. Sair
    li a7, 93           # syscall exit
    li a0, 0
    ecall


.section .data

sockaddr_in:
    .hword 2            # AF_INET
    .hword 0x911F       # htons(8081)
    .word 0             # INADDR_ANY
    .dword 0            # sin_zero

mensagem:
    .ascii "Ola da baixaria TCP!\r\n"
    # CR (\r) = 0x0D, LF (\n) = 0x0A
```

> **Atenção ao `.ascii` vs NASM**: No GNU assembler você pode usar `\r` e `\n` diretamente! Bem mais conveniente que `0x0D, 0x0A`.

### Calculando o tamanho da mensagem

Assim como no x86, podemos usar subtração de labels para calcular o tamanho da mensagem automaticamente:

```asm
mensagem:
    .ascii "Ola da baixaria TCP!\r\n"
mensagem_fim:
```

E usar no código:

```asm
    la a1, mensagem        # ponteiro da mensagem
    la t0, mensagem_fim    # ponteiro para logo depois da mensagem
    sub a2, t0, a1         # tamanho = mensagem_fim - mensagem
```

No GNU assembler, um label também pode marcar o endereço logo depois de uma string. Subtraindo `mensagem` de `mensagem_fim`, temos o tamanho exato em bytes. Fazemos essa subtração em runtime porque os dois endereços são resolvidos pelo linker sem depender da ordem das seções no arquivo.

### Código final com tamanho automático

```asm
.section .text
.global _start

enviar:
    li a7, 64
    ecall
    ret

_start:
    # socket
    li a7, 198
    li a0, 2
    li a1, 1
    li a2, 0
    ecall
    mv s0, a0

    # bind
    li a7, 200
    mv a0, s0
    la a1, sockaddr_in
    li a2, 16
    ecall

    # listen
    li a7, 201
    mv a0, s0
    li a1, 10
    ecall

    # accept
    li a7, 202
    mv a0, s0
    li a1, 0
    li a2, 0
    ecall
    mv s1, a0

    # enviar
    mv a0, s1
    la a1, mensagem
    la t0, mensagem_fim
    sub a2, t0, a1
    call enviar

    # close(cliente)
    li a7, 57
    mv a0, s1
    ecall

    # close(servidor)
    li a7, 57
    mv a0, s0
    ecall

    # exit
    li a7, 93
    li a0, 0
    ecall


.section .data

sockaddr_in:
    .hword 2
    .hword 0x911F
    .word 0
    .dword 0

mensagem:
    .ascii "Ola da baixaria TCP!\r\n"
mensagem_fim:
```

### Testando

Compile, execute com QEMU e conecte com netcat:

```bash
make clean
make
# Executa em background com QEMU
qemu-riscv64 ./helloworld &
pid=$!
sleep 0.5

# Conecta com netcat
nc localhost 8081

# Deve imprimir: Ola da baixaria TCP!

kill $pid 2>/dev/null
```

> **Importante**: O QEMU em modo usuário faz bridge da rede para o host! As portas que você abrir no programa emulado estarão acessíveis no `localhost` da sua máquina.

Se você tem hardware RISC-V nativo, pode simplesmente executar `./helloworld` diretamente e testar com `nc localhost 8081` em outro terminal.

### Salvando o progresso

```bash
git add helloworld.S
git commit -am "Socket TCP funcionando no RISC-V! A baixaria agora eh multicore-friendly!"
```

### Conclusão da terceira parte

Já aceitamos conexões TCP no RISC-V! O fluxo é idêntico ao x86, mas com números de syscall diferentes e a sintaxe do GNU assembler. Aprendemos:

- Syscalls de rede no RISC-V (198-208)
- `.hword`, `.word`, `.dword` para estruturas de dados
- Cálculo de tamanho com `.` (ponto) do GNU assembler
- QEMU faz bridge de rede automaticamente

Na próxima parte: transformar isso em um servidor HTTP!

[Fazendo um servidor HTTP](/webserver/riscv/part3)
