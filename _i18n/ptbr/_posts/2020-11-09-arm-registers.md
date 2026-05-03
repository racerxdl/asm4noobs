---
title: "Registradores ARM (32 e 64 bits)"
date: 2020-11-09T12:33:00-03:00
author: Lucas Teske
layout: page
permalink: /registers/arm
tags:
  - arm
  - registers
  - arm32
  - arm64
---

A arquitetura ARM tem dois conjuntos distintos de registradores: AArch32 (ARMv7 e anteriores, 32 bits) e AArch64 (ARMv8+, 64 bits). Vamos ver ambos.

### ARM 32 bits (AArch32 / ARMv7)

O ARM32 tem **16 registradores de uso geral** de 32 bits (r0–r15):

| Nome | Número | Função | Preservado? |
|------|--------|--------|-------------|
| r0 | 0 | Argumento 1 / retorno | Não |
| r1 | 1 | Argumento 2 / retorno (2º) | Não |
| r2 | 2 | Argumento 3 | Não |
| r3 | 3 | Argumento 4 | Não |
| r4 | 4 | Registrador salvo | Sim |
| r5 | 5 | Registrador salvo | Sim |
| r6 | 6 | Registrador salvo | Sim |
| r7 | 7 | Registrador salvo / syscall number | Sim |
| r8 | 8 | Registrador salvo | Sim |
| r9 | 9 | Registrador salvo / platform register | Sim |
| r10 | 10 | Registrador salvo | Sim |
| r11 | 11 | Frame Pointer (FP) | Sim |
| r12 | 12 | Intra-Procedure-call scratch (IP) | Não |
| r13 | 13 | Stack Pointer (SP) | Sim |
| r14 | 14 | Link Register (LR) | Não |
| r15 | 15 | Program Counter (PC) | — |

> No ARM32, o **PC (r15)** é acessível como registrador de uso geral! Você pode ler e escrever nele com `mov pc, r0` — o que torna branches e returns muito flexíveis, mas também perigosos.

#### Registrador de Estado (CPSR)

O CPSR (Current Program Status Register) armazena:

| Bits | Campo | Significado |
|------|-------|-------------|
| N | Negative | Resultado negativo |
| Z | Zero | Resultado zero |
| C | Carry | Vai-um / empresta-um |
| V | Overflow | Overflow com sinal |
| Q | Saturation | Saturação DSP |
| J | Jazelle | Modo Java bytecode |
| GE[3:0] | Greater-than-or-Equal | SIMD |
| E | Endianness | 0=little, 1=big |
| A | Abort | Mask de abort de dados |
| I | IRQ | Mask de interrupção |
| F | FIQ | Mask de interrupção rápida |
| T | Thumb | 0=ARM, 1=Thumb |
| M[4:0] | Mode | Modo do processador |

#### Bancos de Registradores

ARM32 tem **bancos de registradores** por modo de operação:

| Modo | Registradores bancados |
|------|----------------------|
| User / System | r0–r15 (padrão) |
| FIQ | r8_fiq–r14_fiq, SPSR_fiq |
| IRQ | r13_irq, r14_irq, SPSR_irq |
| Supervisor (SVC) | r13_svc, r14_svc, SPSR_svc |
| Abort | r13_abt, r14_abt, SPSR_abt |
| Undefined | r13_und, r14_und, SPSR_und |

Isso permite troca de contexto rápida: cada modo de exceção tem seus próprios r13 (SP) e r14 (LR), então não precisa salvar na stack para atender uma interrupção.

### ARM 64 bits (AArch64 / ARMv8+)

O AArch64 tem **31 registradores de uso geral** de 64 bits (x0–x30), mais SP e XZR:

