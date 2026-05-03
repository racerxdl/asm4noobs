---
title: "Registradores RISC-V (32 e 64 bits)"
date: 2020-11-16T12:33:00-03:00
author: Lucas Teske
layout: page
permalink: /registers/riscv
tags:
  - riscv
  - risc-v
  - registers
---

O RISC-V define 32 registradores inteiros (x0–x31) tanto em RV32 (32 bits) quanto em RV64 (64 bits). A diferença está apenas na largura: em RV32 cada registrador tem 32 bits, em RV64 tem 64 bits.

### Extensões da ISA

O RISC-V é uma ISA **modular**. Diferente de x86 e ARM — que são monolíticos e acumulam décadas de instruções — o RISC-V começa com uma base mínima e adiciona funcionalidade através de extensões padronizadas. Cada extensão é representada por uma letra.

#### Por que extensões existem?

Três razões principais:

1. **Simplicidade do hardware**: um microcontrolador barato pode implementar apenas `RV32I` (base inteira) e ignorar todo o resto — economizando área de silício e energia
2. **Especialização**: um acelerador de IA pode ter a extensão `V` (vetores) sem precisar carregar o peso de `F`/`D` (ponto flutuante), especialmente para cargas inteiras/quantizadas
3. **Evolução sem ruptura**: novas extensões são adicionadas sem quebrar software existente. Um compilador pode verificar quais extensões o hardware suporta e gerar o código ideal

#### Extensões Padrão

| Letra | Nome | O que adiciona |
|-------|------|---------------|
| **I** | Base Integer | Instruções inteiras básicas (obrigatório). RV32I, RV64I ou RV128I |
| **M** | Multiply/Divide | Multiplicação e divisão inteira (`mul`, `div`, `rem`, etc.) |
| **A** | Atomics | Instruções atômicas (`lr.w`, `sc.w`, `amoadd.w`) para sincronização entre cores |
| **F** | Single-Precision Float | 32 registradores de ponto flutuante `f0`–`f31`, instruções FP de 32 bits |
| **D** | Double-Precision Float | Expande `F` para 64 bits, reutiliza `f0`–`f31` como registradores de 64 bits |
| **C** | Compressed | Instruções comprimidas de 16 bits para densidade de código (~30% menor) |
| **V** | Vector | 32 registradores vetoriais `v0`–`v31`; VLEN depende da implementação, e o software configura `vl`/SEW |
| **B** | Bit Manipulation | Instruções de manipulação de bits (`clz`, `ctz`, `pcnt`, `ror`, etc.) |
| **H** | Hypervisor | Suporte a virtualização (transições VM, CSRs de hypervisor) |
| **Zicsr** | CSR Access | Instruções para acessar Control and Status Registers (`csrr`, `csrw`, etc.) |
| **Zifencei** | Instruction-Fetch Fence | `fence.i` para sincronizar o cache/fetch de instruções (necessário para código auto-modificável) |

> Extensões com prefixo `Z` são menores e mais específicas. Existem dezenas delas (`Zba`, `Zbb`, `Zbs`, `Zfh`, `Zkr`, etc.) cobrindo nichos como endereçamento, half-precision float e criptografia.

#### Nomenclatura

A configuração de um processador RISC-V é expressa concatenando as letras:

```
RV64IMAFDC
││  │││││└─ C: Compressed
││  ││││└── D: Double float
││  │││└─── F: Single float
││  ││└──── A: Atomics
││  │└───── M: Multiply/Divide
││  └────── I: Base Integer (implícito, mas listado)
│└─ 64: 64-bit
└── RV: RISC-V
```

Essa string é frequentemente abreviada como **RV64GC** (G = IMAFD + Zicsr + Zifencei, "general-purpose"). É a configuração típica para Linux e a que usamos no tutorial!

#### Extensões e Registradores

As extensões determinam **quais registradores existem**:

| Extensão | Registradores adicionais |
|----------|------------------------|
| (Base I) | x0–x31 (32 GPRs) |
| F | f0–f31 (32 registradores FP de 32 bits) |
| D | f0–f31 (expandidos para 64 bits) |
| V | v0–v31 (32 registradores vetoriais; VLEN é fixo pela implementação) |

