Enquanto os registradores são a memória ultra-rápida dentro da CPU, a **memória principal (RAM)** é onde programas e dados realmente vivem. Em assembly, você gerencia a memória explicitamente — não há garbage collector, e não há alocação automática de variáveis locais pelo compilador; você ajusta stack e heap manualmente.

### Como a Memória é Organizada

A memória é um grande array de **bytes**, cada um com um endereço numérico único:

```
Endereço:  0x0000  0x0001  0x0002  0x0003  ...  0xFFFF
Conteúdo:  [ 48 ]  [ 65 ]  [ 6C ]  [ 6C ]  ...  [ 00 ]
              ↑       ↑       ↑       ↑
             'H'     'e'     'l'     'l'
```

Cada byte tem 8 bits e pode armazenar valores de 0 a 255 (0x00 a 0xFF). Bytes consecutivos podem ser agrupados em unidades maiores:

| Tamanho | Nome | Bits | Valor máximo | Exemplo de instrução |
|---------|------|------|-------------|---------------------|
| 1 byte | byte | 8 | 255 | `mov al, [addr]` |
| 2 bytes | word | 16 | 65.535 | `mov ax, [addr]` |
| 4 bytes | doubleword | 32 | 4,29 bilhões | `mov eax, [addr]` |
| 8 bytes | quadword | 64 | 1,8 × 10¹⁹ | `mov rax, [addr]` |

### Endereçamento de Memória

Em assembly, você acessa a memória especificando um endereço. Existem vários modos:

**Endereçamento Direto** — acesso a um endereço fixo:
```asm
mov rax, [minha_var]    ; carrega o valor no endereço 'minha_var'
mov [minha_var], 42     ; armazena 42 no endereço 'minha_var'
```

**Endereçamento Indireto** — acesso via registrador:
```asm
mov rax, [rbx]          ; carrega o valor no endereço apontado por RBX
mov [rbx], rax          ; armazena RAX no endereço apontado por RBX
```

**Endereçamento Base + Offset**:
```asm
mov rax, [rbx + 8]      ; carrega do endereço RBX + 8
mov rax, [rbx + rcx]    ; carrega do endereço RBX + RCX
```

### Seções de Memória de um Programa

Quando um programa assembly é carregado na memória pelo sistema operacional, ele é organizado em seções:

> Este é um modelo simplificado. O layout real varia conforme sistema operacional, loader, ASLR, bibliotecas compartilhadas, regiões `mmap`, guard pages e vDSO.

```
Endereços altos  ┌──────────────┐
                 │    Stack     │ ← cresce para baixo (variáveis locais, retornos)
                 ├──────────────┤
                 │      ↓       │
                 │  (espaço     │
                 │   livre)     │
                 │      ↑       │
                 ├──────────────┤
                 │    Heap      │ ← cresce para cima (alocação dinâmica)
                 ├──────────────┤
                 │    .bss      │ ← variáveis não inicializadas
                 ├──────────────┤
                 │   .data      │ ← variáveis inicializadas
                 ├──────────────┤
                 │  .rodata     │ ← constantes (somente leitura)
                 ├──────────────┤
Endereços baixos │   .text      │ ← código executável
                 └──────────────┘
```

- **.text**: contém as instruções do programa (código executável). Read-only + execute.
- **.rodata**: dados constantes (strings, tabelas). Read-only.
- **.data**: variáveis globais inicializadas. Read-write.
- **.bss**: variáveis globais não inicializadas. Read-write. Não ocupa espaço no executável.
- **Heap**: memória alocada dinamicamente (`malloc`/`brk`). Cresce para cima.
- **Stack**: variáveis locais, endereços de retorno, argumentos. Cresce para baixo.

### Stack (Pilha)

A stack é uma região de memória LIFO (Last In, First Out) gerenciada pelo **Stack Pointer (RSP/x2/SP)**. É usada para:

1. **Endereços de retorno**: quando você chama uma função, o endereço de volta é salvo na stack
2. **Variáveis locais**: espaço temporário para funções
3. **Passagem de argumentos**: argumentos extras que não cabem nos registradores
4. **Salvar registradores**: preservar valores entre chamadas de função

Exemplo de push/pop no x86-64:

```asm
push rax        ; RSP -= 8; mem[RSP] = RAX
push rbx        ; RSP -= 8; mem[RSP] = RBX
; ... usar RAX e RBX ...
pop rbx         ; RBX = mem[RSP]; RSP += 8
pop rax         ; RAX = mem[RSP]; RSP += 8
```

No RISC-V (sem push/pop nativo):

```asm
addi sp, sp, -16    # aloca 16 bytes na stack
sd ra, 8(sp)        # salva ra (return address)
sd s0, 0(sp)        # salva s0
; ... usar ra e s0 ...
ld s0, 0(sp)        # restaura s0
ld ra, 8(sp)        # restaura ra
addi sp, sp, 16     # libera a stack
```

### Endianness

**Endianness** define como bytes de um valor multi-byte são ordenados na memória:

**Little-endian** (x86, ARM64*, RISC-V*): o byte menos significativo vem primeiro.
```
Valor 0x12345678 (4 bytes)
Memória: [78] [56] [34] [12]
           ↑              ↑
    endereço baixo   endereço alto
```

**Big-endian** (alguns sistemas embarcados, rede): o byte mais significativo vem primeiro.
```
Valor 0x12345678 (4 bytes)
Memória: [12] [34] [56] [78]
```

> \* ARM64 e RISC-V operam em little-endian por padrão no Linux, mas suportam ambos.

Isso é importante ao trabalhar com dados binários e especialmente com **protocolos de rede** (que usam big-endian). É por isso que usamos `htons()` ao configurar portas de rede no nosso tutorial!

### Memória Virtual

Em sistemas operacionais modernos (Linux, Windows, macOS), cada processo tem seu próprio **espaço de endereço virtual**. Isso significa:

- O endereço `0x400000` no seu programa **não** corresponde ao endereço físico `0x400000` na RAM
- O hardware (MMU — Memory Management Unit) traduz endereços virtuais para físicos
- Cada processo vê um espaço de memória privado e isolado
- Tentar acessar um endereço inválido causa **segmentation fault** (SIGSEGV)

Para o programador assembly, a memória virtual é transparente — você sempre trabalha com endereços virtuais. O kernel e a MMU cuidam da tradução.

### Resumo

- A memória é um array gigante de bytes endereçáveis
- O programa é dividido em seções (.text, .data, .bss, stack, heap)
- A stack é uma estrutura LIFO gerenciada pelo Stack Pointer
- Endianness define a ordem dos bytes na memória
- Memória virtual isola processos e previne acesso indevido
