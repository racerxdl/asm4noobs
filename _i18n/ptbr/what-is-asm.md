Assembly é a linguagem de programação mais próxima do hardware. Enquanto linguagens como Python ou JavaScript são traduzidas por compiladores e interpretadores através de várias camadas de abstração, assembly fala diretamente com o processador.

### O que é Assembly?

Assembly é uma representação textual das **instruções de máquina** — os códigos binários que o processador entende. Cada instrução assembly corresponde (quase) diretamente a uma instrução de máquina:

```asm
mov rax, 42       ; ← assembly (texto legível)
;  ↓ assembler traduz para ↓
; 48 C7 C0 2A 00 00 00   ← código de máquina (bytes)
```

O programa que faz essa tradução é chamado de **assembler** (ou montador). No nosso tutorial usamos dois:
- **NASM** (Netwide Assembler) para x86
- **GNU as** (GNU Assembler) para ARM64 e RISC-V

### Por que aprender Assembly?

1. **Entender o computador de verdade**: você descobre exatamente o que acontece quando seu programa roda — cada instrução, cada acesso à memória, cada chamada de sistema
2. **Performance extrema**: assembly permite otimizações impossíveis em linguagens de alto nível (embora raramente necessário com compiladores modernos)
3. **Engenharia reversa e segurança**: entender assembly é essencial para analisar malware, explorar vulnerabilidades e fazer debugging de binários
4. **Sistemas embarcados e bare-metal**: programar microcontroladores e kernels frequentemente requer assembly
5. **Fundamento sólido**: depois de assembly, qualquer linguagem de programação faz mais sentido — você entende o "porquê" por trás das abstrações

### Assembly vs Linguagens de Alto Nível

| | Assembly | C | Python |
|---|---|---|---|
| Abstração | Nenhuma | Baixa | Alta |
| Performance | Máxima (teórica) | Muito alta | Moderada |
| Portabilidade | Nenhuma (específico da arquitetura) | Alta (com recompilação) | Máxima |
| Produtividade | Baixíssima | Moderada | Altíssima |
| Controle de hardware | Total | Quase total | Nenhum |
| Quantidade de código | Muita | Média | Pouca |

### Arquiteturas Diferentes, Assembly Diferente

Assembly não é uma linguagem única — cada arquitetura de processador tem seu próprio "dialeto":

| Arquitetura | Exemplo de instrução | Significado |
|---|---|---|
| x86-64 | `mov rax, 60` | Mover 60 para RAX |
| ARM64 | `mov x0, #93` | Mover 93 para X0 |
| RISC-V | `li a7, 93` | Carregar 93 em A7 |

Três instruções completamente diferentes que fazem a mesma coisa: colocar um valor em um registrador. A sintaxe, os nomes dos registradores e até a filosofia de design mudam, mas os conceitos fundamentais são universais.

### Abstrações que Você Perde

Quando programa em assembly, você perde todas as conveniências das linguagens modernas:

- **Sem variáveis de alto nível**: você usa registradores, labels e endereços de memória, sem tipos e escopos automáticos
- **Sem tipos**: tudo são bytes — você decide se um valor é inteiro, caractere ou ponteiro
- **Sem controle de fluxo estruturado**: sem `if/else`, `for`, `while` — apenas saltos condicionais (`jump if zero`, `branch if equal`)
- **Sem funções com escopo**: funções são apenas labels + convenções de chamada manuais
- **Sem gerenciamento automático de memória**: você aloca stack e heap manualmente

Parece assustador? É. Mas também é libertador: você entende **tudo** que está acontecendo. Não há "mágica".

### Tipos de Assembly

Existem dois estilos principais de sintaxe:

**Sintaxe Intel** (usada pelo NASM, comum no Windows e neste tutorial):
```asm
mov rax, 60        ; destino, origem
```

**Sintaxe AT&T** (usada pelo GNU as em modo tradicional, comum no Linux):
```asm
movq $60, %rax     ; origem, destino (ordem invertida!)
```

Neste tutorial usamos sintaxe Intel com NASM para x86, e a sintaxe natural do GNU as para ARM64 e RISC-V.

### Nosso Primeiro Programa

Mesmo sem entender todos os detalhes ainda, vamos olhar para um programa assembly completo:

```asm
section .data
    msg: db "Ola, mundo!", 10      ; string + newline

section .text
    global _start

_start:
    ; Escrever msg no terminal
    mov rax, 1          ; syscall write
    mov rdi, 1          ; stdout
    mov rsi, msg        ; ponteiro da mensagem
    mov rdx, 12         ; tamanho
    syscall             ; chama o kernel

    ; Sair do programa
    mov rax, 60         ; syscall exit
    mov rdi, 0          ; status 0
    syscall
```

Isso é um programa real que você pode compilar com NASM e executar no Linux! Cada linha será explicada em detalhes ao longo do tutorial.

### Resumo

- Assembly é a representação legível do código de máquina do processador
- Cada arquitetura (x86, ARM, RISC-V) tem seu próprio assembly
- Programar em assembly significa controle total — mas sem nenhuma abstração
- O assembler traduz texto assembly para código de máquina binário
- Assembly é a base para entender como computadores realmente funcionam
