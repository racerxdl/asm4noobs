---
title: "[linux-riscv] Fazendo Hello World"
date: 2020-10-12T12:33:00-03:00
author: Lucas Teske
layout: page
permalink: /webserver/riscv/part1
tags:
  - riscv
  - risc-v
  - syscall
  - write
  - hello
---

Na [parte anterior](/webserver/riscv/part0) fizemos nosso programa RISC-V apenas sair. Agora vamos fazer algo útil: escrever `Olá, mundo!` no terminal.

### A syscall write no RISC-V

A syscall `write` no RISC-V Linux tem o número **64** e espera três argumentos:

- **a0** = file descriptor (1 = stdout)
- **a1** = ponteiro para o buffer (a string)
- **a2** = quantidade de bytes a escrever

```asm
.section .rodata

helloworld:
    .ascii "Ola, mundo!\n"      # 12 bytes
    # Não tem terminador nulo automático!

helloworld_end:                  # label para calcular o tamanho
```

> No GNU assembler, `.ascii` cria uma string **sem** terminador nulo. Se quisesse com terminador, usaria `.asciz`. Mas no nosso tutorial usaremos `.ascii` + tamanho explícito (como o `db` do NASM).

Calculamos o tamanho com subtração de labels:

```asm
    li a7, 64           # syscall write
    li a0, 1            # fd = stdout
    la a1, helloworld   # ponteiro para a string
    li a2, 12           # tamanho = 12 bytes
    ecall
```

> `la` é uma pseudo-instrução que carrega o endereço de um label. Ela é expandida pelo assembler em `lui` + `addi` (ou `auipc` + `addi` dependendo da distância).

### Juntando com o exit

```asm
.section .text
.global _start

_start:
    # write(stdout, helloworld, 12)
    li a7, 64           # syscall write
    li a0, 1            # stdout
    la a1, helloworld
    li a2, 12
    ecall

    # exit(0)
    li a7, 93           # syscall exit
    li a0, 0
    ecall

.section .rodata

helloworld:
    .ascii "Ola, mundo!\n"
```

Compile e teste:

```bash
make clean
make
make run
# Deve imprimir: Ola, mundo!
```

### Funções em RISC-V

Assim como no x86, podemos criar funções com `call`/`ret`. No RISC-V, usamos `jal` (jump and link) e `jalr` para chamadas e `ret` para retorno.

`jal` salva o endereço de retorno no registrador `ra` (x1) e salta para o label. `ret` é uma pseudo-instrução que expande para `jalr x0, ra, 0`.

Vamos criar uma função `imprime`:

```asm
.section .text
.global _start

imprime:
    # Sempre escreve helloworld no stdout
    li a7, 64
    li a0, 1
    la a1, helloworld
    li a2, 12
    ecall
    ret

_start:
    jal imprime        # chama imprime (salva retorno em ra)
    jal imprime        # chama de novo
    jal imprime        # e de novo

    li a7, 93
    li a0, 0
    ecall

.section .rodata

helloworld:
    .ascii "Ola, mundo!\n"
```

> **Diferença x86 vs RISC-V**: No x86 usamos `call`/`ret`. No RISC-V usamos `jal`/`jalr`/`ret`. A pseudo-instrução `ret` é equivalente a `jalr x0, 0(ra)` (ou `jalr zero, ra, 0`).

### Contando caracteres dinamicamente

No x86 usamos `lodsb` para carregar bytes sequencialmente. RISC-V não tem essa instrução — precisamos fazer manualmente com `lb` (load byte).

Primeiro, adicionamos um terminador nulo na string (usando `.byte`):

```asm
helloworld:
    .ascii "Ola, mundo!\n"
    .byte 0             # terminador nulo
```

Agora criamos um contador de string:

```asm
# Função: conta_str
# Entrada: a0 = ponteiro da string
# Saída:   a0 = número de caracteres (sem o terminador nulo)
conta_str:
    mv t0, a0           # t0 = ponteiro da string
    li t1, 0            # t1 = contador

1:
    lb t2, 0(t0)        # carrega byte em t2
    beqz t2, 2f         # se for 0, terminou
    addi t1, t1, 1      # contador++
    addi t0, t0, 1      # avança ponteiro
    j 1b                # volta pro loop

2:
    mv a0, t1           # retorna o contador em a0
    ret
```

Algumas novidades do RISC-V aqui:

- `mv rd, rs` — pseudo-instrução para copiar registrador (expande para `addi rd, rs, 0`).
- `lb t2, 0(t0)` — carrega um byte do endereço em `t0` + offset 0 para `t2`.
- `beqz rs, label` — branch if equal to zero (pseudo para `beq rs, x0, label`).
- `addi rd, rs, imm` — soma imediato.
- `j label` — jump incondicional.
- Labels numéricos `1:` e referências `1b` (backward) / `1f` (forward) — conveniente para loops locais!

