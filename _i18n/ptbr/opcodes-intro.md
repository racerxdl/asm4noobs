Códigos de operação — **opcodes** — são os comandos que o processador entende. Cada instrução assembly é traduzida para um ou mais bytes que representam um opcode e seus operandos. Entender como instruções são codificadas é essencial para ler assembly com fluência.

### O que é um Opcode?

Um opcode (operation code) é um número binário que diz à CPU **qual operação executar**. Por exemplo, no x86-64:

```asm
90             ; opcode: NOP (no operation)
48 89 D8       ; opcode: MOV RAX, RBX
B8 2A 00 00 00 ; opcode: MOV EAX, 42
```

O primeiro byte (ou primeiros bytes) identifica a operação. Bytes adicionais especificam os operandos (registradores, imediatos, endereços de memória).

### Tipos de Operandos

Cada instrução pode operar sobre diferentes tipos de operandos:

| Tipo | Exemplo | Descrição |
|------|---------|-----------|
| **Registrador** | `mov rax, rbx` | Opera diretamente em registradores |
| **Imediato** | `mov rax, 42` | Valor constante embutido na instrução |
| **Memória** | `mov rax, [rbx]` | Acessa a memória no endereço especificado |
| **Implícito** | `syscall` | Operandos determinados pela instrução |

### Modos de Endereçamento

Instruções que acessam memória podem usar diferentes modos de endereçamento:

```asm
mov rax, [0x600000]         ; Direto: endereço absoluto
mov rax, [rbx]              ; Indireto: ponteiro em RBX
mov rax, [rbx + 8]          ; Base + deslocamento constante
mov rax, [rbx + rcx]        ; Base + índice
mov rax, [rbx + rcx*4]      ; Base + índice × escala
mov rax, [rbx + rcx*4 + 8]  ; Base + índice × escala + deslocamento
```

### RISC vs CISC

A diferença fundamental entre arquiteturas RISC e CISC está nos opcodes:

**CISC** (Complex Instruction Set Computer) — x86:
- Muitos opcodes (centenas)
- Instruções de tamanho variável (1 a 15 bytes no x86)
- Instruções complexas que fazem múltiplas operações
- Exemplo: `rep movsb` copia uma string inteira em uma instrução
- Operandos de memória podem ser usados diretamente em operações aritméticas

```asm
add rax, [rbx]        ; x86: soma memória → registrador (1 instrução)
```

**RISC** (Reduced Instruction Set Computer) — ARM64, RISC-V:
- Conjunto de instruções mais regular e simples
- Instruções de tamanho fixo (4 bytes em ARM64 e RISC-V padrão)
- Cada instrução faz uma operação simples
- Apenas loads e stores acessam memória (load/store architecture)

```asm
ldr x0, [x1]          ; ARM64: carrega da memória
add x0, x0, x2        ; ARM64: soma registradores (2 instruções)
```

### Categorias de Instruções

Independentemente da arquitetura, as instruções se agrupam em categorias:

#### 1. Movimento de Dados

Copiam valores entre registradores e memória:

| x86-64 | ARM64 | RISC-V | Significado |
|--------|-------|--------|-------------|
| `mov rax, rbx` | `mov x0, x1` | `mv a0, a1` | Copiar registrador |
| `mov rax, 42` | `mov x0, #42` | `li a0, 42` | Carregar imediato |
| `mov rax, [rbx]` | `ldr x0, [x1]` | `ld a0, 0(a1)` | Carregar da memória |
| `mov [rbx], rax` | `str x0, [x1]` | `sd a0, 0(a1)` | Armazenar na memória |
| `push rax` | `stp x0, x1, [sp, #-16]!` | `addi sp, sp, -16; sd a0, 8(sp)` | Salvar na stack |

#### 2. Aritmética

Operações matemáticas:

| x86-64 | ARM64 | RISC-V | Significado |
|--------|-------|--------|-------------|
| `add rax, rbx` | `add x0, x0, x1` | `add a0, a0, a1` | Soma |
| `sub rax, rbx` | `sub x0, x0, x1` | `sub a0, a0, a1` | Subtração |
| `inc rax` | `add x0, x0, #1` | `addi a0, a0, 1` | Incremento |
| `dec rax` | `sub x0, x0, #1` | `addi a0, a0, -1` | Decremento |
| `imul rax, rbx` | `mul x0, x0, x1` | `mul a0, a0, a1` | Multiplicação |