Sem a extensão `F`, instruções como `fld`, `fadd.s` ou acesso a `f0`–`f31` não existem. Sem `D`, não existem `fadd.d`, `fmul.d`, etc. E sem `C`, o assembler rejeita instruções comprimidas de 16 bits como `c.addi`, `c.ld`, `c.sd`.

#### Como saber quais extensões estão disponíveis?

Em Linux, você pode consultar `/proc/cpuinfo`:

```bash
cat /proc/cpuinfo | grep isa
# Exemplo em um VisionFive 2:
# isa    : rv64imafdc_zba_zbb_zbc_zbs
```

Na prática, programando em assembly user-mode, você precisa saber quais extensões estão disponíveis antes de usar instruções que dependem delas. O toolchain (`gcc`, `as`) também aceita flags como `-march=rv64imafdc` para gerar código compatível.

### Registradores de Uso Geral (RV64)

| Nome ABI | Número | Descrição | Callee-saved? |
|----------|--------|-----------|---------------|
| zero | x0 | Hardwired a zero | — |
| ra | x1 | Return Address | Não |
| sp | x2 | Stack Pointer | Sim |
| gp | x3 | Global Pointer | — |
| tp | x4 | Thread Pointer | — |
| t0 | x5 | Temporário 0 | Não |
| t1 | x6 | Temporário 1 | Não |
| t2 | x7 | Temporário 2 | Não |
| s0 / fp | x8 | Saved register / Frame Pointer | Sim |
| s1 | x9 | Saved register | Sim |
| a0 | x10 | Argumento 1 / retorno | Não |
| a1 | x11 | Argumento 2 / retorno (2º) | Não |
| a2 | x12 | Argumento 3 | Não |
| a3 | x13 | Argumento 4 | Não |
| a4 | x14 | Argumento 5 | Não |
| a5 | x15 | Argumento 6 | Não |
| a6 | x16 | Argumento 7 | Não |
| a7 | x17 | Argumento 8 | Não |
| s2 | x18 | Saved register | Sim |
| s3 | x19 | Saved register | Sim |
| s4 | x20 | Saved register | Sim |
| s5 | x21 | Saved register | Sim |
| s6 | x22 | Saved register | Sim |
| s7 | x23 | Saved register | Sim |
| s8 | x24 | Saved register | Sim |
| s9 | x25 | Saved register | Sim |
| s10 | x26 | Saved register | Sim |
| s11 | x27 | Saved register | Sim |
| t3 | x28 | Temporário 3 | Não |
| t4 | x29 | Temporário 4 | Não |
| t5 | x30 | Temporário 5 | Não |
| t6 | x31 | Temporário 6 | Não |

### Registrador Zero (x0)

**x0 é hardwired a zero** e não pode ser modificado. Isso é uma das características mais inteligentes do RISC-V:

- `mv a0, x0` → zera a0 (sem precisar de imediato)
- `beq a0, x0, label` → branch if a0 == 0 (equivale a `beqz`)
- `add x0, a0, a1` → descarta o resultado (não altera flags, porque RISC-V não tem flags)

Como escrever em x0 é ignorado, você pode usá-lo como destino quando só quer os efeitos colaterais de uma instrução.

### Registrador Program Counter (PC)

O PC **não** é um registrador de uso geral no RISC-V. Diferente do ARM32 (onde r15 = PC), você não pode ler ou escrever o PC diretamente. Ele é atualizado por:

- Incremento automático após cada instrução
- `jal` / `jalr` (jump and link — chamadas de função)
- Branches condicionais (`beq`, `bne`, `blt`, `bge`, etc.)
- `j` (jump incondicional — pseudo-instrução para `jal x0, offset`)

### Sem Registrador de Flags!

RISC-V não tem registrador de flags (diferente do x86/RFLAGS e ARM/PSTATE). Branches condicionais comparam registradores **diretamente**:

| Instrução | Significado |
|-----------|-------------|
| `beq a0, a1, label` | Branch if a0 == a1 |
| `bne a0, a1, label` | Branch if a0 != a1 |
| `blt a0, a1, label` | Branch if a0 < a1 (signed) |
| `bge a0, a1, label` | Branch if a0 >= a1 (signed) |
| `bltu a0, a1, label` | Branch if a0 < a1 (unsigned) |
| `bgeu a0, a1, label` | Branch if a0 >= a1 (unsigned) |

Pseudo-instruções úteis:

