Vamos conhecer a estrutura interna de um processador x86-64 moderno, focando no que é visível para o programador em assembly.

### Registradores de Uso Geral (GPRs)

O x86-64 tem **16 registradores de uso geral** de 64 bits:

| 64 bits | 32 bits | 16 bits | 8 bits (baixo) | 8 bits (alto)* | Função típica |
|---------|---------|---------|-----------------|-----------------|---------------|
| RAX | EAX | AX | AL | AH | Acumulador / retorno de função |
| RBX | EBX | BX | BL | BH | Base (preservado entre chamadas) |
| RCX | ECX | CX | CL | CH | Contador (loops) |
| RDX | EDX | DX | DL | DH | Dados / extensão de RAX |
| RSI | ESI | SI | SIL | — | Source Index (origem em operações de string) |
| RDI | EDI | DI | DIL | — | Destination Index (destino) |
| RBP | EBP | BP | BPL | — | Base Pointer (frame pointer) |
| RSP | ESP | SP | SPL | — | Stack Pointer |
| R8 | R8D | R8W | R8B | — | Uso geral (adicionados no AMD64) |
| R9 | R9D | R9W | R9B | — | Uso geral |
| R10 | R10D | R10W | R10B | — | Uso geral |
| R11 | R11D | R11W | R11B | — | Uso geral |
| R12 | R12D | R12W | R12B | — | Uso geral (preservado) |
| R13 | R13D | R13W | R13B | — | Uso geral (preservado) |
| R14 | R14D | R14W | R14B | — | Uso geral (preservado) |
| R15 | R15D | R15W | R15B | — | Uso geral (preservado) |

> \* Os nomes AH, BH, CH, DH acessam o byte alto (bits 15-8) dos registradores AX, BX, CX, DX. Não estão disponíveis para R8-R15.

Acessar partes menores de um registrador **não zera** os bits superiores, com exceção de operações de 32 bits (que zeram automaticamente os 32 bits superiores do registrador de 64 bits correspondente).

### Registradores Especiais

- **RIP** (Instruction Pointer): aponta para a próxima instrução a ser executada. Não é acessível diretamente (não pode fazer `mov rax, rip`).
- **RFLAGS**: registrador de flags com bits de estado (Zero, Carry, Sign, Overflow, etc.) e controle (Interrupt, Direction, etc.).
- **Registradores de segmento** (CS, DS, SS, ES, FS, GS): remanescentes da era 8086. Em modo 64 bits, apenas FS e GS são usados na prática (para thread-local storage e acesso a estruturas do sistema).

### Modos de Operação

O x86-64 pode operar em vários modos, herdados de sua evolução:

| Modo | Bits | Descrição |
|------|------|-----------|
| Real mode | 16 | Compatível com 8086. Como o processador inicia. |
| Protected mode | 32 | Modo com paginação, proteção, multitarefa. |
| Long mode | 64 | Modo nativo de 64 bits (AMD64). |
| Compatibility mode | 32 | Submodo do long mode para rodar código 32 bits. |

Processadores modernos iniciam em real mode (16 bits) por compatibilidade. O bootloader/UEFI faz a transição para protected mode, depois para long mode. Como programadores de aplicação em Linux, nosso código sempre roda em **long mode** (64 bits).

### Registradores SIMD

Além dos GPRs, o x86 moderno tem conjuntos de registradores para operações SIMD (uma instrução, múltiplos dados):

| Conjunto | Registradores | Largura | Introdução |
|----------|--------------|---------|------------|
| MMX | mm0–mm7 | 64 bits | Pentium MMX |
| SSE / XMM | xmm0–xmm15 | 128 bits | Pentium III / AMD64 |
| AVX / YMM | ymm0–ymm15 | 256 bits | Sandy Bridge |
| AVX-512 / ZMM | até zmm0–zmm31 | 512 bits | Skylake-X |

Os registradores MMX são mapeados nos registradores da FPU (x87), então não podem ser usados simultaneamente. Os XMM/YMM/ZMM são independentes e podem conter múltiplos inteiros ou floats. AVX-512 não está presente em todos os processadores x86 modernos; quando disponível e habilitado pelo sistema operacional em modo 64 bits, pode expor até 32 registradores ZMM.

### Pipeline e Microarquitetura

Internamente, processadores x86 modernos são muito diferentes do que as instruções sugerem:

1. **Busca** (fetch): instruções x86 de tamanho variável são lidas da memória
2. **Decodificação**: instruções x86 complexas são quebradas em **micro-operações** (µops), que são operações simples no estilo RISC
3. **Renomeação de registradores**: os poucos registradores x86 são mapeados para um arquivo de registradores físico muito maior
4. **Execução fora de ordem**: µops são reordenadas para maximizar paralelismo
5. **Execução especulativa**: branch predictor decide qual caminho executar antes da condição ser resolvida
6. **Aposentadoria** (retirement): µops são confirmadas em ordem

Para o programador assembly, essa complexidade é invisível — você escreve instruções x86 e o processador faz a "mágica" internamente.

### Paginação e Memória Virtual

Em long mode, o x86-64 usa paginação de 4 níveis (recentemente 5 níveis, com extensão LA57):

- Cada processo vê um espaço de endereço virtual privado
- O hardware traduz endereços virtuais para físicos via tabelas de página
- Tamanho de página típico: 4 KB (também suporta 2 MB e 1 GB com huge pages)
- Endereço virtual em 64 bits: na prática, apenas 48 bits são usados (256 TB), com extensão para 57 bits

Como programador de aplicação em Linux, você não precisa gerenciar paginação manualmente — o kernel faz isso. Mas é útil saber que seu programa não acessa a memória física diretamente.

### Convenção de Chamada (Linux x86-64)

A System V AMD64 ABI (usada no Linux) define:

- Argumentos: RDI, RSI, RDX, RCX, R8, R9 (os demais na stack)
- Retorno: RAX (e RDX se precisar de 128 bits)
- Preservados pela função chamada: RBX, RBP, R12–R15
- Stack deve ser alinhada em 16 bytes antes de cada `call`
- **Red zone**: 128 bytes abaixo de RSP que podem ser usados sem ajustar RSP (apenas em leaf functions)

Essa convenção é a que usamos em todo o tutorial!
