<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licenza MIT (vedi il file LICENSE) -->
<div align="center">
  <img src="../../assets/omega-stress.png" alt="Omega-Stress" width="384">
</div>

# 🗲 OMEGA-STRESS

**Postazione di test di carico HTTP controllati**

> Realizzato da **kraynux** per **Omega-server** 
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Pagina ufficiale: [OMEGA-STRESS](https://kraynux.snake-mackarel.ts.net/omega-stress/) &nbsp; Anteprima: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-stress/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interfaccia e report esportati disponibili in **17 lingue** — vedi [Lingue dell'interfaccia](#lingue-dellinterfaccia).  
**Lingue:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)



**Omega-Stress** è un'applicazione locale da terminale (TUI [Textual](https://github.com/Textualize/textual) + CLI scriptabile) che conduce test di carico HTTP in modo controllato e riutilizzabile: profili congelati, cronologia, riesecuzione, esportazioni dettagliate (JSON/CSV/HTML), limiti di sicurezza espliciti.

Il progetto segue i principi della **Clean Architecture**, con una netta separazione tra dominio di business, orchestrazione, infrastruttura e interfaccia utente.
---

## Indice

- [Presentazione](#presentazione)
- [Funzionalità](#funzionalità)
- [Architettura](#architettura)
- [Prerequisiti](#prerequisiti)
- [Installazione](#installazione)
- [Utilizzo](#avvio)
- [Profili di durata D1-D6](#profili-di-durata-d1-d6-modalità-profilo)
- [Modalità sicurezza](#modalità-sicurezza)
- [Calibrazione locale](#calibrazione-locale)
- [Configurazione](#configurazione)
- [Test e qualità](#test-e-qualità)
- [Disinstallazione](#disinstallazione)
- [Limiti noti](#limiti-noti)
- [Licenza](#licenza)

## Presentazione

### Obiettivi

## Cosa fa Omega-Stress (obiettivo V1)

- Tre famiglie di test controllate: **Test di richieste** (portata), **Test di connessioni** (simultaneità), **Test di carico** (salita progressiva).
- **8 livelli di intensità** (Debole/Basso/Medio/Alto/Potente/Aggressivo/Violento/Massimo), con un modello di pre-check a 3 gradini (mai richiesto / richiesto facoltativo / richiesto obbligatorio — vedi [Valori dei test](#valori-dei-test)).
- **Due modalità di durata**: manuale (da 1 a 5 min, limitata per livello) oppure **profilo con nome D1-D6** (durata totale fissa con riscaldamento/rampa/plateau/ritorno alla calma — vedi [Profili di durata D1-D6](#profili-di-durata-d1-d6-modalità-profilo)).
- **Modalità sicurezza** (attiva per impostazione predefinita, disattivabile a ogni avvio): salvaguardie locali di CPU/memoria della macchina ospite, distinte dalle soglie che proteggono la destinazione testata — vedi [Modalità sicurezza](#modalità-sicurezza).
- **Calibrazione locale persistente**: misura la capacità reale della macchina ospite (mai della destinazione) tramite un server di loopback locale, a gradini di carico crescente — vedi [Calibrazione locale](#calibrazione-locale).
- Profili congelati, riutilizzabili e registrati in cronologia — **facoltativi**: un test si avvia altrettanto bene in modalità manuale, senza alcun profilo, scegliendo o inserendo direttamente una destinazione.
- Conferma esplicita di autorizzazione obbligatoria prima di qualsiasi esecuzione su una destinazione non fissata.
- Soglie di arresto automatico, mai un carico illimitato.
- Esportazioni JSON/CSV/HTML dettagliate (gradini, metriche per intervallo, verdetto, diagnosi).
- Modalità CLI non interattiva per l'automazione (cron, CI), che richiama esattamente gli stessi casi d'uso della TUI.
- Adattamento automatico al terminale (tema + profilo di rendering degradabile).

## Cosa il progetto non fa

- Non sostituisce uno strumento di scansione di rete — vocabolario e postura del prodotto dichiaratamente «test di carico», mai «scansione».
- Non implementa alcun motore di carico esterno (k6 ecc.) — generazione nativa `httpx`/asyncio.
- Non avvia alcuna esecuzione senza limiti né conferma di autorizzazione.
- Non è uno strumento di carico distribuito: la generazione gira su una sola macchina, in un solo processo — vedi [Limiti noti](#limiti-noti).

## Funzionalità

- **Tre famiglie di test**, ognuna con 8 livelli di intensità (Debole/Basso/Medio/Alto/Potente/Aggressivo/Violento/Massimo) — vedi la tabella [Riferimenti di carico](#valori-dei-test) per i valori esatti di ogni livello.
- **Profili di test congelati**: nome, destinazione, famiglia, intensità, durata, soglia di errore — creati una volta e rieseguiti in modo identico dalla TUI o dalla CLI.
- **Profili di durata con nome D1-D6** (modalità «profilo»), alternativa alla modalità manuale: una durata totale fissa (da 1 a 120 min) con riscaldamento/rampa/plateau/ritorno alla calma, che limita anche i livelli accessibili — vedi [Profili di durata D1-D6](#profili-di-durata-d1-d6-modalità-profilo).
- **Modalità sicurezza**, selezionata per impostazione predefinita in ogni schermata di avvio: arresta un test se la macchina ospite (non la destinazione) sembra in pericolo. Disattivabile consapevolmente, con un promemoria che confronta il livello scelto con l'ultima calibrazione effettuata — vedi [Modalità sicurezza](#modalità-sicurezza).
- **Calibrazione locale persistente**: misura ciò che la macchina può realmente sostenere (7 gradini di carico crescente verso un server di loopback locale integrato), consultabile dalla schermata Calibrazione — vedi [Calibrazione locale](#calibrazione-locale).
- **Destinazioni fissate**: un indirizzo fissato evita di riselezionare l'autorizzazione a ogni avvio; le destinazioni recenti non fissate restano visibili (al massimo 10) senza autorizzazione implicita. Una destinazione fissata si usa in due modi indipendenti: direttamente, per avviare un test in modalità manuale senza alcun profilo, oppure come destinazione predefinita alla creazione di un profilo congelato.
- **Cronologia completa**: ogni esecuzione viene registrata (verdetto, metriche, cronologia per intervallo, modalità sicurezza usata); un'esecuzione legata a un profilo congelato può essere ripetuta in modo identico.
- **Esportazioni dettagliate** in JSON (dati grezzi reimportabili), CSV (analisi tabellare) o HTML (report leggibile, con tema a scelta tra le 10 palette del progetto). Il report HTML viene scritto nella lingua scelta nelle Impostazioni («Lingua delle esportazioni», per impostazione predefinita quella dell'interfaccia); JSON e CSV restano dati, non tradotti.
- **Pre-check** automatico e obbligatorio prima di qualsiasi test Violento/Massimo, facoltativo (ma capace di sbloccare durate aggiuntive) su Potente/Aggressivo, con una finestra di validità (24 h).
- **Monitoraggio in tempo reale** di un test in corso: indicatore di avanzamento con conto alla rovescia affidabile (tempo rimanente calcolato direttamente, mai stimato), portata/errori/latenza p95 aggiornati a ogni intervallo, arresto manuale possibile senza uscire dall'applicazione.
- **Impostazioni centralizzate**: tema (10 palette Omega + tutti i temi integrati di Textual, 31 in totale dalla palette dei comandi), profilo di rendering (automatico o forzato), cartelle di esportazione e di screenshot, pulizia delle destinazioni/della cronologia.
- **Aiuto integrato** (tasto `a`): scorciatoie da tastiera, descrizione di ogni schermata (comprese Calibrazione e Modalità sicurezza), tabella di riferimento dei valori di carico e tabella dei profili di durata D1-D6.
- **CLI scriptabile** (`omega-stress profile|run|history|export|calibrate ...`), esattamente gli stessi casi d'uso della TUI, con uscita `--json` disponibile per l'automazione.
- **Adattamento automatico al terminale**: famiglia e dimensioni rilevate all'avvio, tema e ricchezza di visualizzazione regolati di conseguenza (vedi [Terminali supportati](#terminali-supportati)).

## Architettura

Clean Architecture + Ports & Adapters in 9 pacchetti (`app/`, `core/`, `domain/`, `application/`, `ports/`, `infrastructure/`, `interfaces/`, `plugins/`, `shared/`).
Dettaglio completo: `ARCHITECTURE.md`.

```text
src/omega_stress/
├── app/              Avvio e contenitore di iniezione delle dipendenze (collegamento manuale, nessun framework DI)
├── core/             Vocabolario trasversale: enumerazioni, eccezioni radice, Result/Ok/Err, capacità del sistema
├── domain/           Logica di business pura: carico, profili, esecuzioni, destinazioni, temi, terminale — senza I/O
├── application/      Orchestrazione: commands (azioni), queries (letture), pipeline di esecuzione (guards/hooks)
├── ports/            Contratti Protocol/ABC attesi dagli adattatori (repository, esportatori, generatore di carico...)
├── infrastructure/   Implementazioni concrete: SQLite, esportatori JSON/CSV/HTML, generatore httpx/asyncio, rilevamento del terminale, sonda di sistema
├── interfaces/       Due adattatori di presentazione indipendenti: TUI (Textual) e CLI (argparse)
├── plugins/          Punto di estensione riservato (caricamento di plugin) — struttura presente, non implementata nella V1
└── shared/           Utilità trasversali senza dipendenze di business (orologio iniettabile, generazione di identificatori)
```

### Principi di progettazione

- `domain/` non contiene né I/O né dipendenze dall'infrastruttura — logica di business pura, interamente testabile senza mock.
- `application/` orchestra i casi d'uso tramite il dominio e le porte, mai direttamente con una classe concreta di `infrastructure/`.
- `infrastructure/` implementa le porte senza mai essere importata direttamente da `application/` o `domain/` — solo `interfaces/` e `app/` la referenziano.
- `interfaces/` non deve mai chiamare direttamente `infrastructure/` né `subprocess`: solo tramite `application/` (commands/queries) e i propri controller.
- `ports/` definisce i contratti attesi dagli adattatori (Protocol), mai un'implementazione.
- `core/` raccoglie il vocabolario comune a tutti i livelli, senza mai codificarvi una regola di business numerica (soglie, durate, preset — sempre in `domain/*/policies.py`).

La Dependency Rule (solo dai livelli esterni verso quelli interni) e l'isolamento delle tecnologie di terze parti (`textual`, `sqlite3`, `httpx`, `jinja2`, ciascuna confinata al proprio punto d'ingresso designato) vengono verificati automaticamente a ogni esecuzione di `lint-imports` (vedi [Test e qualità](#test-e-qualità)).

## Prerequisiti

- Python ≥ 3.10
- [`uv`](https://github.com/astral-sh/uv) consigliato per la gestione delle dipendenze (altrimenti `pip` standard)

### Sistema

- Linux, in primo luogo Arch Linux e distribuzioni compatibili.
- Python 3.10 o superiore.
- Nessun privilegio di root necessario: Omega-Stress effettua solo chiamate HTTP in uscita come utente normale.

## Installazione

L'archivio ufficiale è fornito in formato `.tar.gz`. Verificane l'integrità prima dell'installazione:

```bash
sha256sum omega-stress.tar.gz
```

### Metodo 1 — script di installazione

```bash
[ -d omega-stress ] && echo "ℹ️ Già estratto qui, passaggio saltato." || tar -xzf omega-stress.tar.gz
[ -d ~/omega-stress ] && echo "ℹ️ ~/omega-stress esiste già, spostamento saltato." || mv omega-stress ~/
cd ~/omega-stress/
chmod +x install.sh
./install.sh
```

### Metodo 2 — installazione completa resiliente

Questo comando può essere copiato e incollato così com'è e rilanciato senza errori: ogni passaggio salta ciò che è già stato fatto.

```bash
( [ -d omega-stress ] || tar -xzf omega-stress.tar.gz ) && \
( [ -d ~/omega-stress ] || mv omega-stress ~/ ) && \
cd ~/omega-stress && chmod +x install.sh && ./install.sh
```
`install.sh`:

1. Crea l'ambiente virtuale `.venv` se non esiste già.
2. Installa le dipendenze (`pip install -e .`; `pyproject.toml` resta l'unica fonte di verità).
3. Rende eseguibili `omega-stress.sh` e `install.sh`.
4. Aggiunge l'alias `stress` a `~/.bashrc` e `~/.zshrc` (senza duplicati se già presente).

## Installazione (sviluppo)

```bash
uv sync --all-extras
# oppure, senza uv:
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```


### Avvio

```bash
cd ~/omega-stress
./omega-stress.sh

# oppure digita semplicemente "stress" in un nuovo terminale se l'alias è stato creato
```

Il lanciatore:

1. Rileva `.venv`, `venv` o il Python di sistema.
2. Imposta `PYTHONPATH` su `src/`.
3. Avvia `python -m omega_stress` — senza argomenti apre la TUI; con un argomento passa alla CLI.

### Lingue dell'interfaccia

L'interfaccia è disponibile in 17 lingue: francese, inglese, spagnolo, portoghese (Brasile), italiano, tedesco, olandese, polacco, russo, cinese semplificato, vietnamita, thailandese, indonesiano, giapponese, coreano, hindi e arabo. La scelta si fa nelle Impostazioni («Langue / Language») e vale dopo il riavvio dell'interfaccia; la variabile `OMEGA_STRESS_LANG` (per esempio `OMEGA_STRESS_LANG=it ./omega-stress.sh`) impone una lingua per una sessione. Avviato da omega-suite, omega-stress usa la lingua della suite. In una console di testo Linux (TTY), le lingue con scrittura non latina vengono mostrate in inglese per la sessione. La riga di comando resta in francese.

### Utilizzo da CLI

```bash
omega-stress profile list                                     # elencare i profili
omega-stress profile create --name "Sondaggio API" --target-id t-1 \
    --family request --level bas --duration-minutes 1 --max-error-rate 0.05
omega-stress profile freeze <profile-id>                       # congelare un profilo

# Pre-check obbligatorio prima di qualsiasi avvio Violento/Massimo (facoltativo su Potente/Aggressivo)
omega-stress run precheck --target-id t-1 --target-url https://exemple.org --confirm

omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level bas --duration-minutes 1 --max-error-rate 0.05 --confirm
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level moyen --duration-minutes 3 --max-error-rate 0.05 --confirm
omega-stress run ramp --target-id t-1 --target-url https://exemple.org \
    --level puissant --duration-minutes 3 --max-error-rate 0.05 --confirm --precheck-validated

# Modalità profilo D1-D6, al posto di --duration-minutes (mutuamente esclusivi)
# D4 (resilience) consente Aggressivo senza condizioni e Violento con conferma rafforzata
omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-preset d4 --max-error-rate 0.05 --confirm \
    --precheck-validated --confirmation-text JE_CONFIRME_LA_CIBLE_AUTORISEE

# --unsafe disattiva la modalità sicurezza (salvaguardie locali di CPU/memoria); assente per impostazione predefinita
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-minutes 1 --max-error-rate 0.05 --confirm \
    --precheck-validated --unsafe

omega-stress run replay <run-id> --confirm                     # ripete un'esecuzione legata a un profilo congelato

omega-stress history list                                      # cronologia delle esecuzioni
omega-stress history show <run-id>                              # dettaglio di un'esecuzione

omega-stress export <run-id> --format html --destination var/exports --theme omega-base

omega-stress calibrate run                                      # avvia una calibrazione di questa macchina
omega-stress calibrate show                                     # mostra l'ultima calibrazione nota
```

I valori di `--level` (`faible`, `bas`, `moyen`, `haut`, `puissant`, `agressif`, `violent`, `maximum`) e il testo di conferma restano in francese, come il resto della riga di comando.

`--confirm` è l'equivalente da riga di comando della casella di autorizzazione della TUI: obbligatorio per qualsiasi destinazione che non sia già fissata come autorizzata. `--target-id`/`--target-url` identici indicano una destinazione manuale (non fissata); usa l'identificatore di una destinazione già fissata per evitare `--confirm` a ogni avvio.

Aggiungi `--json` a `history`/`export`/`calibrate` per un'uscita leggibile dalle macchine, sfruttabile in cron/CI.

### Percorso generale

1. Al primo avvio, la schermata iniziale propone: Profili, Test di richieste, Test di connessioni, Test di carico, Cronologia, Obiettivi, Calibrazione, Impostazioni, Aiuto.
2. Da una schermata di test, un profilo congelato (facoltativo) resta selezionabile in alto: due modi per indicare destinazione e criteri, mai combinati in uno stesso avvio —
   - **con un profilo**: selezionarlo precompila destinazione/intensità/durata/soglia di errore e il campo della destinazione manuale scompare (non serve più); i valori precompilati restano modificabili prima dell'avvio;
   - **senza profilo (modalità manuale)**: scegliere una destinazione fissata/recente dall'elenco o inserirne una nuova, selezionare l'autorizzazione se non è già fissata come autorizzata, regolare a mano intensità/durata (manuale o profilo di durata D1-D6)/soglia di errore.

   In entrambi i casi: lasciare attiva la modalità sicurezza o disattivarla consapevolmente, eseguire un pre-check se il livello lo richiede, poi avviare il test.
3. Il risultato appare subito (verdetto, metriche, cronologia), senza passare dalla Cronologia — un'esportazione viene proposta direttamente da questa schermata.
4. Un profilo può essere congelato per rieseguire lo stesso test in modo identico in seguito, dalla schermata Profili o ripetendolo dalla Cronologia.

### Valori dei test

8 livelli di intensità, identici nelle tre famiglie di test (cambia solo la dimensione controllata) — griglia completa:

| Tipo di test | Livello | Dimensione controllata | Valore obiettivo | Pre-check | Durate disponibili (modalità manuale) |
|---|---|---|---|---|---|
| Test di richieste | Debole | Portata | 250 rich/min (≈4,2 rich/s) | No | Da 1 a 5 min |
| Test di richieste | Basso | Portata | 500 rich/min (≈8,3 rich/s) | No | Da 1 a 5 min |
| Test di richieste | Medio | Portata | 1000 rich/min (≈16,7 rich/s) | No | Da 1 a 5 min |
| Test di richieste | Alto | Portata | 2000 rich/min (≈33,3 rich/s) | No | Da 1 a 5 min |
| Test di richieste | Potente | Portata | 6000 rich/min (≈100 rich/s) | Facoltativo | Da 1 a 3 min (5 con pre-check superato) |
| Test di richieste | Aggressivo | Portata | 10.000 rich/min (≈167 rich/s) | Facoltativo | Da 1 a 3 min (5 con pre-check superato) |
| Test di richieste | Violento | Portata | 15.000 rich/min (≈250 rich/s) | **Obbligatorio** | Solo da 1 a 3 min |
| Test di richieste | Massimo | Portata | 20.000 rich/min (≈333 rich/s) | **Obbligatorio** | Solo da 1 a 3 min |
| Test di connessioni | Debole | Connessioni simultanee | 25 connessioni | No | Da 1 a 5 min |
| Test di connessioni | Basso | Connessioni simultanee | 50 connessioni | No | Da 1 a 5 min |
| Test di connessioni | Medio | Connessioni simultanee | 100 connessioni | No | Da 1 a 5 min |
| Test di connessioni | Alto | Connessioni simultanee | 200 connessioni | No | Da 1 a 5 min |
| Test di connessioni | Potente | Connessioni simultanee | 1000 connessioni | Facoltativo | Da 1 a 3 min (5 con pre-check superato) |
| Test di connessioni | Aggressivo | Connessioni simultanee | 2000 connessioni | Facoltativo | Da 1 a 3 min (5 con pre-check superato) |
| Test di connessioni | Violento | Connessioni simultanee | 3500 connessioni | **Obbligatorio** | Solo da 1 a 3 min |
| Test di connessioni | Massimo | Connessioni simultanee | 5000 connessioni | **Obbligatorio** | Solo da 1 a 3 min |
| Test di carico (salita progressiva) | Debole | Portata, in rampa | picco di 250 rich/min | No | Da 1 a 5 min |
| Test di carico (salita progressiva) | Basso | Portata, in rampa | picco di 500 rich/min | No | Da 1 a 5 min |
| Test di carico (salita progressiva) | Medio | Portata, in rampa | picco di 1000 rich/min | No | Da 1 a 5 min |
| Test di carico (salita progressiva) | Alto | Portata, in rampa | picco di 2000 rich/min | No | Da 1 a 5 min |
| Test di carico (salita progressiva) | Potente | Portata, in rampa | picco di 6000 rich/min | Facoltativo | Da 1 a 3 min (5 con pre-check superato) |
| Test di carico (salita progressiva) | Aggressivo | Portata, in rampa | picco di 10.000 rich/min | Facoltativo | Da 1 a 3 min (5 con pre-check superato) |
| Test di carico (salita progressiva) | Violento | Portata, in rampa | picco di 15.000 rich/min | **Obbligatorio** | Solo da 1 a 3 min |
| Test di carico (salita progressiva) | Massimo | Portata, in rampa | picco di 20.000 rich/min | **Obbligatorio** | Solo da 1 a 3 min |

- **Pre-check No**: il test parte direttamente, senza condizioni di durata.
- **Pre-check Facoltativo** (Potente/Aggressivo): il test parte senza pre-check (durate 1-3 min), ma un pre-check superato sblocca anche le durate di 4-5 min.
- **Pre-check Obbligatorio** (Violento/Massimo): il test non parte senza un pre-check superato in precedenza; la durata resta limitata a 3 min anche con pre-check (qui il pre-check condiziona l'accesso al livello, non una durata estesa).

La colonna «Durate disponibili» qui sopra copre solo la **modalità manuale** (al massimo 5 min). Oltre, solo la [modalità profilo D1-D6](#profili-di-durata-d1-d6-modalità-profilo) permette test più lunghi (fino a 120 min) — ogni profilo D1-D6 stabilisce da sé quali livelli restano accessibili a quella durata (`free_max_level`/`reinforced_level`, vedi la sua tabella):

| Livello | Durata max in modalità manuale | Durata max con un profilo D1-D6 |
|---|---|---|
| Debole / Basso / Medio / Alto | 5 min | 120 min (D6, solo Connessioni/Carico); 60 min su Richieste (D5, D6 non compatibile con questa famiglia) |
| Potente | 5 min (3 min senza pre-check) | 120 min con conferma rafforzata (D6, Connessioni/Carico) o 60 min senza (D5) |
| Aggressivo | 5 min (3 min senza pre-check) | 60 min con conferma rafforzata (D5) o 30 min senza (D4) |
| Violento | 3 min (pre-check obbligatorio) | 30 min con conferma rafforzata (D4) o 15 min senza (D3) |
| Massimo | 3 min (pre-check obbligatorio) | 5 min al massimo (solo D1/D2 — nessun profilo D3-D6 offre Massimo, nemmeno con conferma) |

Questa stessa tabella è disponibile direttamente nell'applicazione (Aiuto → Riferimenti di carico), sempre generata dagli stessi valori di riferimento (`domain/load/presets.py`, `domain/load/policies.py`) — mai duplicata a mano.

> Nel Test di carico in **modalità manuale**, la rampa e il plateau vengono adattati automaticamente alla durata scelta (mantenendo le proporzioni del preset): un test di 1 min esplora tutta la curva, da 0 al picco, non solo il suo inizio. In **modalità profilo D1-D6**, la stessa garanzia è data nativamente dalla suddivisione riscaldamento/rampa/plateau/ritorno alla calma di ogni profilo — vedi [Profili di durata D1-D6](#profili-di-durata-d1-d6-modalità-profilo).

### Navigazione

- Frecce su/giù: spostare il cursore.
- `Tab` / `Maiusc+Tab`: spostarsi tra i campi di un modulo.
- `Esc`: tornare indietro (conferma di uscita dalla schermata iniziale).
- `a`: mostrare l'aiuto.
- `t`: cambiare tema.
- `q`: uscire (con conferma).
- `r`: aggiorna la visualizzazione, utile dopo aver ridimensionato il terminale.
- `Ctrl+P`: palette dei comandi (cambiare tema, screenshot, aiuto sulle scorciatoie).

Passa da un tema all'altro con `t`: Omega-Stress adatta automaticamente i colori e la ricchezza di visualizzazione alle capacità rilevate del terminale, da qualsiasi schermata. Dalla palette dei comandi (`Ctrl+P` → Tema) vengono proposti tutti i 31 temi disponibili (10 temi Omega + 21 temi integrati di Textual).

### Terminali supportati

Quattro profili di rendering, dal più ricco al più degradato: **Completo**, **Standard**, **Ridotto**, **Mono**. Il profilo scelto è il più restrittivo tra la famiglia di terminale rilevata e la dimensione reale della finestra (mai più ricco di uno dei due tetti).

| Terminale | Profilo predefinito |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | Completo |
| Konsole, GNOME Terminal, Terminator, xfce4-terminal | Standard |
| urxvt, xterm | Ridotto |
| TTY Linux | Mono |
| SSH (true color/256 colori rilevati) | Ridotto |
| SSH (segnale minimo) | Mono |
| Terminale non riconosciuto | Ridotto (ripiego prudente) |

Sotto le 80 colonne × 24 righe, una schermata di avviso appare prima di quella iniziale (mai bloccante: l'applicazione resta utilizzabile, in modalità degradata). Konsole, GNOME Terminal e Terminator vengono riconosciuti tramite la propria variabile d'ambiente caratteristica (`KONSOLE_VERSION`, `GNOME_TERMINAL_SCREEN`/`GNOME_TERMINAL_SERVICE`, `TERMINATOR_UUID`) anziché tramite `TERM`, che lasciano al suo valore generico di compatibilità — xfce4-terminal non imposta alcun marcatore equivalente noto finora e quindi ripiega su questo stesso profilo Standard solo se espone un valore `TERM`/`TERM_PROGRAM` riconoscibile, altrimenti Ridotto.

### Percorsi interni e percorsi di sistema

Per impostazione predefinita, Omega-Stress lavora nella propria cartella `var/`, relativa alla directory da cui viene avviato (o `$OMEGA_STRESS_VAR_DIR` se definita):

```text
var/db/app.db           # database SQLite (profili, destinazioni, cronologia)
var/settings.json       # impostazioni salvate (tema, profilo di rendering, cartelle predefinite)
var/exports/            # esportazioni JSON/CSV/HTML predefinite
var/screenshots/        # screenshot SVG predefiniti (palette dei comandi)
var/audit.jsonl         # registro di audit (una riga per esecuzione)
var/app.log             # registro dell'applicazione
```

Un percorso assoluto di sistema (es. `/var/exports/`) non viene mai usato per impostazione predefinita — la `/` iniziale è quindi significativa: ne esce solo un'esportazione esplicita verso una cartella scelta dall'utente (Impostazioni o schermata Esportazione).

## Profili di durata D1-D6 (modalità profilo)

Alternativa alla modalità manuale (durata 1-5 min limitata per livello): un **profilo di durata con nome**, con una durata totale fissa e una suddivisione interna in 4 fasi (riscaldamento, rampa, plateau, ritorno alla calma). Selezionabile in ogni schermata di avvio (interruttore «Modalità durata: Manuale / Profilo D1-D6») e da CLI tramite `--duration-preset`.

| Profilo | Durata totale | Riscaldamento | Rampa | Plateau | Ritorno alla calma | Livello max senza conferma | Livello aggiuntivo (conferma rafforzata) | Famiglie compatibili |
|---|---|---|---|---|---|---|---|---|
| D1 (quick) | 1 min | 5 s | 10 s | 40 s | 5 s | Massimo | — | Richieste, Connessioni, Carico |
| D2 (short) | 5 min | 15 s | 30 s | 4 min | 15 s | Massimo | — | Richieste, Connessioni, Carico |
| D3 (standard) | 15 min | 30 s | 1 min 30 | 12 min 30 | 30 s | Violento | — | Richieste, Connessioni, Carico |
| D4 (resilience) | 30 min | 1 min | 3 min | 25 min | 1 min | Aggressivo | Violento | Richieste, Connessioni, Carico |
| D5 (extended) | 60 min | 2 min | 5 min | 51 min | 2 min | Potente | Aggressivo | Richieste, Connessioni, Carico |
| D6 (soak) | 120 min | 3 min | 10 min | 104 min | 3 min | Alto | Potente | Connessioni, Carico (mai Richieste) |

- Il livello «aggiuntivo» (D4-D6) è accessibile solo digitando esattamente il testo di conferma rafforzata mostrato sullo schermo — mai con una semplice casella da spuntare.
- D6 esclude il Test di richieste: un test di portata si limita in volume, cosa mai pertinente su un profilo di 2 h incentrato sulla deriva nel tempo.
- Questa stessa tabella è disponibile nell'applicazione (Aiuto → Profili di durata D1-D6).

## Modalità sicurezza

Una casella di spunta, presente in ogni schermata di avvio (selezionata per impostazione predefinita), che attiva o disattiva **soltanto** le salvaguardie che proteggono la macchina che esegue Omega-Stress (CPU/memoria del generatore locale):

- **Sempre attive, qualunque sia questa impostazione**: le soglie che proteggono la **destinazione testata** (tasso di errore, latenza) — disattivarle non ha mai senso per il prodotto; non è ciò che copre questa casella.
- **Modalità sicurezza attiva (predefinita)**: un test si ferma automaticamente se la macchina ospite stessa sembra sotto pressione (CPU del generatore E CPU complessiva della macchina elevate contemporaneamente, non una delle due da sola — la normale saturazione di un singolo core non basta mai da sola).
- **Modalità sicurezza disattivata**: questa salvaguardia locale viene rimossa. Compare allora un promemoria che confronta il livello scelto con l'ultima calibrazione nota di questa macchina (vedi [Calibrazione locale](#calibrazione-locale)) — superare quell'involucro resta possibile, ma l'affidabilità del risultato e la stabilità della macchina diventano responsabilità dell'utente.

Disponibile anche da CLI tramite `--unsafe` (assente per impostazione predefinita = modalità sicurezza attiva).

## Calibrazione locale

Misura la capacità reale di **questa macchina** (mai della destinazione testata): un server di loopback locale integrato in Omega-Stress riceve un carico crescente a gradini, generato dallo stesso motore `httpx`/asyncio dei test reali.

- 7 gradini, dal riposo (rumore di fondo del sistema) fino a 2000 connessioni / 12.000 rich/s, ciascuno valutato rispetto a soglie di salute (CPU del generatore E complessiva, memoria disponibile, tasso di errore, portata raggiunta) — gli ultimi 2 gradini sono condizionali, saltati se il gradino precedente non è sano.
- Produce un involucro sicuro (`VU_safe` / `RPS_safe`) a partire dall'ultimo gradino sano, con un margine di sicurezza (~30 % di riserva) e un livello di fiducia che cresce con la profondità raggiunta.
- **Solo misurazione nella V1**: il risultato non viene applicato automaticamente per limitare un test reale — serve da riferimento informativo, soprattutto quando la [Modalità sicurezza](#modalità-sicurezza) è disattivata.
- Salvata per macchina (impronta non invasiva: SO/architettura/numero di core/RAM, mai un indirizzo hardware), consultabile in qualsiasi momento senza rifare la misura.

Accessibile dalla schermata **Calibrazione** della TUI (pulsante «Avvia la calibrazione», avanzamento mostrato secondo per secondo), oppure da CLI:

```bash
omega-stress calibrate run     # avvia una nuova calibrazione
omega-stress calibrate show    # mostra l'ultima calibrazione nota, senza avviarne un'altra
```

## Configurazione

Tutto si regola dalla schermata **Impostazioni** della TUI (nessun file di configurazione da modificare a mano):

- **Tema**: uno dei 10 temi Omega, applicato subito e salvato.
- **Profilo di rendering**: Automatico (rilevamento all'avvio) o forzato manualmente (Completo/Standard/Ridotto/Mono).
- **Cartella di esportazione predefinita**: precompila il campo «destinazione» della schermata Esportazione.
- **Cartella degli screenshot predefinita**: usata dal comando «Screenshot» della palette (`Ctrl+P`).
- **Pulizie**: destinazioni recenti (mai quelle fissate), tutte le destinazioni (comprese quelle fissate e le relative autorizzazioni) oppure l'intera cronologia — ciascuna protetta da una conferma dedicata.

Le impostazioni vengono salvate in `var/settings.json`. La radice `var/` stessa può essere reindirizzata tramite la variabile d'ambiente `OMEGA_STRESS_VAR_DIR` (utile per isolare più istanze, o per i test).

## Test e qualità

```bash
pytest
ruff check .
mypy src
lint-imports   # verifica la Dependency Rule (vedi pyproject.toml [tool.importlinter])
```

La suite copre più di 570 test (unitari, integrazione, TUI, CLI). `lint-imports` fa fallire la CI se la Dependency Rule o l'isolamento delle tecnologie di terze parti vengono violati — vedi [Architettura](#architettura).

## Disinstallazione

Omega-Stress non tocca nulla al di fuori della propria cartella e di una riga di alias facoltativa:

```bash
rm -rf ~/omega-stress
sed -i '/alias stress=/d' ~/.bashrc ~/.zshrc
```

`install.sh` non crea alcun pacchetto di sistema, servizio né file al di fuori di `~/omega-stress/` — non serve alcuna disinstallazione aggiuntiva.

## Limiti noti

- Generazione del carico **nel processo stesso**, su una sola macchina (`httpx`/asyncio): non è uno strumento distribuito — i tetti reali (vedi [Valori dei test](#valori-dei-test)) sono nettamente più modesti di quelli di un servizio SaaS di test di carico (loader.io ecc.), volutamente, per una postura di prodotto controllato. Su hardware modesto, i livelli Aggressivo/Violento/Massimo del Test di connessioni possono richiedere molto più tempo reale della durata scelta per emettere tutto il carico previsto — è allora la capacità di **questa macchina**, non quella della destinazione, a limitare la portata reale; usa la [Calibrazione locale](#calibrazione-locale) per conoscere i valori ragionevoli sul tuo hardware.
- Il rilevamento automatico della famiglia di terminale si basa su variabili d'ambiente: xfce4-terminal non ha alcun marcatore affidabile noto finora (vedi [Terminali supportati](#terminali-supportati)).
- `plugins/` è un punto di estensione previsto dall'architettura (caricamento di plugin integrati/esterni), non implementato nella V1: la struttura esiste, non viene fornito alcun plugin.
- `var/` è relativa alla cartella del progetto (non XDG): pensata per un uso locale a utente singolo, non per la condivisione tra più utenti sulla stessa macchina.
- Il Test di carico (salita progressiva) in **modalità manuale** non prevede un gradino di discesa («cooldown») dopo il plateau — disponibile solo tramite un [profilo di durata D1-D6](#profili-di-durata-d1-d6-modalità-profilo), che include nativamente le 4 fasi.
- Un pre-check superato non è legato a una destinazione precisa: resta valido 24 h per qualsiasi avvio Violento/Massimo successivo, non solo sulla destinazione verificata.
- La [Calibrazione locale](#calibrazione-locale) misura, ma non applica ancora automaticamente il proprio involucro sicuro per limitare un test reale — un lavoro volutamente separato, non ancora iniziato.

## Licenza

MIT — vedi `LICENSE`.