#### 3. Lógica e Bits

Operações bit a bit:

| x86-64 | ARM64 | RISC-V | Significado |
|--------|-------|--------|-------------|
| `and rax, rbx` | `and x0, x0, x1` | `and a0, a0, a1` | AND bit a bit |
| `or rax, rbx` | `orr x0, x0, x1` | `or a0, a0, a1` | OR bit a bit |
| `xor rax, rbx` | `eor x0, x0, x1` | `xor a0, a0, a1` | XOR bit a bit |
| `shl rax, 1` | `lsl x0, x0, #1` | `slli a0, a0, 1` | Shift left |
| `shr rax, 1` | `lsr x0, x0, #1` | `srli a0, a0, 1` | Shift right |

#### 4. Controle de Fluxo

Alteram o fluxo de execução:

**x86-64** (usando flags implícitas de `cmp`):
```asm
cmp rax, rbx
je  .igual       ; salta se RAX == RBX
jne .diferente   ; salta se RAX != RBX
jg  .maior       ; salta se RAX > RBX (com sinal)
jl  .menor       ; salta se RAX < RBX (com sinal)
jmp .sempre      ; salta incondicionalmente
```

**ARM64** (`cmp` atualiza flags explicitamente):
```asm
cmp x0, x1
b.eq .igual      ; branch if equal
b.ne .diferente  ; branch if not equal
b.gt .maior      ; branch if greater than
b.lt .menor      ; branch if less than
b .sempre        ; branch incondicional
```

**RISC-V** (branches comparam registradores diretamente, sem flags):
```asm
beq a0, a1, .igual      ; branch if equal
bne a0, a1, .diferente  ; branch if not equal
blt a0, a1, .menor      ; branch if less than
bge a0, a1, .maior_igual ; branch if greater or equal
j .sempre                ; jump incondicional
```

#### 5. Chamadas de Função

Transferem controle para sub-rotinas e retornam:

| x86-64 | ARM64 | RISC-V | Ação |
|--------|-------|--------|------|
| `call func` | `bl func` | `call func` | Salva retorno em stack/LR, salta |
| `ret` | `ret` | `ret` | Retorna ao endereço salvo |

### Codificação Real de um Opcode

Vamos ver como a instrução `mov rax, rbx` (x86-64) é codificada:

```
mov rax, rbx  →  48 89 D8
                  │  │  └─ ModR/M: mod=11, reg=RBX (origem), r/m=RAX (destino)
                  │  └─── Opcode principal: MOV r/m64, r64
                  └────── REX prefix: 64-bit operand size
```

E como `addi a0, a0, 5` (RISC-V) é codificada:

```
addi a0, a0, 5  →  palavra de instrução: 0x00550513
                   bytes no arquivo (little-endian): 13 05 55 00

                   │││││││└─────── opcode: 0010011 (OP-IMM)
                   │││││└───────── rd = a0 = 01010
                   │││└─────────── funct3 = 000 (ADDI)
                   │└───────────── rs1 = a0 = 01010
                   └────────────── immediate = 5 = 000000000101
```

> Na prática, você raramente precisa decodificar opcodes manualmente — o assembler faz isso. Mas entender a estrutura ajuda a ler disassembly e entender o "peso" das instruções.

### Prefixos e Extensões (x86)

O x86 é famoso por seus prefixos — bytes adicionais antes do opcode que modificam o comportamento:

- **REX** (0x48): acesso a registradores de 64 bits e R8–R15
- **0x66**: operand size override (alterna entre 16 e 32 bits)
- **0xF2 / 0xF3**: REP/REPE/REPNE (repetição de string)
- **0x0F**: escape para opcodes de 2 bytes (SSE, etc.)

Essa complexidade é uma das razões pelas quais o decoder x86 é notoriamente complicado de implementar.

### Conclusão

- Opcodes são números binários que comandam a CPU
- RISC tem poucos opcodes simples e fixos; CISC tem muitos opcodes complexos e variáveis
- Instruções se agrupam em movimento de dados, aritmética, lógica, controle de fluxo e chamadas
- Modos de endereçamento definem como operandos de memória são calculados
- O assembler cuida da codificação para você — mas entender o mecanismo é valioso
