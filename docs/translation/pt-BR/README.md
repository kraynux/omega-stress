<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licença MIT (ver o arquivo LICENSE) -->
<div align="center">
  <img src="../../assets/omega-stress.png" alt="Omega-Stress" width="384">
</div>

# 🗲 OMEGA-STRESS

**Estação de testes de carga HTTP controlados**

> Desenvolvido por [kraynux](https://github.com/kraynux) para [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Página oficial: [OMEGA-STRESS](https://kraynux.snake-mackarel.ts.net/omega-stress/) &nbsp; Capturas de tela: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-stress/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interface e relatórios exportados disponíveis em **17 idiomas** — veja [Idiomas da interface](#idiomas-da-interface).  
**Idiomas:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)



**Omega-Stress** é uma aplicação local de terminal (TUI [Textual](https://github.com/Textualize/textual) + CLI scriptável) que conduz testes de carga HTTP de forma controlada e reutilizável: perfis congelados, histórico, reexecução, exportações detalhadas (JSON/CSV/HTML), limites de segurança explícitos.

O projeto segue os princípios da **Clean Architecture**, com uma separação clara entre domínio de negócio, orquestração, infraestrutura e interface do usuário.
---

## Sumário

- [Apresentação](#apresentação)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Uso](#execução)
- [Perfis de duração D1-D6](#perfis-de-duração-d1-d6-modo-perfil)
- [Modo segurança](#modo-segurança)
- [Calibração local](#calibração-local)
- [Configuração](#configuração)
- [Testes e qualidade](#testes-e-qualidade)
- [Desinstalação](#desinstalação)
- [Limitações conhecidas](#limitações-conhecidas)
- [Licença](#licença)

## Apresentação

### Objetivos

## O que o Omega-Stress faz (alvo V1)

- Três famílias de teste controladas: **Teste de requisições** (vazão), **Teste de conexões** (simultaneidade), **Teste de carga** (subida progressiva).
- **8 níveis de intensidade** (Fraco/Baixo/Médio/Alto/Potente/Agressivo/Violento/Máximo), com um modelo de pré-check em 3 degraus (nunca exigido / exigido opcional / exigido obrigatório — veja [Valores dos testes](#valores-dos-testes)).
- **Dois modos de duração**: manual (de 1 a 5 min, limitado por nível) ou **perfil nomeado D1-D6** (duração total fixa com aquecimento/rampa/platô/retorno à calma — veja [Perfis de duração D1-D6](#perfis-de-duração-d1-d6-modo-perfil)).
- **Modo segurança** (ativo por padrão, desativável a cada execução): salvaguardas locais de CPU/memória da máquina hospedeira, distintas dos limites que protegem o alvo testado — veja [Modo segurança](#modo-segurança).
- **Calibração local persistente**: mede a capacidade real da máquina hospedeira (nunca do alvo) por meio de um servidor de loopback local, em degraus de carga crescente — veja [Calibração local](#calibração-local).
- Perfis congelados, reutilizáveis e registrados no histórico — **opcionais**: um teste roda igualmente bem em modo manual, sem nenhum perfil, escolhendo ou digitando diretamente um alvo.
- Confirmação explícita de autorização obrigatória antes de qualquer execução em um alvo não fixado.
- Limites de parada automática, nunca uma carga sem limites.
- Exportações JSON/CSV/HTML detalhadas (degraus, métricas por intervalo, veredito, diagnóstico).
- Modo CLI não interativo para automação (cron, CI), chamando exatamente os mesmos casos de uso da TUI.
- Adaptação automática ao terminal (tema + perfil de renderização degradável).

## O que o projeto não faz

- Não substitui uma ferramenta de varredura de rede — vocabulário e postura do produto assumidos como «teste de carga», nunca «varredura».
- Não implementa nenhum motor de carga externo (k6 etc.) — geração nativa `httpx`/asyncio.
- Não inicia nenhuma execução sem limites nem confirmação de autorização.
- Não é uma ferramenta de carga distribuída: a geração roda em uma única máquina, em um único processo — veja [Limitações conhecidas](#limitações-conhecidas).

## Funcionalidades

- **Três famílias de teste**, cada uma com 8 níveis de intensidade (Fraco/Baixo/Médio/Alto/Potente/Agressivo/Violento/Máximo) — veja a tabela [Referências de carga](#valores-dos-testes) para os valores exatos de cada nível.
- **Perfis de teste congelados**: nome, alvo, família, intensidade, duração, limite de erro — criados uma vez e reexecutados de forma idêntica pela TUI ou pela CLI.
- **Perfis de duração nomeados D1-D6** (modo «perfil»), alternativa ao modo manual: uma duração total fixa (de 1 a 120 min) com aquecimento/rampa/platô/retorno à calma, que também limita os níveis acessíveis — veja [Perfis de duração D1-D6](#perfis-de-duração-d1-d6-modo-perfil).
- **Modo segurança**, marcado por padrão em cada tela de execução: interrompe um teste se a máquina hospedeira (não o alvo) parecer em perigo. Desativável com conhecimento de causa, com um lembrete comparando o nível escolhido com a última calibração feita — veja [Modo segurança](#modo-segurança).
- **Calibração local persistente**: mede o que a máquina realmente aguenta (7 degraus de carga crescente contra um servidor de loopback local embutido), consultável pela tela Calibração — veja [Calibração local](#calibração-local).
- **Alvos fixados**: um endereço fixado dispensa marcar a autorização a cada execução; os alvos recentes não fixados continuam visíveis (10 no máximo) sem autorização implícita. Um alvo fixado pode ser usado de duas formas independentes: diretamente, para iniciar um teste em modo manual sem nenhum perfil, ou como alvo padrão ao criar um perfil congelado.
- **Histórico completo**: cada execução é registrada (veredito, métricas, cronologia por intervalo, modo segurança usado); uma execução ligada a um perfil congelado pode ser repetida de forma idêntica.
- **Exportações detalhadas** em JSON (dados brutos reimportáveis), CSV (análise tabular) ou HTML (relatório legível, com tema à escolha entre as 10 paletas do projeto). O relatório HTML é escrito no idioma escolhido em Configurações («Idioma das exportações», por padrão o da interface); JSON e CSV continuam sendo dados, não traduzidos.
- **Pré-check** automático e obrigatório antes de qualquer teste Violento/Máximo, opcional (mas liberando durações adicionais) em Potente/Agressivo, com janela de validade (24 h).
- **Acompanhamento ao vivo** de um teste em andamento: indicador de progresso com contagem regressiva confiável (tempo restante calculado diretamente, nunca estimado), vazão/erros/latência p95 atualizados a cada intervalo, parada manual possível sem sair da aplicação.
- **Configurações centralizadas**: tema (10 paletas Omega + todos os temas embutidos do Textual, 31 no total pela paleta de comandos), perfil de renderização (automático ou forçado), pastas de exportação e de captura de tela, limpeza dos alvos/do histórico.
- **Ajuda integrada** (tecla `a`): atalhos de teclado, descrição de cada tela (incluindo Calibração e Modo segurança), tabela de referência dos valores de carga e tabela dos perfis de duração D1-D6.
- **CLI scriptável** (`omega-stress profile|run|history|export|calibrate ...`), exatamente os mesmos casos de uso da TUI, com saída `--json` disponível para automação.
- **Adaptação automática ao terminal**: família e tamanho detectados na inicialização, tema e riqueza de exibição ajustados de acordo (veja [Terminais compatíveis](#terminais-compatíveis)).

## Arquitetura

Clean Architecture + Ports & Adapters em 9 pacotes (`app/`, `core/`, `domain/`, `application/`, `ports/`, `infrastructure/`, `interfaces/`, `plugins/`, `shared/`).
Detalhe completo: `ARCHITECTURE.md`.

```text
src/omega_stress/
├── app/              Inicialização e contêiner de injeção de dependências (ligação manual, sem framework de DI)
├── core/             Vocabulário transversal: enumerações, exceções raiz, Result/Ok/Err, capacidades do sistema
├── domain/           Lógica de negócio pura: carga, perfis, execuções, alvos, temas, terminal — sem E/S
├── application/      Orquestração: commands (ações), queries (leituras), pipeline de execução (guards/hooks)
├── ports/            Contratos Protocol/ABC esperados pelos adaptadores (repositórios, exportadores, gerador de carga...)
├── infrastructure/   Implementações concretas: SQLite, exportadores JSON/CSV/HTML, gerador httpx/asyncio, detecção do terminal, sonda do sistema
├── interfaces/       Dois adaptadores de apresentação independentes: TUI (Textual) e CLI (argparse)
├── plugins/          Ponto de extensão reservado (carregamento de plugins) — estrutura presente, não implementada na V1
└── shared/           Utilitários transversais sem dependência de negócio (relógio injetável, geração de identificadores)
```

### Princípios de design

- `domain/` não contém nem E/S nem dependência da infraestrutura — lógica de negócio pura, totalmente testável sem mocks.
- `application/` orquestra os casos de uso por meio do domínio e das portas, nunca diretamente com uma classe concreta de `infrastructure/`.
- `infrastructure/` implementa as portas sem nunca ser importada diretamente por `application/` ou `domain/` — só `interfaces/` e `app/` a referenciam.
- `interfaces/` nunca deve chamar `infrastructure/` diretamente nem `subprocess`: apenas por meio de `application/` (commands/queries) e de seus próprios controllers.
- `ports/` define os contratos esperados pelos adaptadores (Protocol), nunca uma implementação.
- `core/` reúne o vocabulário comum a todas as camadas, sem nunca codificar uma regra de negócio com números (limites, durações, presets — sempre em `domain/*/policies.py`).

A Dependency Rule (somente das camadas externas para as internas) e o isolamento das tecnologias de terceiros (`textual`, `sqlite3`, `httpx`, `jinja2`, cada uma restrita ao seu ponto de entrada designado) são verificados automaticamente a cada execução de `lint-imports` (veja [Testes e qualidade](#testes-e-qualidade)).

## Pré-requisitos

- Python ≥ 3.10
- [`uv`](https://github.com/astral-sh/uv) recomendado para gerenciar as dependências (senão, `pip` padrão)

### Sistema

- Linux, de preferência Arch Linux e distribuições compatíveis.
- Python 3.10 ou superior.
- Nenhum privilégio de root necessário: o Omega-Stress só faz chamadas HTTP de saída como usuário comum.

## Instalação

O arquivo oficial é distribuído no formato `.tar.gz`. Verifique sua integridade antes de instalar:

```bash
sha256sum omega-stress.tar.gz
```

### Método 1 — script de instalação

```bash
[ -d omega-stress ] && echo "ℹ️ Já extraído aqui, etapa ignorada." || tar -xzf omega-stress.tar.gz
[ -d ~/omega-stress ] && echo "ℹ️ ~/omega-stress já existe, movimentação ignorada." || mv omega-stress ~/
cd ~/omega-stress/
chmod +x install.sh
./install.sh
```

### Método 2 — instalação completa resiliente

Este comando pode ser copiado e colado tal como está e executado de novo sem erro: cada etapa ignora o que já foi feito.

```bash
( [ -d omega-stress ] || tar -xzf omega-stress.tar.gz ) && \
( [ -d ~/omega-stress ] || mv omega-stress ~/ ) && \
cd ~/omega-stress && chmod +x install.sh && ./install.sh
```
`install.sh`:

1. Cria o ambiente virtual `.venv` se ele ainda não existir.
2. Instala as dependências (`pip install -e .`; `pyproject.toml` continua sendo a única fonte de verdade).
3. Torna `omega-stress.sh` e `install.sh` executáveis.
4. Adiciona o alias `stress` a `~/.bashrc` e `~/.zshrc` (sem duplicar se já existir).

## Instalação (desenvolvimento)

```bash
uv sync --all-extras
# ou, sem uv:
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```


### Execução

```bash
cd ~/omega-stress
./omega-stress.sh

# ou simplesmente digite "stress" em um novo terminal se o alias tiver sido criado
```

O inicializador:

1. Detecta `.venv`, `venv` ou o Python do sistema.
2. Configura `PYTHONPATH` para `src/`.
3. Executa `python -m omega_stress` — sem argumento, abre a TUI; com um argumento, encaminha para a CLI.

### Idiomas da interface

A interface está disponível em 17 idiomas: francês, inglês, espanhol, português (Brasil), italiano, alemão, holandês, polonês, russo, chinês simplificado, vietnamita, tailandês, indonésio, japonês, coreano, hindi e árabe. A escolha é feita em Configurações («Langue / Language») e vale após reiniciar a interface; a variável `OMEGA_STRESS_LANG` (por exemplo `OMEGA_STRESS_LANG=pt-BR ./omega-stress.sh`) força um idioma durante uma sessão. Iniciado pelo omega-suite, o omega-stress usa o idioma da suíte. Em um console de texto Linux (TTY), os idiomas de escrita não latina aparecem em inglês durante a sessão. A linha de comando continua em francês.

### Uso pela CLI

```bash
omega-stress profile list                                     # listar os perfis
omega-stress profile create --name "Sondagem API" --target-id t-1 \
    --family request --level bas --duration-minutes 1 --max-error-rate 0.05
omega-stress profile freeze <profile-id>                       # congelar um perfil

# Pré-check obrigatório antes de qualquer execução Violento/Máximo (opcional em Potente/Agressivo)
omega-stress run precheck --target-id t-1 --target-url https://exemple.org --confirm

omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level bas --duration-minutes 1 --max-error-rate 0.05 --confirm
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level moyen --duration-minutes 3 --max-error-rate 0.05 --confirm
omega-stress run ramp --target-id t-1 --target-url https://exemple.org \
    --level puissant --duration-minutes 3 --max-error-rate 0.05 --confirm --precheck-validated

# Modo perfil D1-D6, em vez de --duration-minutes (mutuamente exclusivos)
# D4 (resilience) permite Agressivo sem condição e Violento com confirmação reforçada
omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-preset d4 --max-error-rate 0.05 --confirm \
    --precheck-validated --confirmation-text JE_CONFIRME_LA_CIBLE_AUTORISEE

# --unsafe desativa o modo segurança (salvaguardas locais de CPU/memória); ausente por padrão
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-minutes 1 --max-error-rate 0.05 --confirm \
    --precheck-validated --unsafe

omega-stress run replay <run-id> --confirm                     # repete uma execução ligada a um perfil congelado

omega-stress history list                                      # histórico das execuções
omega-stress history show <run-id>                              # detalhe de uma execução

omega-stress export <run-id> --format html --destination var/exports --theme omega-base

omega-stress calibrate run                                      # inicia uma calibração desta máquina
omega-stress calibrate show                                     # mostra a última calibração conhecida
```

Os valores de `--level` (`faible`, `bas`, `moyen`, `haut`, `puissant`, `agressif`, `violent`, `maximum`) e o texto de confirmação continuam em francês, como o resto da linha de comando.

`--confirm` é o equivalente, na linha de comando, da caixa de autorização da TUI: obrigatório para qualquer alvo que ainda não esteja fixado como autorizado. Um `--target-id`/`--target-url` idêntico indica um alvo manual (não fixado); use o identificador de um alvo já fixado para evitar `--confirm` a cada execução.

Acrescente `--json` a `history`/`export`/`calibrate` para uma saída legível por máquina, aproveitável em cron/CI.

### Percurso geral

1. Na primeira execução, a tela inicial oferece: Perfis, Teste de requisições, Teste de conexões, Teste de carga, Histórico, Alvos, Calibração, Configurações, Ajuda.
2. A partir de uma tela de teste, um perfil congelado (opcional) continua selecionável no topo da tela: duas maneiras de informar o alvo e os critérios, nunca combinadas em uma mesma execução —
   - **com um perfil**: selecioná-lo preenche alvo/intensidade/duração/limite de erro e o campo de alvo manual desaparece (perde o sentido); os valores preenchidos continuam editáveis antes de iniciar;
   - **sem perfil (modo manual)**: escolher um alvo fixado/recente na lista ou digitar um novo, marcar a autorização se ele ainda não estiver fixado como autorizado, ajustar à mão intensidade/duração (manual ou perfil de duração D1-D6)/limite de erro.

   Nos dois casos: deixar o modo segurança ativo ou desativá-lo com conhecimento de causa, fazer um pré-check se o nível exigir e então iniciar o teste.
3. O resultado aparece imediatamente (veredito, métricas, cronologia), sem passar pelo Histórico — uma exportação é oferecida diretamente nesta tela.
4. Um perfil pode ser congelado para executar o mesmo teste de forma idêntica mais tarde, pela tela Perfis ou repetindo-o a partir do Histórico.

### Valores dos testes

8 níveis de intensidade, idênticos nas três famílias de teste (só muda a dimensão controlada) — grade completa:

| Tipo de teste | Nível | Dimensão controlada | Valor visado | Pré-check | Durações disponíveis (modo manual) |
|---|---|---|---|---|---|
| Teste de requisições | Fraco | Vazão | 250 req/min (≈4,2 req/s) | Não | 1 a 5 min |
| Teste de requisições | Baixo | Vazão | 500 req/min (≈8,3 req/s) | Não | 1 a 5 min |
| Teste de requisições | Médio | Vazão | 1000 req/min (≈16,7 req/s) | Não | 1 a 5 min |
| Teste de requisições | Alto | Vazão | 2000 req/min (≈33,3 req/s) | Não | 1 a 5 min |
| Teste de requisições | Potente | Vazão | 6000 req/min (≈100 req/s) | Opcional | 1 a 3 min (5 com pré-check aprovado) |
| Teste de requisições | Agressivo | Vazão | 10.000 req/min (≈167 req/s) | Opcional | 1 a 3 min (5 com pré-check aprovado) |
| Teste de requisições | Violento | Vazão | 15.000 req/min (≈250 req/s) | **Obrigatório** | Somente 1 a 3 min |
| Teste de requisições | Máximo | Vazão | 20.000 req/min (≈333 req/s) | **Obrigatório** | Somente 1 a 3 min |
| Teste de conexões | Fraco | Conexões simultâneas | 25 conexões | Não | 1 a 5 min |
| Teste de conexões | Baixo | Conexões simultâneas | 50 conexões | Não | 1 a 5 min |
| Teste de conexões | Médio | Conexões simultâneas | 100 conexões | Não | 1 a 5 min |
| Teste de conexões | Alto | Conexões simultâneas | 200 conexões | Não | 1 a 5 min |
| Teste de conexões | Potente | Conexões simultâneas | 1000 conexões | Opcional | 1 a 3 min (5 com pré-check aprovado) |
| Teste de conexões | Agressivo | Conexões simultâneas | 2000 conexões | Opcional | 1 a 3 min (5 com pré-check aprovado) |
| Teste de conexões | Violento | Conexões simultâneas | 3500 conexões | **Obrigatório** | Somente 1 a 3 min |
| Teste de conexões | Máximo | Conexões simultâneas | 5000 conexões | **Obrigatório** | Somente 1 a 3 min |
| Teste de carga (subida progressiva) | Fraco | Vazão, em rampa | pico de 250 req/min | Não | 1 a 5 min |
| Teste de carga (subida progressiva) | Baixo | Vazão, em rampa | pico de 500 req/min | Não | 1 a 5 min |
| Teste de carga (subida progressiva) | Médio | Vazão, em rampa | pico de 1000 req/min | Não | 1 a 5 min |
| Teste de carga (subida progressiva) | Alto | Vazão, em rampa | pico de 2000 req/min | Não | 1 a 5 min |
| Teste de carga (subida progressiva) | Potente | Vazão, em rampa | pico de 6000 req/min | Opcional | 1 a 3 min (5 com pré-check aprovado) |
| Teste de carga (subida progressiva) | Agressivo | Vazão, em rampa | pico de 10.000 req/min | Opcional | 1 a 3 min (5 com pré-check aprovado) |
| Teste de carga (subida progressiva) | Violento | Vazão, em rampa | pico de 15.000 req/min | **Obrigatório** | Somente 1 a 3 min |
| Teste de carga (subida progressiva) | Máximo | Vazão, em rampa | pico de 20.000 req/min | **Obrigatório** | Somente 1 a 3 min |

- **Pré-check Não**: o teste começa diretamente, sem condição de duração.
- **Pré-check Opcional** (Potente/Agressivo): o teste começa sem pré-check (durações de 1-3 min), mas um pré-check aprovado também libera as durações de 4-5 min.
- **Pré-check Obrigatório** (Violento/Máximo): o teste não começa sem um pré-check aprovado antes; a duração continua limitada a 3 min mesmo com pré-check (aqui o pré-check condiciona o acesso ao nível, não uma duração maior).

A coluna «Durações disponíveis» acima cobre apenas o **modo manual** (5 min no máximo). Além disso, só o [modo perfil D1-D6](#perfis-de-duração-d1-d6-modo-perfil) permite testes mais longos (até 120 min) — cada perfil D1-D6 define ele mesmo quais níveis continuam acessíveis nessa duração (`free_max_level`/`reinforced_level`, veja a tabela própria):

| Nível | Duração máx. em modo manual | Duração máx. com um perfil D1-D6 |
|---|---|---|
| Fraco / Baixo / Médio / Alto | 5 min | 120 min (D6, só Conexões/Carga); 60 min em Requisições (D5, D6 incompatível com esta família) |
| Potente | 5 min (3 min sem pré-check) | 120 min com confirmação reforçada (D6, Conexões/Carga) ou 60 min sem (D5) |
| Agressivo | 5 min (3 min sem pré-check) | 60 min com confirmação reforçada (D5) ou 30 min sem (D4) |
| Violento | 3 min (pré-check obrigatório) | 30 min com confirmação reforçada (D4) ou 15 min sem (D3) |
| Máximo | 3 min (pré-check obrigatório) | 5 min no máximo (só D1/D2 — nenhum perfil D3-D6 oferece Máximo, nem com confirmação) |

Esta mesma tabela está disponível diretamente na aplicação (Ajuda → Referências de carga), sempre gerada a partir dos mesmos valores de referência (`domain/load/presets.py`, `domain/load/policies.py`) — nunca duplicada à mão.

> No Teste de carga em **modo manual**, a rampa e o platô são ajustados automaticamente à duração escolhida (mantendo as proporções do preset): um teste de 1 min percorre toda a curva, de 0 ao pico, e não só o seu começo. No **modo perfil D1-D6**, a mesma garantia é dada nativamente pela divisão aquecimento/rampa/platô/retorno à calma de cada perfil — veja [Perfis de duração D1-D6](#perfis-de-duração-d1-d6-modo-perfil).

### Navegação

- Setas para cima/baixo: mover o cursor.
- `Tab` / `Shift+Tab`: navegar entre os campos de um formulário.
- `Esc`: voltar (confirmação de saída a partir da tela inicial).
- `a`: mostrar a ajuda.
- `t`: mudar de tema.
- `q`: sair (com confirmação).
- `r`: atualiza a exibição, útil depois de redimensionar o terminal.
- `Ctrl+P`: paleta de comandos (mudar de tema, captura de tela, ajuda dos atalhos).

Alterne entre os temas com `t`: o Omega-Stress adapta automaticamente as cores e a riqueza de exibição às capacidades detectadas do terminal, a partir de qualquer tela. Pela paleta de comandos (`Ctrl+P` → Tema), os 31 temas disponíveis são oferecidos (10 temas Omega + 21 temas embutidos do Textual).

### Terminais compatíveis

Quatro perfis de renderização, do mais rico ao mais degradado: **Completo**, **Padrão**, **Reduzido**, **Mono**. O perfil escolhido é o mais restritivo entre a família de terminal detectada e o tamanho real da janela (nunca mais rico que qualquer um dos dois tetos).

| Terminal | Perfil padrão |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | Completo |
| Konsole, GNOME Terminal, Terminator, xfce4-terminal | Padrão |
| urxvt, xterm | Reduzido |
| TTY do Linux | Mono |
| SSH (cor real/256 cores detectadas) | Reduzido |
| SSH (sinal mínimo) | Mono |
| Terminal não reconhecido | Reduzido (alternativa prudente) |

Abaixo de 80 colunas × 24 linhas, uma tela de aviso aparece antes da tela inicial (nunca bloqueante: a aplicação continua utilizável, em modo degradado). Konsole, GNOME Terminal e Terminator são reconhecidos pela sua própria variável de ambiente característica (`KONSOLE_VERSION`, `GNOME_TERMINAL_SCREEN`/`GNOME_TERMINAL_SERVICE`, `TERMINATOR_UUID`) em vez de `TERM`, que deixam com seu valor genérico de compatibilidade — o xfce4-terminal não define nenhum marcador equivalente conhecido até hoje e, portanto, só cai nesse mesmo perfil Padrão se expuser um valor `TERM`/`TERM_PROGRAM` reconhecível; caso contrário, Reduzido.

### Caminhos internos e caminhos do sistema

Por padrão, o Omega-Stress trabalha na sua própria pasta `var/`, relativa ao diretório a partir do qual é iniciado (ou `$OMEGA_STRESS_VAR_DIR`, se definida):

```text
var/db/app.db           # banco SQLite (perfis, alvos, histórico)
var/settings.json       # configurações salvas (tema, perfil de renderização, pastas padrão)
var/exports/            # exportações JSON/CSV/HTML padrão
var/screenshots/        # capturas de tela SVG padrão (paleta de comandos)
var/audit.jsonl         # registro de auditoria (uma linha por execução)
var/app.log             # registro da aplicação
```

Um caminho absoluto do sistema (ex. `/var/exports/`) nunca é usado por padrão — a `/` inicial é, portanto, significativa: só uma exportação explícita para uma pasta escolhida pelo usuário (Configurações ou tela Exportação) sai dela.

## Perfis de duração D1-D6 (modo perfil)

Alternativa ao modo manual (duração de 1-5 min limitada por nível): um **perfil de duração nomeado**, com duração total fixa e uma divisão interna em 4 fases (aquecimento, rampa, platô, retorno à calma). Selecionável em cada tela de execução (alternância «Modo de duração: Manual / Perfil D1-D6») e na CLI por `--duration-preset`.

| Perfil | Duração total | Aquecimento | Rampa | Platô | Retorno à calma | Nível máx. sem confirmação | Nível extra (confirmação reforçada) | Famílias compatíveis |
|---|---|---|---|---|---|---|---|---|
| D1 (quick) | 1 min | 5 s | 10 s | 40 s | 5 s | Máximo | — | Requisições, Conexões, Carga |
| D2 (short) | 5 min | 15 s | 30 s | 4 min | 15 s | Máximo | — | Requisições, Conexões, Carga |
| D3 (standard) | 15 min | 30 s | 1 min 30 | 12 min 30 | 30 s | Violento | — | Requisições, Conexões, Carga |
| D4 (resilience) | 30 min | 1 min | 3 min | 25 min | 1 min | Agressivo | Violento | Requisições, Conexões, Carga |
| D5 (extended) | 60 min | 2 min | 5 min | 51 min | 2 min | Potente | Agressivo | Requisições, Conexões, Carga |
| D6 (soak) | 120 min | 3 min | 10 min | 104 min | 3 min | Alto | Potente | Conexões, Carga (nunca Requisições) |

- O nível «extra» (D4-D6) só fica acessível digitando exatamente o texto de confirmação reforçada mostrado na tela — nunca com uma simples caixa de seleção.
- D6 exclui o Teste de requisições: um teste de vazão é limitado por volume, algo nunca pertinente em um perfil de 2 h focado na deriva ao longo do tempo.
- Esta mesma tabela está disponível na aplicação (Ajuda → Perfis de duração D1-D6).

## Modo segurança

Uma caixa de seleção, presente em cada tela de execução (marcada por padrão), que liga ou desliga **apenas** as salvaguardas que protegem a máquina que executa o Omega-Stress (CPU/memória do gerador local):

- **Sempre ativos, qualquer que seja esta configuração**: os limites que protegem o **alvo testado** (taxa de erro, latência) — desativá-los nunca faz sentido para o produto; não é isso que esta caixa cobre.
- **Modo segurança ativo (padrão)**: um teste para automaticamente se a própria máquina hospedeira parecer sob pressão (CPU do gerador E CPU geral da máquina altas ao mesmo tempo, não uma das duas isoladamente — a saturação normal de um único núcleo nunca basta sozinha).
- **Modo segurança desativado**: essa salvaguarda local é retirada. Um lembrete aparece então, comparando o nível escolhido com a última calibração conhecida desta máquina (veja [Calibração local](#calibração-local)) — ultrapassar esse envelope continua possível, mas a confiabilidade do resultado e a estabilidade da máquina passam a ser responsabilidade do usuário.

Também disponível na CLI por `--unsafe` (ausente por padrão = modo segurança ativo).

## Calibração local

Mede a capacidade real **desta máquina** (nunca do alvo testado): um servidor de loopback local embutido no Omega-Stress recebe uma carga crescente em degraus, gerada pelo mesmo motor `httpx`/asyncio dos testes reais.

- 7 degraus, do repouso (ruído de fundo do sistema) até 2000 conexões / 12.000 req/s, cada um avaliado contra limites de saúde (CPU do gerador E geral, memória disponível, taxa de erro, vazão atingida) — os 2 últimos degraus são condicionais, pulados se o degrau anterior não estiver saudável.
- Produz um envelope seguro (`VU_safe` / `RPS_safe`) a partir do último degrau saudável, com uma margem de segurança (~30 % de reserva) e um nível de confiança que cresce com a profundidade atingida.
- **Só medição na V1**: o resultado não é aplicado automaticamente para limitar um teste real — serve como referência informativa, sobretudo quando o [Modo segurança](#modo-segurança) está desativado.
- Salvo por máquina (impressão digital não invasiva: SO/arquitetura/número de núcleos/RAM, nunca um endereço de hardware), consultável a qualquer momento sem medir de novo.

Acessível pela tela **Calibração** da TUI (botão «Iniciar a calibração», progresso mostrado segundo a segundo), ou pela CLI:

```bash
omega-stress calibrate run     # inicia uma nova calibração
omega-stress calibrate show    # mostra a última calibração conhecida, sem iniciar outra
```

## Configuração

Tudo se ajusta pela tela **Configurações** da TUI (nenhum arquivo de configuração para editar à mão):

- **Tema**: um dos 10 temas Omega, aplicado na hora e salvo.
- **Perfil de renderização**: Automático (detecção na inicialização) ou forçado manualmente (Completo/Padrão/Reduzido/Mono).
- **Pasta de exportação padrão**: preenche o campo «destino» da tela Exportação.
- **Pasta de capturas de tela padrão**: usada pelo comando «Captura de tela» da paleta (`Ctrl+P`).
- **Limpezas**: alvos recentes (nunca os fixados), todos os alvos (inclusive os fixados e suas autorizações) ou o histórico completo — cada uma protegida por uma confirmação própria.

As configurações são salvas em `var/settings.json`. A própria raiz `var/` pode ser redirecionada pela variável de ambiente `OMEGA_STRESS_VAR_DIR` (útil para isolar várias instâncias, ou para os testes).

## Testes e qualidade

```bash
pytest
ruff check .
mypy src
lint-imports   # verifica a Dependency Rule (veja pyproject.toml [tool.importlinter])
```

O conjunto cobre mais de 570 testes (unitários, integração, TUI, CLI). `lint-imports` faz a CI falhar se a Dependency Rule ou o isolamento das tecnologias de terceiros for violado — veja [Arquitetura](#arquitetura).

## Desinstalação

O Omega-Stress não mexe em nada fora da sua própria pasta e de uma linha de alias opcional:

```bash
rm -rf ~/omega-stress
sed -i '/alias stress=/d' ~/.bashrc ~/.zshrc
```

Nenhum pacote do sistema, serviço ou arquivo fora de `~/omega-stress/` é criado pelo `install.sh` — não é preciso nenhuma desinstalação adicional.

## Limitações conhecidas

- Geração de carga **no próprio processo**, em uma única máquina (`httpx`/asyncio): não é uma ferramenta distribuída — os tetos reais (veja [Valores dos testes](#valores-dos-testes)) são bem mais modestos que os de um serviço SaaS de testes de carga (loader.io etc.), de propósito, por postura de produto controlado. Em hardware modesto, os níveis Agressivo/Violento/Máximo do Teste de conexões podem levar bem mais tempo real do que a duração escolhida para emitir toda a carga visada — é então a capacidade **desta máquina**, não a do alvo, que limita a vazão real; use a [Calibração local](#calibração-local) para conhecer os valores razoáveis no seu hardware.
- A detecção automática da família de terminal se baseia em variáveis de ambiente: o xfce4-terminal não tem nenhum marcador confiável conhecido até hoje (veja [Terminais compatíveis](#terminais-compatíveis)).
- `plugins/` é um ponto de extensão previsto pela arquitetura (carregamento de plugins embutidos/externos), não implementado na V1: a estrutura existe, nenhum plugin é entregue.
- `var/` é relativo à pasta do projeto (não XDG): pensado para uso local por um único usuário, não para compartilhamento entre vários usuários da mesma máquina.
- O Teste de carga (subida progressiva) em **modo manual** não tem degrau de descida («cooldown») depois do platô — só disponível com um [perfil de duração D1-D6](#perfis-de-duração-d1-d6-modo-perfil), que inclui as 4 fases nativamente.
- Um pré-check aprovado não está ligado a um alvo específico: continua válido por 24 h para qualquer execução Violento/Máximo seguinte, não só no alvo verificado.
- A [Calibração local](#calibração-local) mede, mas ainda não aplica automaticamente seu envelope seguro para limitar um teste real — um trabalho deliberadamente separado, ainda não iniciado.

## Licença

MIT — veja `LICENSE`.
