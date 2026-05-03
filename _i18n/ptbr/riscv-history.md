RISC-V é a arquitetura mais nova entre as que estudamos — e a única que é completamente **aberta e gratuita**. Sua história reflete uma mudança fundamental na indústria de semicondutores.

### Origem Acadêmica (2010)

O RISC-V nasceu na **UC Berkeley** em 2010, liderado por Krste Asanović, David Patterson e Andrew Waterman. O projeto começou como uma ISA para pesquisa e ensino, já que as alternativas existentes tinham problemas:

- **x86**: proprietário, impossível de usar sem licença da Intel/AMD
- **ARM**: requer licenciamento caro (mesmo para uso acadêmico)
- **MIPS**: tinha licenças disponíveis, mas a arquitetura estava estagnada
- **SPARC**: aberto, mas pouco adotado fora de nichos

A equipe decidiu criar uma ISA limpa, modular e **livre de royalties** desde o primeiro dia. O nome "RISC-V" (pronuncia-se "risk-five") vem de ser a quinta geração de projetos RISC de Berkeley (RISC-I a RISC-V).

### Fundação e Padronização

| Ano | Marco |
|-----|-------|
| 2010 | Início do projeto na UC Berkeley |
| 2011 | Primeiro chip RISC-V (Raven-1) fabricado |
| 2014 | Primeira conferência RISC-V Workshop |
| 2015 | **RISC-V Foundation** criada |
| 2019 | Ratificação da ISA base (RV32I/RV64I) e extensões principais |
| 2020 | RISC-V Foundation vira **RISC-V International** (sede na Suíça) |
| 2022–24 | Ratificação de Vector (RVV), Hypervisor, Crypto e outras extensões |

A RISC-V International hoje tem mais de **4.000 membros** em 70+ países, incluindo Google, NVIDIA, Qualcomm, Samsung, Intel, AMD, Western Digital, Alibaba e Huawei.

### Modelo de Extensões Modulares

Diferente de outras ISAs que são monolíticas, o RISC-V é **modular**:

- **Base**: RV32I (32-bit integer), RV64I (64-bit integer), RV128I (128-bit integer — especificação existe, mas sem implementação real)
- **Extensões padrão**: letras que você adiciona à base:
  - **M**: multiplicação e divisão inteira
  - **A**: instruções atômicas
  - **F**: ponto flutuante de precisão simples
  - **D**: ponto flutuante de precisão dupla
  - **C**: instruções comprimidas (16 bits)
  - **V**: vetores (SIMD escalável)
  - **B**: manipulação de bits
  - **H**: suporte a hypervisor

Uma configuração comum para Linux é **RV64GC** (também chamada RV64IMAFDC), que inclui base + integer mul/div + atomics + float + double + compressed. É a que usamos no nosso tutorial!

### Adoção pela Indústria

O RISC-V está sendo adotado em ritmo acelerado:

- **Microcontroladores**: ESP32-C3/C6 (Espressif), GD32V (GigaDevice), WCH — milhões de unidades vendidas
- **Armazenamento**: Western Digital anunciou transição para RISC-V em todos seus controladores
- **IA e Aceleração**: NVIDIA usa RISC-V em GPUs (controladores internos), Google tem TPUs com RISC-V
- **Servidores**: Ventana, Rivos, Tenstorrent — chips de datacenter RISC-V em desenvolvimento
- **Space**: NASA e ESA usando RISC-V em missões espaciais (tolerância a radiação)
- **Automotivo**: Renesas, Mobileye — RISC-V em ECUs e sistemas embarcados
- **Desktop**: SiFive HiFive, StarFive VisionFive 2 — computadores RISC-V rodando Linux desktop
- **China e Índia**: adotando RISC-V como ISA nacional para independência tecnológica

### Por que RISC-V é Importante?

1. **Sem royalties**: qualquer um pode implementar RISC-V sem pagar licenças — democratizando o design de processadores
2. **Design moderno**: sem décadas de compatibilidade retroativa, a ISA é limpa e ortogonal
3. **Modular**: você pode implementar só o que precisa (de um microcontrolador RV32I até um supercomputador RV64GCV)
4. **Segurança**: ISA aberta permite auditoria independente (sem backdoors proprietários)
5. **Ensino**: ideal para aprender arquitetura de computadores — muitos cursos universitários migraram para RISC-V

### O Futuro

Analistas projetam que RISC-V pode representar **25% do mercado de processadores até 2030**. Com a China investindo pesadamente como alternativa ao x86/ARM, a União Europeia financiando projetos de HPC com RISC-V, e a Índia usando RISC-V em sua estratégia de semicondutores, o crescimento é inevitável.

Aprender RISC-V hoje é como aprender Linux nos anos 90 — você está na frente da curva.
