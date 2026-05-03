A arquitetura x86 é a mais antiga ainda em uso ativo nos computadores pessoais — e carrega décadas de evolução e compatibilidade retroativa. Entender sua história ajuda a entender suas "esquisitices".

### Intel 8086 (1978)

O x86 nasceu com o **Intel 8086**, um processador de 16 bits lançado em 1978. Ele foi escolhido pela IBM para o IBM PC em 1981, criando o padrão que dominaria o mercado por décadas.

Características do 8086:
- **16 bits**: registradores de 16 bits (AX, BX, CX, DX, SI, DI, BP, SP)
- **Barramento de endereço de 20 bits**: até 1 MB de memória endereçável
- **Segmentação**: memória acessada via `segmento:offset` (ex: CS:IP, DS:DX)
- Registradores de segmento: CS (código), DS (dados), SS (stack), ES (extra)

O 8088, uma versão com barramento externo de 8 bits, foi o escolhido para o IBM PC original por ser mais barato.

> A segmentação do 8086 é a origem de várias limitações e "gambiarras" históricas que ainda afetam o x86 moderno!

### 80286 (1982)

O **Intel 286** introduziu o **modo protegido**, permitindo acesso a até 16 MB de memória e proteção entre processos. Porém, a transição entre modo real (compatível com 8086) e modo protegido era complicada e pouco usada no MS-DOS.

### 80386 (1985) — A Revolução

O **Intel 386** foi um marco. Ele trouxe:
- **Arquitetura de 32 bits**: registradores estendidos para 32 bits (EAX, EBX, etc.)
- **Modo protegido completo**: com paginação e memória virtual
- **Modo Virtual 8086**: permitindo rodar programas DOS em janelas dentro de sistemas multitarefa
- Conjunto de instruções muito expandido

Foi o 386 que tornou viáveis sistemas como Windows, OS/2 e Linux no PC. Ele estabeleceu a base que usamos até hoje — o "i386" ainda é referenciado em kernels e compiladores.

### 80486 (1989)

O **Intel 486** integrou o coprocessador matemático (FPU) no mesmo chip (antes era um chip separado, o 80387) e adicionou cache L1 interno. O desempenho deu um salto.

### Pentium (1993)

O **Pentium** (que seria o 586, mas a Intel mudou a nomenclatura por questões de marca) introduziu:
- **Arquitetura superescalar**: duas instruções por ciclo de clock
- **Pipeline de 5 estágios**
- **MMX** (a partir do Pentium MMX): 8 registradores de 64 bits para SIMD (Single Instruction, Multiple Data), compartilhados com a FPU

### Pentium Pro / II / III

- **Pentium Pro (1995)**: execução fora de ordem (out-of-order), tradução de instruções x86 para micro-operações internas (µops)
- **Pentium II (1997)**: MMX melhorado
- **Pentium III (1999)**: introdução do **SSE** (Streaming SIMD Extensions) — 8 registradores XMM de 128 bits, operações de ponto flutuante SIMD

### AMD64 (2003) — A Extensão de 64 bits

Enquanto a Intel apostava no Itanium (IA-64, uma arquitetura completamente nova e incompatível), a **AMD** criou o **AMD64** (também chamado x86-64 ou x64):

- Registradores estendidos para 64 bits (RAX, RBX, etc.)
- **8 novos registradores**: R8 a R15
- Modo de compatibilidade para rodar código 32 bits nativamente
- O modo de 64 bits é chamado de **long mode**

A Intel acabou adotando o AMD64 sob o nome **Intel 64**. Hoje, todo processador x86 de PC usa essa extensão.

### Era Moderna

- **Core 2 (2006)**: nova microarquitetura Intel, múltiplos núcleos
- **SSE2/SSE3/SSE4**: mais instruções SIMD
- **AVX (2011)**: registradores YMM de 256 bits (Sandy Bridge)
- **AVX2 (2013)**: operações inteiras SIMD de 256 bits (Haswell)
- **AVX-512 (2016)**: registradores ZMM de 512 bits, 32 registradores (Skylake-X)

### Por que o x86 é "estranho"?

Comparado com arquiteturas RISC modernas, o x86 tem características herdadas de 40+ anos de evolução:

- **Instruções de tamanho variável** (1 a 15 bytes) — difícil de decodificar
- **Poucos registradores** (apenas 16 GPRs em 64 bits) — comparado com 32 do ARM64 ou RISC-V
- **Registradores com nomes não ortogonais**: AL/AH/AX/EAX/RAX são todos partes do mesmo registrador
- **Instruções complexas** que fazem várias operações em uma só (ex: `rep movsb`, `loop`)
- **Flags condicionais** implícitas após quase toda operação

Apesar disso, o x86 sobreviveu e prosperou por causa da **compatibilidade retroativa**: a ISA ainda preserva os mecanismos necessários para executar software antigo, embora sistemas modernos normalmente usem emulação, virtualização ou modos específicos para rodar programas DOS. Essa é uma façanha de engenharia sem paralelo.