| Nome | Número | Função | Preservado? |
|------|--------|--------|-------------|
| x0 | 0 | Argumento 1 / retorno | Não |
| x1 | 1 | Argumento 2 | Não |
| x2 | 2 | Argumento 3 | Não |
| x3 | 3 | Argumento 4 | Não |
| x4 | 4 | Argumento 5 | Não |
| x5 | 5 | Argumento 6 | Não |
| x6 | 6 | Argumento 7 | Não |
| x7 | 7 | Argumento 8 | Não |
| x8 | 8 | Retorno indireto (struct) | Não |
| x9–x15 | 9–15 | Temporários (caller-saved) | Não |
| x16 | 16 | IP0 (intra-procedure-call) | Não |
| x17 | 17 | IP1 (intra-procedure-call) | Não |
| x18 | 18 | Platform Register (PR) | Depende |
| x19–x28 | 19–28 | Callee-saved | Sim |
| x29 | 29 | Frame Pointer (FP) | Sim |
| x30 | 30 | Link Register (LR) | Não |
| SP | — | Stack Pointer | Sim |
| XZR | — | Zero Register (sempre 0) | — |
| PC | — | Program Counter | — |

> Em AArch64, o **PC e SP não são registradores de uso geral**. Diferente do ARM32, você não pode acessar o PC com `mov` — use branches (`b`, `bl`, `ret`).

#### Sub-registradores

Cada `xn` pode ser acessado como `wn` (32 bits inferiores). Escrever em `wn` automaticamente **zera os 32 bits superiores** de `xn`:

| Escrita | Bits superiores |
|---------|----------------|
| `mov x0, val` | — |
| `mov w0, val` | Zera bits 63:32 |

#### Registradores NEON / SIMD

32 registradores de 128 bits, acessíveis em várias larguras:

| Nome | Bits | Tipo |
|------|------|------|
| v0–v31 | 128 | NEON |
| q0–q31 | 128 | Quadword |
| d0–d31 | 64 | Doubleword (double float) |
| s0–s31 | 32 | Single float |
| h0–h31 | 16 | Half float |
| b0–b31 | 8 | Byte |

#### PSTATE (Processor State)

Substitui o CPSR do ARM32:

| Flag | Nome | Significado |
|------|------|-------------|
| N | Negative | Resultado < 0 |
| Z | Zero | Resultado = 0 |
| C | Carry | Carry / borrow |
| V | Overflow | Signed overflow |

As flags só são atualizadas por instruções com sufixo `S` (`adds`, `subs`, `cmp`).

#### Syscall ARM64

| Syscall | Número (x8) | Ação |
|---------|------------|------|
| read | 63 | Ler de fd |
| write | 64 | Escrever em fd |
| close | 57 | Fechar fd |
| socket | 198 | Criar socket |
| bind | 200 | Associar porta |
| listen | 201 | Modo escuta |
| accept | 202 | Aceitar conexão |
| exit | 93 | Sair |

### Convenção de Chamada ARM32 (AAPCS)

- Argumentos: **r0–r3** (os demais na stack)
- Retorno: **r0** (e r1 para 64 bits)
- Stack alinhada em **8 bytes** (SP mantido em 8 bytes)
- Syscall: `svc #0` com número em **r7**
- Callee-saved: r4–r11, SP

### Convenção de Chamada ARM64 (AAPCS64)

- Argumentos: **x0–x7** (os demais na stack)
- Retorno: **x0** (e x1 para 128 bits)
- Stack alinhada em **16 bytes**
- Syscall: `svc #0` com número em **x8** (diferente da convenção de função!)
- Callee-saved: x19–x28, x29 (FP), SP

### Comparação Rápida

| Característica | ARM32 | ARM64 |
|---|---|---|
| GPRs | 16 (r0–r15) | 31 (x0–x30) + SP/XZR |
| PC acessível | Sim (r15) | Não (acesso indireto) |
| GPR largura | 32 bits | 64 bits |
| Syscall número | r7 | x8 |
| Thumb (16-bit) | Sim | Não (unificado em 32-bit) |
| Predicação | Quase toda instrução | Apenas branches condicionais |
| Stack alignment | 8 bytes | 16 bytes |