| Pseudo | Expande para |
|--------|-------------|
| `beqz a0, label` | `beq a0, x0, label` |
| `bnez a0, label` | `bne a0, x0, label` |
| `j label` | `jal x0, label` |
| `ret` | `jalr x0, 0(ra)` |
| `call func` | `jal ra, func` em chamadas próximas, ou `auipc` + `jalr` para chamadas longas |

### Registradores de Ponto Flutuante (extensões F e D)

Com as extensões de ponto flutuante, ganhamos 32 registradores adicionais:

| Nome | Bits | Tipo |
|------|------|------|
| f0–f31 | 64 (com D) ou 32 (apenas F) | Ponto flutuante |

- RV32F/RV64F: registradores FP de 32 bits
- RV32D/RV64D: registradores FP de 64 bits (f0–f31)

Instruções: `fld` / `fsd` (load/store double), `fadd.d` / `fadd.s` (adição), `fmul.d`, `fdiv.d`, etc.

### Registradores Vetoriais (extensão V)

A extensão V adiciona **32 registradores vetoriais** (`v0`–`v31`), cada um com largura configurável (`VLEN`):

- VLEN típico: 128 a 1024 bits
- Largura dos elementos configurável: 8, 16, 32 ou 64 bits
- Comprimento do vetor configurável por instrução (`vl` — vector length)

### CSRs (Control and Status Registers)

O RISC-V define CSRs para configuração e controle do processador. São acessados com instruções específicas (`csrr`, `csrw`, `csrrs`, etc.):

| CSR | Função |
|-----|--------|
| mstatus | Machine status (interrupt enable, etc.) |
| mtvec | Machine trap vector (onde pular em exceções) |
| mepc | Machine exception PC (onde retornar após exceção) |
| mcause | Machine cause (código da exceção) |
| stvec | Supervisor trap vector |
| sepc | Supervisor exception PC |
| scause | Supervisor cause |
| cycle | Contador de ciclos (read-only) |
| time | Timer (read-only) |
| instret | Contador de instruções aposentadas (read-only) |

> Em Linux user-mode, CSRs não são acessíveis diretamente — o kernel gerencia isso. Mas em sistemas bare-metal (microcontroladores RISC-V), CSRs são essenciais.

### Modos de Privilégio

| Modo | Nome | Uso |
|------|------|-----|
| U | User | Aplicações |
| S | Supervisor | Kernel do SO (Linux) |
| M | Machine | Firmware / bootloader (obrigatório) |
| H | Hypervisor (opcional) | Virtualização |

Transições entre modos são feitas por exceções, interrupções ou `ecall` (syscall).

### Convenção de Chamada (psABI)

| Regra | Detalhe |
|-------|---------|
| Argumentos | a0–a7 (x10–x17) |
| Retorno | a0 (x10), a1 (x11) para 128 bits |
| Stack alignment | 16 bytes |
| Callee-saved | s0–s11 (x8–x9, x18–x27), sp (x2) |
| Caller-saved | ra (x1), t0–t6 (x5–x7, x28–x31), a0–a7 (x10–x17) |
| Syscall número | a7 (x17) |
| Syscall arg 1–6 | a0–a5 (x10–x15) |
| Syscall retorno | a0 (x10) |

### Syscalls Comuns (Linux RISC-V 64)

| Syscall | Número (a7) | Ação |
|---------|------------|------|
| read | 63 | Ler de fd |
| write | 64 | Escrever em fd |
| close | 57 | Fechar fd |
| socket | 198 | Criar socket |
| bind | 200 | Associar porta |
| listen | 201 | Escutar |
| accept | 202 | Aceitar conexão |
| setsockopt | 208 | Configurar socket |
| exit | 93 | Sair |

### Comparação RV32 vs RV64

| Característica | RV32 | RV64 |
|---|---|---|
| Largura dos GPRs | 32 bits | 64 bits |
| Número de GPRs | 32 (x0–x31) | 32 (x0–x31) |
| Load word | `lw` (32 bits) | `lw` (32 bits, sign-extend) |
| Load doubleword | — | `ld` (64 bits) |
| Store word | `sw` (32 bits) | `sw` (32 bits) |
| Store doubleword | — | `sd` (64 bits) |
| Palavra de instrução | 32 bits | 32 bits |
| Espaço endereçável | 4 GB | Teórico 16 EB (prático 256 TB) |