> **RISC-V não tem registrador de flags!** Enquanto o x86 usa `cmp` + `jz` (baseado na flag ZF), o RISC-V compara dois registradores diretamente com `beq` (branch equal), `bne` (branch not equal), `blt` (less than), etc.

### Função imprime genérica

Vamos criar uma função `imprime` que recebe uma string qualquer em `a0`:

```asm
imprime:
    # Salva registradores que vamos usar
    addi sp, sp, -32    # reserva 32 bytes para manter sp alinhado em 16 bytes
    sd ra, 24(sp)       # salva ra (porque vamos chamar conta_str)
    sd s0, 16(sp)       # salva s0
    sd s1, 8(sp)        # salva s1

    mv s0, a0           # s0 = ponteiro da string

    call conta_str      # a0 = tamanho da string
    mv s1, a0           # s1 = tamanho

    li a7, 64           # syscall write
    li a0, 1            # stdout
    mv a1, s0           # buffer = string
    mv a2, s1           # tamanho
    ecall

    ld ra, 24(sp)       # restaura ra
    ld s0, 16(sp)       # restaura s0
    ld s1, 8(sp)        # restaura s1
    addi sp, sp, 32     # libera a stack
    ret
```

> **Aqui está a maior diferença:** RISC-V não tem `push`/`pop`! Gerenciamos a stack manualmente:
> 1. `addi sp, sp, -32` — move o stack pointer para baixo (cresce para baixo) mantendo alinhamento de 16 bytes.
> 2. `sd reg, offset(sp)` — salva registrador na stack (store doubleword, 8 bytes).
> 3. `ld reg, offset(sp)` — restaura registrador da stack (load doubleword).
> 4. `addi sp, sp, 32` — restaura o stack pointer.

### Convenção de chamada RISC-V

No RISC-V, os registradores são divididos em:

| Registrador | Nome ABI | Preservado? | Uso |
|---|---|---|---|
| x1 | ra | Não (caller-saved) | Endereço de retorno |
| x2 | sp | Sim (callee-saved) | Stack pointer |
| x5-x7 | t0-t2 | Não | Temporários |
| x8 | s0/fp | Sim | Salvo / frame pointer |
| x9 | s1 | Sim | Salvo |
| x10-x17 | a0-a7 | Não | Argumentos de função |
| x18-x27 | s2-s11 | Sim | Salvos |
| x28-x31 | t3-t6 | Não | Temporários |

Registradores `s0`-`s11` devem ser preservados pela função chamada (se forem usados). Registradores `t0`-`t6` e `a0`-`a7` podem ser livremente alterados. Como usamos `s0` e `s1`, salvamos eles na stack.

### Código completo

```asm
.section .text
.global _start

conta_str:
    mv t0, a0
    li t1, 0
1:
    lb t2, 0(t0)
    beqz t2, 2f
    addi t1, t1, 1
    addi t0, t0, 1
    j 1b
2:
    mv a0, t1
    ret

imprime:
    addi sp, sp, -32
    sd ra, 24(sp)
    sd s0, 16(sp)
    sd s1, 8(sp)

    mv s0, a0

    call conta_str
    mv s1, a0

    li a7, 64
    li a0, 1
    mv a1, s0
    mv a2, s1
    ecall

    ld ra, 24(sp)
    ld s0, 16(sp)
    ld s1, 8(sp)
    addi sp, sp, 32
    ret

_start:
    la a0, helloworld
    call imprime

    la a0, msg2
    call imprime

    li a7, 93
    li a0, 0
    ecall

.section .rodata

helloworld:
    .ascii "Ola, mundo!\n"
    .byte 0

msg2:
    .ascii "QQ eu to fazendo aqui?\n"
    .byte 0
```

Compile e teste:

```bash
make clean
make
make run
```

Saída esperada:

```
Ola, mundo!
QQ eu to fazendo aqui?
```

### Salvando o progresso

```bash
git add helloworld.S
git commit -am "Hello World no RISC-V! Funcao imprime generica e contador de strings"
```

### Conclusão da segunda parte

Já dominamos o básico do RISC-V: syscalls, funções com `call`/`ret`, stack manual, e contagem de strings. A sintaxe é diferente do x86, mas os conceitos são os mesmos — uma vez que você entende uma arquitetura, migrar para outra é questão de aprender a nova "sintaxe"!

Na próxima parte: sockets e TCP no RISC-V!

[Aceitando uma conexão TCP](/webserver/riscv/part2)
