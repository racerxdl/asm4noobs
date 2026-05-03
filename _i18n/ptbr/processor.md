Antes de escrever código assembly, precisamos entender o que é um processador e como ele executa instruções. Vamos construir um modelo mental simples, mas correto, de como uma CPU funciona.

### O Modelo de von Neumann

A maioria dos computadores modernos segue a **arquitetura de von Neumann** (1945), que define quatro componentes principais:

1. **Unidade de Controle** (Control Unit): busca e decodifica instruções
2. **Unidade Lógica e Aritmética** (ALU): executa cálculos e operações lógicas
3. **Memória**: armazena instruções e dados
4. **Entrada/Saída**: comunicação com o mundo externo (teclado, tela, rede)

Esses componentes se comunicam através de **barramentos** (fios que transportam dados, endereços e sinais de controle).

### O Ciclo de Execução

Toda CPU opera em um ciclo contínuo chamado **fetch-decode-execute** (busca-decodifica-execução):

```
┌─────────────────────────────────────────┐
│            CICLO DE EXECUÇÃO             │
│                                          │
│  ┌──────────┐   ┌──────────┐   ┌───────┐│
│  │  FETCH   │──→│ DECODE   │──→│EXECUTE││
│  │  Busca   │   │ Decodif. │   │Executa││
│  └──────────┘   └──────────┘   └───┬───┘│
│       ↑                            │    │
│       └────────────────────────────┘    │
└─────────────────────────────────────────┘
```

1. **Fetch (Busca)**: a CPU lê a próxima instrução da memória, usando o **Program Counter** (PC) como endereço. O PC é incrementado automaticamente.
2. **Decode (Decodificação)**: a unidade de controle interpreta os bits da instrução — qual operação realizar, quais registradores usar, etc.
3. **Execute (Execução)**: a ALU realiza a operação (soma, comparação, load/store, etc.)

Esse ciclo repete **bilhões de vezes por segundo** (um processador de 4 GHz executa 4 bilhões de ciclos por segundo!).

> Processadores modernos são muito mais complexos (pipeline, execução fora de ordem, branch prediction), mas o modelo fetch-decode-execute ainda é o fundamento.

### Registradores

Registradores são a **memória mais rápida do computador** — ficam dentro da CPU e são acessados em um único ciclo de clock. Pense neles como "variáveis de altíssima velocidade".

Cada arquitetura tem seu próprio conjunto de registradores:

| Arquitetura | GPRs | Tamanho | Exemplos |
|---|---|---|---|
| x86-64 | 16 | 64 bits | RAX, RBX, RCX, RSP, RDI, R8...R15 |
| ARM64 | 31 | 64 bits | X0–X30, SP, XZR |
| RISC-V 64 | 32 | 64 bits | x0 (zero), x1 (ra), x2 (sp), a0–a7, s0–s11 |

Registradores têm funções específicas por convenção (ABI), mas arquiteturalmente a maioria pode ser usada para qualquer propósito. As convenções existem para que funções escritas por pessoas diferentes possam se comunicar.

### A Unidade Lógica e Aritmética (ALU)

A ALU é o "coração matemático" da CPU. Ela realiza operações como:

- **Aritméticas**: adição, subtração, multiplicação, divisão
- **Lógicas**: AND, OR, XOR, NOT
- **Deslocamento**: shift left, shift right
- **Comparação**: igual, maior, menor

Cada operação da ALU tipicamente:
1. Recebe um ou dois operandos (de registradores)
2. Realiza a operação
3. Armazena o resultado em um registrador

Em arquiteturas com flags (como x86), algumas instruções também atualizam flags de estado (zero, carry, overflow, etc.). Em arquiteturas como RISC-V, não existe registrador de flags; os branches comparam registradores diretamente.

Exemplo em x86-64:

```asm
mov rax, 10       ; rax = 10
add rax, 5        ; rax = 15   (ALU: adição)
sub rax, 3        ; rax = 12   (ALU: subtração)
cmp rax, 12       ; rax == 12? (ALU: comparação — seta flag ZF=1)
```

Em RISC-V, que não usa flags:

```asm
li a0, 10
addi a0, a0, 5    # a0 = 15
addi a0, a0, -3   # a0 = 12
li t0, 12
beq a0, t0, sao_iguais   # branch direto, sem flags

sao_iguais:
    # continua aqui se a0 == t0
```

### O Program Counter (PC)

O PC (também chamado IP — Instruction Pointer — no x86) é um registrador especial que aponta para a **próxima instrução** a ser executada. Toda vez que uma instrução é completada, o PC avança.

Saltos (jumps, branches) funcionam modificando o PC diretamente:

```asm
    mov rax, 1
    jmp .pular       ; PC pula para .pular
    mov rax, 2       ; ← esta linha NUNCA executa!
.pular:
    ; continua aqui
```

Instruções condicionais só modificam o PC se uma condição for verdadeira:

```asm
    cmp rax, 10
    je  .eh_dez      ; salta só se rax == 10
    ; se não for igual, continua aqui
```

### Clock e Frequência

O **clock** é o "batimento cardíaco" do processador. A cada pulso de clock, a CPU avança um passo no pipeline. A frequência (medida em GHz) determina quantos pulsos por segundo:

- **4 GHz** = 4 bilhões de pulsos por segundo
- Cada instrução pode levar 1 ou mais ciclos (dependendo da complexidade)
- Processadores modernos executam múltiplas instruções por ciclo (superescalar)

Mais GHz não significa necessariamente mais rápido — a eficiência da arquitetura (IPC — Instructions Per Cycle) é igualmente importante. Um ARM64 a 3 GHz pode superar um x86 a 4 GHz dependendo da carga de trabalho.

### Resumo

- A CPU opera em um ciclo contínuo: fetch → decode → execute
- Registradores são memória ultra-rápida dentro da CPU
- A ALU faz cálculos e comparações
- O PC aponta para a próxima instrução
- Saltos modificam o PC para alterar o fluxo do programa

Na próxima seção, vamos explorar a memória — onde instruções e dados vivem quando não estão nos registradores.
