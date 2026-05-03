---
title: "[linux-riscv] Criando o projeto e um programa que sai"
date: 2020-10-05T12:33:00-03:00
author: Lucas Teske
layout: page
permalink: /webserver/riscv/part0
tags:
  - riscv
  - risc-v
  - syscall
  - exit
  - qemu
---

Aqui começaremos nossa jornada com RISC-V! Faremos o mesmo que fizemos no tutorial x86: criar um programa que sai sem crashar. Mas antes, precisamos do ambiente de desenvolvimento para RISC-V.

Como a maioria das pessoas ainda não tem um computador RISC-V (eles estão chegando!), usaremos ferramentas de compilação cruzada e o QEMU para testar. Se você tem hardware RISC-V nativo (ex: StarFive VisionFive, SiFive HiFive, ou uma FPGA com RISC-V), pode pular a parte do QEMU.

### Instalando requisitos

Precisamos instalar três coisas:

1. O toolchain de compilação cruzada RISC-V (GNU assembler + linker)
2. O QEMU para emular RISC-V (modo usuário)
3. O `git` para versionamento

```bash
sudo apt install gcc-riscv64-linux-gnu qemu-user git
```

> **Arch Linux**: `sudo pacman -S riscv64-linux-gnu-gcc qemu-user`
> **Fedora**: `sudo dnf install riscv64-linux-gnu-gcc qemu-user`

Verifique se as ferramentas estão instaladas:

```bash
riscv64-linux-gnu-as --version
qemu-riscv64 --version
```

### Preparando nosso projeto

```bash
mkdir -p hello-asm-riscv
cd hello-asm-riscv
git init
```

Para facilitar a compilação, criamos um `Makefile` adaptado para RISC-V:

```makefile
ASM_SRC=helloworld.S
ASM_OBJ=$(ASM_SRC:%.S=%.o)
PROGRAM=helloworld

AS=riscv64-linux-gnu-as
LD=riscv64-linux-gnu-ld
QEMU=qemu-riscv64

ASFLAGS=-g
LDFLAGS=

all: $(PROGRAM)

%.o: %.S
	@echo "Montando $< -> $@"
	@$(AS) $(ASFLAGS) -o $@ $<

clean:
	@echo "Limpando projeto"
	@rm -f $(PROGRAM) *.o

link: $(ASM_OBJ)
	@echo "Ligando objetos $(ASM_OBJ)"
	@$(LD) $(LDFLAGS) -o $(PROGRAM) $(ASM_OBJ)

$(PROGRAM): link
	@echo "YEY!"

run: $(PROGRAM)
	@echo "Executando no QEMU RISC-V..."
	@$(QEMU) ./$(PROGRAM)

.PHONY: clean run
```

Diferente do Makefile x86, aqui usamos o assembler e linker GNU específicos para RISC-V e adicionamos um target `run` que executa via QEMU.

Salvamos o Makefile:

```bash
git add Makefile
git commit -am "Makefile adicionado para RISC-V"
```

### Arquitetura RISC-V: primeiras diferenças

Antes de escrevermos código, vamos entender as diferenças principais entre RISC-V (64 bits) e x86-64:

| Característica | x86-64 | RISC-V 64 |
|---|---|---|
| Filosofia | CISC | RISC |
| Registradores | 16 GPRs (RAX-R15) | 31 GPRs (x1-x31) + x0=0 |
| Convenção de argumentos | RDI, RSI, RDX, RCX, R8, R9 | a0-a7 (x10-x17) |
| Chamada de sistema | `syscall` | `ecall` |
| Número da syscall | RAX | a7 (x17) |
| Retorno | RAX | a0 (x10) |
| Stack | `push`/`pop` | Manual: addi sp / sd / ld |
| Saltos condicionais | `jz`, `jnz`, etc (baseado em flags) | `beq`, `bne`, `blt`, etc (compara dois registradores) |
| Load imediato | `mov reg, immed` | `li reg, immed` (pseudo-instrução) |

> A pseudo-instrução `li` é expandida pelo assembler em uma combinação de `lui` e `addi`. Você pode usar ela sem preocupações!

A tabela completa de syscalls do Linux RISC-V usa os números do conjunto `asm-generic`. As que usaremos:

| Syscall | Número RISC-V | x86-64 (comparação) |
|---------|---------------|---------------------|
| read | 63 | 0 |
| write | 64 | 1 |
| close | 57 | 3 |
| socket | 198 | 41 |
| bind | 200 | 49 |
| listen | 201 | 50 |
| accept | 202 | 43 |
| setsockopt | 208 | 54 |
| exit | 93 | 60 |

> Os números são diferentes do x86! RISC-V Linux usa a tabela genérica (`asm-generic/unistd.h`), então confira sempre antes de usar.

### Nosso primeiro programa RISC-V

Agora ao código! Criamos `helloworld.S` (note a extensão `.S` — é a convenção do GNU assembler para assembly com pré-processador):

```asm
.section .text
.global _start

_start:
    # exit(0)
    li a7, 93       # syscall exit (93 no RISC-V)
    li a0, 0        # status = 0 (OK)
    ecall           # chama o kernel
```

Vamos entender cada linha:

- `.section .text` — equivalente ao `section .text` do NASM. Declara a seção de código.
- `.global _start` — equivalente ao `global _start`. Torna o símbolo visível ao linker.
- `_start:` — label (sem dois pontos também funciona no GNU as, mas usamos `:` para clareza).
- `li a7, 93` — carrega o valor 93 no registrador a7 (syscall exit).
- `li a0, 0` — carrega o valor 0 no registrador a0 (status de saída).
- `ecall` — executa a chamada de sistema (equivalente ao `syscall` do x86).

> **Convenção de syscall RISC-V Linux:** o número da syscall vai em `a7`, os argumentos em `a0` a `a5`, e o retorno vem em `a0`.

Compile e teste:

```bash
make clean
make
make run
```

Se tudo funcionou, o programa sai silenciosamente com status 0 — sem segmentation fault! Para confirmar:

```bash
make run
echo $?   # deve imprimir 0
```

### Comparação lado a lado: x86 vs RISC-V

```asm
# ──── x86-64 (NASM) ────
section .text
global _start

_start:
  mov rax, 60      ; exit
  mov rdi, 0       ; status
  syscall

# ──── RISC-V 64 (GNU as) ────
.section .text
.global _start

_start:
  li a7, 93        # exit
  li a0, 0         # status
  ecall
```

As semânticas são idênticas, mas:

- RISC-V usa `a7` para o número da syscall (não `a0` como no x86 que usa `rax`).
- RISC-V usa `a0` para o primeiro argumento (equivalente ao `rdi` do x86).
- O número **93** é o `exit` no RISC-V (60 no x86).

### Salvando o progresso

```bash
git add helloworld.S
git commit -am "Meu primeiro programa RISC-V sabe sair!"
```

### Conclusão da primeira parte

Montamos nosso ambiente de compilação cruzada RISC-V, entendemos as diferenças fundamentais em relação ao x86, e escrevemos um programa que chama o `exit` corretamente.

Na próxima parte, vamos fazer o Hello World: usar a syscall `write` e criar nossa primeira função em RISC-V.

[Fazendo Hello World](/webserver/riscv/part1)
