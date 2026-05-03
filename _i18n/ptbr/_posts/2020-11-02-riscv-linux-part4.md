---
title: "[linux-riscv] Conclusões do servidor HTTP"
date: 2020-11-02T12:33:00-03:00
author: Lucas Teske
layout: page
permalink: /webserver/riscv/part4
tags:
  - riscv
  - risc-v
  - syscall
  - tcp
  - http
  - webserver
  - conclusao
---

Na [parte anterior](/webserver/riscv/part3) nosso servidor HTTP já responde com HTML e tem roteamento básico. Mas ele ainda atende apenas um cliente. Vamos resolver isso e dar os toques finais!

### Loop de conexões

A ideia é simples: depois de fechar o cliente, voltamos para o `accept`. No RISC-V, usamos labels locais e `j`:

```asm
.proximo_cliente:
    # accept(socket_fd, NULL, NULL)
    li a7, 202
    mv a0, s0
    li a1, 0
    li a2, 0
    ecall
    mv s1, a0       # salva fd do cliente

    # tratar_cliente(fd_do_cliente)
    mv a0, s1
    call tratar_cliente

    # close(cliente)
    li a7, 57
    mv a0, s1
    ecall

    j .proximo_cliente
```

### setsockopt com SO_REUSEADDR

Evita o erro "Address already in use" ao reiniciar o servidor. No RISC-V:

```asm
    # setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR, &opt, 4)
    li a7, 208          # syscall setsockopt
    mv a0, s0           # socket fd
    li a1, 1            # SOL_SOCKET
    li a2, 2            # SO_REUSEADDR
    la a3, reuse_opt    # &opt (valor 1)
    li a4, 4            # sizeof(opt)
    ecall
```

Precisamos adicionar na `.data`:

```asm
reuse_opt:
    .word 1             # SO_REUSEADDR ativado (4 bytes)
```

> **Syscalls com 6 argumentos no RISC-V**: a convenção é `a0` a `a5`. Para `setsockopt`, que precisa de 5 argumentos, usamos `a0`-`a4`. Se precisasse de 6, usaria `a0`-`a5`.

### Código final completo

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

    mv s0, a0

    # read(fd, buffer, 4096)
    li a7, 63
    mv a0, s0
    la a1, buffer
    li a2, 4096
    ecall

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
    mv s0, a0           # s0 = socket fd

    # 2. setsockopt (SO_REUSEADDR)
    li a7, 208
    mv a0, s0
    li a1, 1            # SOL_SOCKET
    li a2, 2            # SO_REUSEADDR
    la a3, reuse_opt
    li a4, 4            # sizeof(int)
    ecall

    # 3. bind
    li a7, 200
    mv a0, s0
    la a1, sockaddr_in
    li a2, 16
    ecall

    # 4. listen
    li a7, 201
    mv a0, s0
    li a1, 10
    ecall

    # 5. Loop principal
.proximo_cliente:
    li a7, 202
    mv a0, s0
    li a1, 0
    li a2, 0
    ecall
    mv s1, a0           # guarda fd do cliente

    mv a0, s1
    call tratar_cliente   # a0 = fd do cliente

    li a7, 57
    mv a0, s1
    ecall                 # close(cliente)

    j .proximo_cliente


.section .data

sockaddr_in:
    .hword 2
    .hword 0x911F
    .word 0
    .dword 0

reuse_opt:
    .word 1

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

### Testando o loop

```bash
make clean
make
qemu-riscv64 ./helloworld &
```

Em outros terminais:

```bash
curl http://localhost:8081/
curl http://localhost:8081/
curl http://localhost:8081/invalido
```

Todas as requisições serão atendidas em sequência. Para parar, use `kill %1` ou Ctrl+C no terminal do QEMU.

### Resumo: x86-64 vs RISC-V 64 lado a lado

Depois de completar os dois tutoriais, aqui está uma tabela comparativa:

| Conceito | x86-64 (NASM) | RISC-V 64 (GNU as) |
|---|---|---|
| Assembler | `nasm` | `riscv64-linux-gnu-as` |
| Sintaxe de seção | `section .text` | `.section .text` |
| Símbolo global | `global _start` | `.global _start` |
| Syscall | `syscall` | `ecall` |
| Número syscall | `rax` | `a7` |
| Arg 1 | `rdi` | `a0` |
| Arg 2 | `rsi` | `a1` |
| Arg 3 | `rdx` | `a2` |
| Retorno | `rax` | `a0` |
| Movimento | `mov reg, immed` | `li reg, immed` |
| Load byte | `lodsb` / `mov al, [addr]` | `lb rd, offset(rs)` |
| Stack push | `push reg` | `addi sp, sp, -8; sd reg, 0(sp)` |
| Stack pop | `pop reg` | `ld reg, 0(sp); addi sp, sp, 8` |
| Chamada | `call label` | `call label` (pseudo = `jal ra, label`) |
| Retorno | `ret` | `ret` (pseudo = `jalr x0, ra, 0`) |
| Branch if zero | `jz label` | `beqz rs, label` |
| Branch if equal | `je label` | `beq rs1, rs2, label` |
| Comparação | `cmp a, b` (flags) | `beq`/`bne`/`blt`/`bge` (registrador vs registrador) |
| Label local | `label:` | `label:` ou `1:` / `1b` / `1f` |
| Tamanho de símbolo | `equ $ - label` | `name = . - label` ou `.equ name, . - label` |
| Número de GPRs | 16 | 31 + x0 = zero |
| Filosofia | CISC | RISC |

### Por que RISC-V?

Algumas vantagens de aprender assembly em RISC-V:

1. **ISA aberta e gratuita** — sem royalties, sem licenciamento. Qualquer um pode implementar.
2. **Design limpo** — sem legacy de décadas como o x86. Menos instruções, mais ortogonalidade.
3. **Crescimento rápido** — RISC-V está sendo adotado em microcontroladores, servidores, HPC e até em chips de AI.
4. **Simplicidade acadêmica** — a arquitetura foi projetada para ser ensinável. Os conceitos são transferíveis para ARM, MIPS e outras RISC.

### Indo além

Ideias para expandir o servidor RISC-V:

1. **Compilar para RISC-V nativo** — execute em hardware real (VisionFive 2, SiFive HiFive, etc.)
2. **Servir arquivos** — use `openat` (syscall 56) e `read` para servir arquivos do disco
3. **Multi-thread** — use `clone` (syscall 220) para atender clientes em paralelo
4. **Suporte a HTTP/1.1 keep-alive** — mantenha a conexão aberta para múltiplas requisições
5. **WebAssembly no RISC-V** — compile o servidor para WASM e execute em navegadores

Se você criar algo legal, contribua com o projeto! [Guia de contribuição](/contributing).

### Fim do tutorial Linux RISC-V

Parabéns! Você construiu um servidor web em assembly RISC-V — uma arquitetura que está moldando o futuro da computação. Você agora entende como aplicar os mesmos conceitos de sistemas operacionais (syscalls, sockets, rede) em duas arquiteturas completamente diferentes.

Volte para a [página inicial](/) e escolha seu próximo desafio!
