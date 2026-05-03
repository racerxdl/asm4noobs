ARM é a arquitetura RISC mais bem-sucedida do mundo — está em bilhões de dispositivos, de smartphones a servidores. Sua história é marcada por um modelo de negócios único e decisões de design acertadas.

### Acorn Computers e o Primeiro ARM (1983–1985)

Tudo começou na **Acorn Computers**, uma empresa britânica que fabricava microcomputadores educacionais (como o BBC Micro). Em 1983, a Acorn buscava um processador para sua próxima geração de máquinas, mas não encontrou nada adequado no mercado.

Sophie Wilson e Steve Furber projetaram o **ARM1** (Acorn RISC Machine) em 1985. Ele tinha:
- Arquitetura RISC limpa (influenciada pelo Berkeley RISC)
- **32 bits** com apenas 30.000 transistores (o 68000 da Motorola tinha 68.000)
- Execução condicional em quase toda instrução (para evitar branches)
- Barrel shifter integrado no datapath

O primeiro chip ARM consumia pouquíssima energia — uma característica que definiria a arquitetura.

### ARM Ltd e o Modelo de Licenciamento (1990)

Em 1990, a Acorn, Apple e VLSI Technology formaram a **ARM Ltd** (Advanced RISC Machines). A decisão crucial: a ARM **não fabricaria chips**. Em vez disso, licenciaria seus designs para outras empresas — um modelo de negócios radicalmente diferente da Intel e AMD.

Isso permitiu que fabricantes como Texas Instruments, Samsung e Qualcomm criassem processadores ARM personalizados para seus produtos. O sucesso foi explosivo.

### Evolução da Arquitetura

| Versão | Ano | Destaques |
|--------|-----|-----------|
| ARMv1–v3 | 1985–1993| Primeiros designs, 26-bit addressing |
| ARMv4 | 1996 | 32-bit completo, Thumb (instruções comprimidas de 16 bits) |
| ARMv5 | 1999 | DSP instructions, Jazelle (Java bytecode em hardware) |
| ARMv6 | 2002 | SIMD instructions, melhorias para embarcados |
| ARMv7 | 2005 | Cortex-A/R/M profiles, NEON SIMD |
| ARMv8 | 2011 | **AArch64** (execução 64-bit). 31 GPRs de 64 bits. Retrocompatível com AArch32. |
| ARMv9 | 2021 | SVE2 (Scalable Vector Extension), CCA (Confidential Compute), segurança melhorada |

### Dominação Mobile

O ARM dominou o mercado de dispositivos móveis por uma razão simples: **eficiência energética**. Smartphones precisam de processadores que consumam pouco, e a filosofia RISC do ARM (poucas instruções simples, pipeline eficiente) se provou ideal.

Processadores ARM estão em:
- **Smartphones**: praticamente 100% do mercado (Apple A-series, Qualcomm Snapdragon, Samsung Exynos)
- **Tablets**: iPad, Galaxy Tab, etc.
- **Embedded**: roteadores, smart TVs, microcontroladores (Cortex-M)
- **IoT**: sensores, wearables, dispositivos inteligentes

### Apple Silicon: A Transição do Mac

Em 2020, a Apple anunciou a transição dos Macs de Intel para processadores ARM próprios (Apple M1). Foi um movimento sísmico na indústria que provou que ARM tem performance competitiva até no mercado de desktops e laptops.

O M1 e seus sucessores (M2, M3, M4) mostram que um design ARM bem-feito pode competir de igual para igual — e frequentemente superar — em performance por watt.

### ARM64 no Datacenter

A ARM também está conquistando servidores:
- **AWS Graviton** (baseado em ARM Neoverse): servidores cloud com excelente custo/performance
- **Ampere Altra**: até 128 núcleos ARM64 para datacenters
- **NVIDIA Grace**: CPU ARM64 para HPC e IA
- **Google Axion**: processadores ARM customizados para Google Cloud

### Raspberry Pi e a Democratização

O **Raspberry Pi** popularizou o ARM entre hobbistas e educadores. Milhões de pessoas tiveram seu primeiro contato com arquitetura ARM através desses pequenos computadores de placa única, que rodam Linux nativo em processadores ARM (originalmente ARMv6, hoje ARMv8 64-bit).

É por isso que escolhemos o Raspberry Pi como referência para este tutorial!

### Por que aprender ARM64?

- É a arquitetura do **seu smartphone** (e provavelmente do seu próximo laptop)
- **Cresce nos servidores**: AWS, Azure, Google Cloud, Oracle Cloud
- **Design limpo** (RISC) — mais fácil de aprender conceitos fundamentais
- **Futuro**: com Apple Silicon, RISC-V e ARM no datacenter, arquiteturas não-x86 são o presente e o futuro
