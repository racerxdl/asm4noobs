O ARM64 (AArch64) é o estado de execução de 64 bits da arquitetura ARMv8. Vamos conhecer sua estrutura do ponto de vista do programador assembly.

### Registradores de Uso Geral

O AArch64 tem **31 registradores de uso geral** de 64 bits (x0–x30), mais o **zero register** e o **stack pointer**:

| Nome | Função | Preservado? |
|------|--------|-------------|
| x0–x7 | Argumentos de função / retorno | Não |
| x8 | Retorno indireto (struct) | Não |
| x9–x15 | Temporários (caller-saved) | Não |
| x16 | IP0 (intra-procedure-call scratch) | Não |
| x17 | IP1 (intra-procedure-call scratch) | Não |
| x18 | Platform register (PR) | Depende da plataforma |
| x19–x28 | Registradores salvos (callee-saved) | Sim |
| x29 | Frame Pointer (FP) | Sim |
| x30 | Link Register (LR — endereço de retorno) | Não |

Cada registrador xn pode ser acessado como **wn** para os 32 bits inferiores:

```asm
mov x0, 0x1234567890ABCDEF   # 64 bits
mov w0, 0x12345678           # 32 bits (zera bits 63:32)
```

> Em AArch64, escrever em `wn` automaticamente zera os 32 bits superiores de `xn`. Isso é parecido com escrever em EAX no x86-64; escrever em AX ou AL não zera os bits superiores.

### Registradores Especiais

- **XZR / WZR** (Zero Register): sempre lê como 0, descarta escritas. Usado em comparações e operações que precisam de uma constante zero.
- **SP** (Stack Pointer): não é um registrador de uso geral. Deve ser acessado com instruções específicas.
- **PC** (Program Counter): em AArch64, **não** é um registrador de uso geral. Não pode ser lido ou escrito diretamente. É modificado por branches, calls e returns.

### PSTATE (Processor State)

O registrador de estado armazena as **flags de condição**:

| Flag | Nome | Significado |
|------|------|-------------|
| N | Negative | Resultado negativo |
| Z | Zero | Resultado igual a zero |
| C | Carry | Vai-um / empresta-um |
| V | Overflow | Overflow com sinal |

Diferentemente do x86, as flags no ARM64 **não** são atualizadas automaticamente por toda instrução. Você precisa usar a variante com sufixo `S`:

```asm
adds x0, x1, x2    # atualiza flags
add  x0, x1, x2    # NÃO atualiza flags
cmp  x0, x1        # sempre atualiza flags (alias de subs xzr, x0, x1)
```

Isso dá mais controle ao programador e evita efeitos colaterais indesejados.

### Exception Levels (Níveis de Privilégio)

O ARM64 define 4 níveis de execução:

| Nível | Nome | Uso típico |
|-------|------|------------|
| EL0 | User | Aplicações (nosso código assembly roda aqui) |
| EL1 | Kernel | Kernel do sistema operacional |
| EL2 | Hypervisor | Virtualização |
| EL3 | Secure Monitor | Firmware seguro / TrustZone |

Neste tutorial, todo nosso código roda em **EL0** (modo usuário no Linux). As syscalls (`svc #0` em ARM64) causam uma transição para EL1.

### Registradores NEON / SIMD

O ARM64 tem **32 registradores SIMD/FP** de 128 bits (v0–v31), que podem ser acessados em várias larguras:

| Nome | Largura | Uso |
|------|---------|-----|
| q0–q31 | 128 bits | NEON SIMD completo |
| d0–d31 | 64 bits | Double-precision float ou NEON duplo |
| s0–s31 | 32 bits | Single-precision float |
| h0–h31 | 16 bits | Half-precision float |
| b0–b31 | 8 bits | Byte |

### Arquitetura Load/Store

ARM64 é uma arquitetura **load/store pura**: instruções aritméticas e lógicas operam apenas em registradores. Para acessar memória, você usa load e store:

```asm
ldr x0, [x1]       # x0 = mem[x1]           (load 64 bits)
str x0, [x1]       # mem[x1] = x0           (store 64 bits)
ldr w0, [x1]       # w0 = mem[x1]           (load 32 bits, zera upper)
ldrb w0, [x1]      # w0 = mem[x1] (byte)   (load 8 bits)
ldp x0, x1, [sp]   # carrega dois registradores de uma vez
stp x0, x1, [sp]   # salva dois registradores de uma vez
```

Com modos de endereçamento flexíveis:

```asm
ldr x0, [x1, #8]      # base + offset imediato
ldr x0, [x1, x2]      # base + registrador
ldr x0, [x1, x2, lsl #3]  # base + (registrador << 3)
ldr x0, [x1], #8      # pós-incremento: x0 = mem[x1]; x1 += 8
ldr x0, [x1, #8]!     # pré-incremento: x1 += 8; x0 = mem[x1]
```

### Instruções de 32 Bits Fixas

Toda instrução AArch64 tem exatamente **32 bits** (4 bytes). Isso simplifica a decodificação em hardware. O ARM32 (AArch32) também tem modo Thumb com instruções de 16 bits, mas em AArch64 isso foi unificado.

### Convenção de Chamada (AAPCS64)

A convenção de chamada ARM64 para Linux define:

- Argumentos: **x0–x7** (os demais na stack)
- Retorno: **x0** (e x1 para 128 bits)
- Stack deve ser alinhada em **16 bytes** no ponto de chamada
- **LR (x30)**: endereço de retorno; é caller-saved, então funções que chamam outras normalmente salvam LR na stack
- **FP (x29)**: frame pointer, usado para debug e unwind
- **x19–x28**: callee-saved

### Chamada de Sistema (Linux ARM64)

No Linux ARM64, a syscall é feita com `svc #0`:

- Número da syscall em **x8**
- Argumentos em **x0–x5**
- Retorno em **x0**
- Convenção de syscall **diferente** da convenção de função! (x8 vs x0 para o número)

| Syscall | Número ARM64 | No tutorial |
|---------|-------------|-------------|
| read | 63 | Leitura de requisição |
| write | 64 | Envio de resposta |
| close | 57 | Fechar sockets |
| socket | 198 | Criar socket |
| bind | 200 | Associar porta |
| listen | 201 | Modo escuta |
| accept | 202 | Aceitar conexão |
| exit | 93 | Sair do programa |

> Os números de syscall do ARM64 são os mesmos do `asm-generic`, iguais aos do RISC-V!
