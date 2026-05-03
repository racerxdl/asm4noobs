O RISC-V 64 (RV64) é uma arquitetura RISC limpa e moderna. Se você já leu a estrutura do ARM64, muitas ideias vão soar familiares — mas o RISC-V é ainda mais minimalista e ortogonal.

### Registradores de Uso Geral

O RV64 tem **32 registradores inteiros** de 64 bits (x0–x31), mais o **PC** (não acessível diretamente):

| Nome | Número | Função | Preservado? |
|------|--------|--------|-------------|
| zero | x0 | Sempre 0 (hardwired) | — |
| ra | x1 | Return Address (endereço de retorno) | Não |
| sp | x2 | Stack Pointer | Sim |
| gp | x3 | Global Pointer | — |
| tp | x4 | Thread Pointer | — |
| t0–t2 | x5–x7 | Temporários | Não |
| s0/fp | x8 | Frame Pointer / Saved | Sim |
| s1 | x9 | Saved register | Sim |
| a0–a1 | x10–x11 | Argumentos / retorno de função | Não |
| a2–a7 | x12–x17 | Argumentos de função | Não |
| s2–s11 | x18–x27 | Saved registers | Sim |
| t3–t6 | x28–x31 | Temporários | Não |

> **x0 é hardwired a zero**: qualquer leitura retorna 0, escritas são ignoradas. Isso permite pseudo-instruções úteis como `beqz` (branch if equal to zero) que o assembler converte para `beq rs, x0, label`.

### Sem Registrador de Flags!

RISC-V **não tem registrador de flags**! Diferente do x86 (RFLAGS) e ARM64 (PSTATE), todas as comparações e condições são feitas diretamente com branches condicionais:

```asm
blt x0, x1, label    # branch se x0 < x1
bge x0, x1, label    # branch se x0 >= x1
beq x0, x1, label    # branch se x0 == x1
bne x0, x1, label    # branch se x0 != x1
bltu x0, x1, label   # branch se x0 < x1 (unsigned)
bgeu x0, x1, label   # branch se x0 >= x1 (unsigned)
```

Isso simplifica o pipeline (não precisa trackear flags entre instruções) e evita efeitos colaterais. A pseudo-instrução `beqz` expande para `beq rs, x0, label`.

### Níveis de Privilégio

RISC-V define 3 níveis (mais um opcional):

| Nível | Nome | Uso típico |
|-------|------|------------|
| U | User mode | Aplicações (nosso código roda aqui) |
| S | Supervisor mode | Kernel do SO |
| M | Machine mode | Firmware / bootloader (obrigatório) |
| H | Hypervisor (opcional) | Virtualização |

Todo sistema RISC-V deve implementar o Machine mode (M-mode). O Linux roda em S-mode e nossas aplicações em U-mode. A syscall é feita com `ecall`, que causa transição de U-mode para S-mode.

### CSRs (Control and Status Registers)

CSRs são registradores especiais acessados com instruções dedicadas:

```asm
csrr t0, mstatus    # lê machine status (M-mode)
csrw mepc, t0       # escreve machine exception PC
csrrs t0, mcause, t1   # lê e seta bits
```

Em aplicações Linux user-mode, raramente acessamos CSRs diretamente (o kernel gerencia isso). Mas em sistemas bare-metal, CSRs são essenciais para configurar interrupções, proteção de memória, etc.

### Arquitetura Load/Store

Como toda boa arquitetura RISC, RISC-V é load/store puro:

```asm
ld t0, 0(t1)        # t0 = mem[t1 + 0]          (load 64 bits)
sd t0, 0(t1)        # mem[t1 + 0] = t0          (store 64 bits)
lw t0, 0(t1)        # t0 = mem[t1 + 0] (32-bit sign-extend)
lb t0, 0(t1)        # t0 = mem[t1 + 0] (byte, sign-extend)
lbu t0, 0(t1)       # t0 = mem[t1 + 0] (byte, zero-extend)
```

O offset é sempre um imediato de 12 bits com sinal, adicionado ao registrador base.

### Codificação de Instruções

O RISC-V tem dois tamanhos de instrução:

- **32 bits**: instruções padrão (formato R/I/S/B/U/J)
- **16 bits**: instruções comprimidas (extensão C — opcional mas quase universal)

Os 2 bits inferiores de cada instrução indicam o tamanho:
- `11`: instrução de 32 bits
- `00/01/10`: instrução comprimida de 16 bits

Isso significa que as instruções comprimidas são apenas uma redução de código, não um modo separado (diferente do Thumb no ARM32).

### Registradores de Ponto Flutuante (Extensões F/D)

Com as extensões F (single-precision) e D (double-precision):

- **f0–f31**: 32 registradores de ponto flutuante de 64 bits
- Instruções específicas: `fld`, `fsd`, `fadd.d`, `fmul.s`, etc.
- A extensão V (Vector) adiciona registradores vetoriais separados (`v0`–`v31`) para SIMD escalável

### Convenção de Chamada

A convenção RISC-V para Linux (psABI) define:

- Argumentos: **a0–a7** (x10–x17)
- Retorno: **a0** (e a1 para 128 bits)
- Stack alinhada em **16 bytes**
- **ra (x1)**: endereço de retorno (salvo pelo caller)
- **s0–s11 (x8–x9, x18–x27)**: callee-saved
- **sp (x2)**: stack pointer, deve ser preservado com alinhamento de 16 bytes
- Frame pointer em **s0 (x8)** (opcional)

### Chamada de Sistema (Linux RISC-V)

Syscall via `ecall`:

- Número da syscall em **a7 (x17)**
- Argumentos em **a0–a5 (x10–x15)**
- Retorno em **a0 (x10)**

| Syscall | Número | Uso no tutorial |
|---------|--------|-----------------|
| read | 63 | Ler requisição HTTP |
| write | 64 | Enviar resposta |
| close | 57 | Fechar sockets |
| socket | 198 | Criar socket |
| bind | 200 | Associar porta |
| listen | 201 | Modo escuta |
| accept | 202 | Aceitar conexão |
| setsockopt | 208 | Configurar opções de socket |
| exit | 93 | Encerrar programa |

### Comparação Rápida: RISC-V vs ARM64 vs x86-64

| Característica | x86-64 | ARM64 (AArch64) | RISC-V 64 |
|---|---|---|---|
| GPRs | 16 | 31 (+ SP/XZR) | 32 (x0=0) |
| Flags | Sim (RFLAGS) | Sim (PSTATE) | Não |
| Tamanho instrução | 1–15 bytes | 4 bytes fixo | 4 bytes (2 com ext. C) |
| Load/Store | Não puro | Puro | Puro |
| Condição em ALU | Flags implícitas | Sufixo S opcional | Branches explícitos |
| ISA | Proprietária | Licenciada | Aberta e gratuita |
| Extensibilidade | Monolítica | Monolítica | Modular |
| Idade | 1978 | 1985 | 2010 |
