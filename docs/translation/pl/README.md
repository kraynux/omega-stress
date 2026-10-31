<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licencja MIT (zobacz plik LICENSE) -->
<div align="center">
  <img src="../../assets/omega-stress.png" alt="Omega-Stress" width="384">
</div>

# 🗲 OMEGA-STRESS

**Stanowisko kontrolowanych testów obciążenia HTTP**

> Stworzone przez [kraynux](https://github.com/kraynux) dla [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Oficjalna strona: [OMEGA-STRESS](https://kraynux.snake-mackarel.ts.net/omega-stress/) &nbsp; Podgląd: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-stress/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interfejs i eksportowane raporty dostępne w **17 językach** — zobacz [Języki interfejsu](#języki-interfejsu).  
**Języki:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)



**Omega-Stress** to lokalna aplikacja terminalowa (TUI [Textual](https://github.com/Textualize/textual) + skryptowalne CLI), która prowadzi testy obciążenia HTTP w sposób kontrolowany i powtarzalny: zamrożone profile, historia, ponowne uruchamianie, szczegółowe eksporty (JSON/CSV/HTML), jawne granice bezpieczeństwa.

Projekt jest zbudowany zgodnie z zasadami **Clean Architecture**, z wyraźnym podziałem na domenę biznesową, orkiestrację, infrastrukturę i interfejs użytkownika.
---

## Spis treści

- [Prezentacja](#prezentacja)
- [Funkcje](#funkcje)
- [Architektura](#architektura)
- [Wymagania](#wymagania)
- [Instalacja](#instalacja)
- [Użycie](#uruchamianie)
- [Profile czasu trwania D1-D6](#profile-czasu-trwania-d1-d6-tryb-profilu)
- [Tryb bezpieczeństwa](#tryb-bezpieczeństwa)
- [Kalibracja lokalna](#kalibracja-lokalna)
- [Konfiguracja](#konfiguracja)
- [Testy i jakość](#testy-i-jakość)
- [Odinstalowanie](#odinstalowanie)
- [Znane ograniczenia](#znane-ograniczenia)
- [Licencja](#licencja)

## Prezentacja

### Cele

## Co robi Omega-Stress (cel V1)

- Trzy kontrolowane rodziny testów: **Test żądań** (przepustowość), **Test połączeń** (współbieżność), **Test obciążenia** (stopniowy wzrost).
- **8 poziomów intensywności** (Słaby/Niski/Średni/Wysoki/Mocny/Agresywny/Gwałtowny/Maksimum), z trzystopniowym modelem pre-checku (nigdy niewymagany / wymagany opcjonalnie / wymagany obowiązkowo — zobacz [Wartości testów](#wartości-testów)).
- **Dwa tryby czasu trwania**: ręczny (od 1 do 5 min, ograniczony dla poziomu) lub **nazwany profil D1-D6** (stały łączny czas z rozgrzewką/narastaniem/plateau/wyciszeniem — zobacz [Profile czasu trwania D1-D6](#profile-czasu-trwania-d1-d6-tryb-profilu)).
- **Tryb bezpieczeństwa** (domyślnie włączony, do wyłączenia przy każdym uruchomieniu): lokalne zabezpieczenia CPU/pamięci maszyny hosta, odrębne od progów chroniących testowany cel — zobacz [Tryb bezpieczeństwa](#tryb-bezpieczeństwa).
- **Trwała kalibracja lokalna**: mierzy rzeczywistą wydajność maszyny hosta (nigdy celu) za pomocą lokalnego serwera pętli zwrotnej, w stopniach rosnącego obciążenia — zobacz [Kalibracja lokalna](#kalibracja-lokalna).
- Profile zamrożone, wielokrotnego użytku, zapisywane w historii — **opcjonalne**: test działa równie dobrze w trybie ręcznym, bez żadnego profilu, przez bezpośredni wybór lub wpisanie celu.
- Obowiązkowe wyraźne potwierdzenie autoryzacji przed każdym uruchomieniem na nieprzypiętym celu.
- Progi automatycznego zatrzymania, nigdy nieograniczone obciążenie.
- Szczegółowe eksporty JSON/CSV/HTML (stopnie, metryki na interwał, werdykt, diagnoza).
- Nieinteraktywny tryb CLI do automatyzacji (cron, CI), wywołujący dokładnie te same przypadki użycia co TUI.
- Automatyczne dopasowanie do terminala (motyw + upraszczalny profil renderowania).

## Czego projekt nie robi

- Nie zastępuje narzędzia do skanowania sieci — słownictwo i postawa produktu to świadomie „test obciążenia”, nigdy „skanowanie”.
- Nie implementuje żadnego zewnętrznego silnika obciążenia (k6 itp.) — natywne generowanie `httpx`/asyncio.
- Nie uruchamia żadnego testu bez granic i bez potwierdzenia autoryzacji.
- Nie jest narzędziem do rozproszonego obciążenia: generowanie działa na jednej maszynie, w jednym procesie — zobacz [Znane ograniczenia](#znane-ograniczenia).

## Funkcje

- **Trzy rodziny testów**, każda z 8 poziomami intensywności (Słaby/Niski/Średni/Wysoki/Mocny/Agresywny/Gwałtowny/Maksimum) — zobacz tabelę [Punkty odniesienia obciążenia](#wartości-testów) z dokładnymi wartościami każdego poziomu.
- **Zamrożone profile testów**: nazwa, cel, rodzina, intensywność, czas trwania, próg błędów — tworzone raz, uruchamiane ponownie identycznie z TUI lub CLI.
- **Nazwane profile czasu trwania D1-D6** (tryb „profilu”), alternatywa dla trybu ręcznego: stały łączny czas (od 1 do 120 min) z rozgrzewką/narastaniem/plateau/wyciszeniem, który ogranicza też dostępne poziomy — zobacz [Profile czasu trwania D1-D6](#profile-czasu-trwania-d1-d6-tryb-profilu).
- **Tryb bezpieczeństwa**, domyślnie zaznaczony na każdym ekranie uruchamiania: zatrzymuje test, jeśli maszyna hosta (nie cel) wydaje się zagrożona. Można go świadomie wyłączyć, z przypomnieniem porównującym wybrany poziom z ostatnią wykonaną kalibracją — zobacz [Tryb bezpieczeństwa](#tryb-bezpieczeństwa).
- **Trwała kalibracja lokalna**: mierzy, co maszyna naprawdę wytrzymuje (7 stopni rosnącego obciążenia wobec wbudowanego lokalnego serwera pętli zwrotnej), dostępna na ekranie Kalibracja — zobacz [Kalibracja lokalna](#kalibracja-lokalna).
- **Przypięte cele**: przypięty adres zwalnia z ponownego zaznaczania autoryzacji przy każdym uruchomieniu; ostatnie nieprzypięte cele pozostają widoczne (maksymalnie 10) bez domyślnej autoryzacji. Przypięty cel można wykorzystać na dwa niezależne sposoby: bezpośrednio, aby uruchomić test w trybie ręcznym bez profilu, lub jako cel domyślny przy tworzeniu zamrożonego profilu.
- **Pełna historia**: każde uruchomienie jest zapisywane (werdykt, metryki, przebieg w interwałach, użyty tryb bezpieczeństwa); uruchomienie powiązane z zamrożonym profilem można odtworzyć identycznie.
- **Szczegółowe eksporty** w JSON (surowe dane do ponownego importu), CSV (analiza tabelaryczna) lub HTML (czytelny raport, z motywem do wyboru spośród 10 palet projektu). Raport HTML jest zapisywany w języku wybranym w Ustawieniach („Język eksportów”, domyślnie język interfejsu); JSON i CSV pozostają danymi i nie są tłumaczone.
- **Pre-check** automatyczny i obowiązkowy przed każdym testem Gwałtowny/Maksimum, opcjonalny (ale odblokowujący dłuższe czasy) na poziomach Mocny/Agresywny, z oknem ważności (24 h).
- **Podgląd na żywo** trwającego testu: wskaźnik postępu z wiarygodnym odliczaniem (pozostały czas liczony bezpośrednio, nigdy szacowany), przepustowość/błędy/opóźnienie p95 aktualizowane w każdym interwale, ręczne zatrzymanie możliwe bez opuszczania aplikacji.
- **Ustawienia w jednym miejscu**: motyw (10 palet Omega + wszystkie wbudowane motywy Textual, łącznie 31 w palecie poleceń), profil renderowania (automatyczny lub wymuszony), foldery eksportu i zrzutów ekranu, czyszczenie celów/historii.
- **Wbudowana pomoc** (klawisz `a`): skróty klawiszowe, opis każdego ekranu (w tym Kalibracja i Tryb bezpieczeństwa), tabela referencyjna wartości obciążenia i tabela profili czasu trwania D1-D6.
- **Skryptowalne CLI** (`omega-stress profile|run|history|export|calibrate ...`), dokładnie te same przypadki użycia co TUI, z wyjściem `--json` do automatyzacji.
- **Automatyczne dopasowanie do terminala**: rodzina i rozmiar wykrywane przy starcie, motyw i bogactwo wyświetlania dostosowywane odpowiednio (zobacz [Obsługiwane terminale](#obsługiwane-terminale)).

## Architektura

Clean Architecture + Ports & Adapters w 9 pakietach (`app/`, `core/`, `domain/`, `application/`, `ports/`, `infrastructure/`, `interfaces/`, `plugins/`, `shared/`).
Pełne szczegóły: `ARCHITECTURE.md`.

```text
src/omega_stress/
├── app/              Uruchamianie i kontener wstrzykiwania zależności (ręczne łączenie, bez frameworka DI)
├── core/             Wspólne słownictwo: wyliczenia, wyjątki bazowe, Result/Ok/Err, możliwości systemu
├── domain/           Czysta logika biznesowa: obciążenie, profile, uruchomienia, cele, motywy, terminal — bez operacji wejścia/wyjścia
├── application/      Orkiestracja: commands (akcje), queries (odczyty), potok wykonania (guards/hooks)
├── ports/            Kontrakty Protocol/ABC oczekiwane przez adaptery (repozytoria, eksportery, generator obciążenia...)
├── infrastructure/   Konkretne implementacje: SQLite, eksportery JSON/CSV/HTML, generator httpx/asyncio, wykrywanie terminala, sonda systemowa
├── interfaces/       Dwa niezależne adaptery prezentacji: TUI (Textual) i CLI (argparse)
├── plugins/          Zarezerwowany punkt rozszerzeń (ładowanie wtyczek) — szkielet obecny, niezaimplementowany w V1
└── shared/           Wspólne narzędzia bez zależności biznesowych (wstrzykiwalny zegar, generowanie identyfikatorów)
```

### Zasady projektowe

- `domain/` nie zawiera ani operacji wejścia/wyjścia, ani zależności od infrastruktury — czysta logika biznesowa, w pełni testowalna bez mocków.
- `application/` koordynuje przypadki użycia przez domenę i porty, nigdy bezpośrednio przez konkretną klasę z `infrastructure/`.
- `infrastructure/` implementuje porty, nigdy nie będąc importowaną bezpośrednio przez `application/` ani `domain/` — odwołują się do niej tylko `interfaces/` i `app/`.
- `interfaces/` nie może nigdy wywoływać bezpośrednio `infrastructure/` ani `subprocess`: wyłącznie przez `application/` (commands/queries) i własne kontrolery.
- `ports/` definiuje kontrakty oczekiwane przez adaptery (Protocol), nigdy implementację.
- `core/` gromadzi słownictwo wspólne dla wszystkich warstw, nigdy nie kodując w nim reguły biznesowej z liczbami (progi, czasy, presety — zawsze w `domain/*/policies.py`).

Dependency Rule (wyłącznie od warstw zewnętrznych do wewnętrznych) i izolacja technologii zewnętrznych (`textual`, `sqlite3`, `httpx`, `jinja2`, każda ograniczona do swojego wyznaczonego punktu wejścia) są automatycznie sprawdzane przy każdym uruchomieniu `lint-imports` (zobacz [Testy i jakość](#testy-i-jakość)).

## Wymagania

- Python ≥ 3.10
- Zalecany [`uv`](https://github.com/astral-sh/uv) do zarządzania zależnościami (w przeciwnym razie standardowy `pip`)

### System

- Linux, przede wszystkim Arch Linux i dystrybucje zgodne.
- Python 3.10 lub nowszy.
- Nie są potrzebne uprawnienia roota: Omega-Stress wykonuje tylko wychodzące wywołania HTTP jako zwykły użytkownik.

## Instalacja

Oficjalne archiwum jest dostarczane w formacie `.tar.gz`. Przed instalacją sprawdź jego integralność:

```bash
sha256sum omega-stress.tar.gz
```

### Metoda 1 — skrypt instalacyjny

```bash
[ -d omega-stress ] && echo "ℹ️ Już tu rozpakowano, krok pominięty." || tar -xzf omega-stress.tar.gz
[ -d ~/omega-stress ] && echo "ℹ️ ~/omega-stress już istnieje, przenoszenie pominięte." || mv omega-stress ~/
cd ~/omega-stress/
chmod +x install.sh
./install.sh
```

### Metoda 2 — pełna, odporna instalacja

To polecenie można skopiować i wkleić bez zmian i uruchomić ponownie bez błędu: każdy krok pomija to, co już zostało zrobione.

```bash
( [ -d omega-stress ] || tar -xzf omega-stress.tar.gz ) && \
( [ -d ~/omega-stress ] || mv omega-stress ~/ ) && \
cd ~/omega-stress && chmod +x install.sh && ./install.sh
```
`install.sh`:

1. Tworzy środowisko wirtualne `.venv`, jeśli jeszcze nie istnieje.
2. Instaluje zależności (`pip install -e .`; `pyproject.toml` pozostaje jedynym źródłem prawdy).
3. Nadaje plikom `omega-stress.sh` i `install.sh` prawo wykonywania.
4. Dodaje alias `stress` do `~/.bashrc` i `~/.zshrc` (bez duplikatu, jeśli już istnieje).

## Instalacja (deweloperska)

```bash
uv sync --all-extras
# lub, bez uv:
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```


### Uruchamianie

```bash
cd ~/omega-stress
./omega-stress.sh

# lub po prostu wpisz "stress" w nowym terminalu, jeśli utworzono alias
```

Program uruchamiający:

1. Wykrywa `.venv`, `venv` lub systemowy Python.
2. Ustawia `PYTHONPATH` na `src/`.
3. Uruchamia `python -m omega_stress` — bez argumentu otwiera TUI; z argumentem przekazuje sterowanie do CLI.

### Języki interfejsu

Interfejs jest dostępny w 17 językach: francuskim, angielskim, hiszpańskim, portugalskim (Brazylia), włoskim, niemieckim, niderlandzkim, polskim, rosyjskim, chińskim uproszczonym, wietnamskim, tajskim, indonezyjskim, japońskim, koreańskim, hindi i arabskim. Wyboru dokonuje się w Ustawieniach („Langue / Language”), a zmiana obowiązuje po ponownym uruchomieniu interfejsu; zmienna `OMEGA_STRESS_LANG` (na przykład `OMEGA_STRESS_LANG=pl ./omega-stress.sh`) wymusza język na czas jednej sesji. Uruchomiony z omega-suite, omega-stress przejmuje język pakietu. W tekstowej konsoli Linuksa (TTY) języki o piśmie innym niż łacińskie są na czas sesji wyświetlane po angielsku. Wiersz poleceń pozostaje po francusku.

### Użycie w CLI

```bash
omega-stress profile list                                     # lista profili
omega-stress profile create --name "Sondowanie API" --target-id t-1 \
    --family request --level bas --duration-minutes 1 --max-error-rate 0.05
omega-stress profile freeze <profile-id>                       # zamrożenie profilu

# Obowiązkowy pre-check przed każdym uruchomieniem Gwałtowny/Maksimum (opcjonalny na Mocny/Agresywny)
omega-stress run precheck --target-id t-1 --target-url https://exemple.org --confirm

omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level bas --duration-minutes 1 --max-error-rate 0.05 --confirm
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level moyen --duration-minutes 3 --max-error-rate 0.05 --confirm
omega-stress run ramp --target-id t-1 --target-url https://exemple.org \
    --level puissant --duration-minutes 3 --max-error-rate 0.05 --confirm --precheck-validated

# Tryb profilu D1-D6 zamiast --duration-minutes (wzajemnie się wykluczają)
# D4 (resilience) pozwala na Agresywny bez warunku, na Gwałtowny ze wzmocnionym potwierdzeniem
omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-preset d4 --max-error-rate 0.05 --confirm \
    --precheck-validated --confirmation-text JE_CONFIRME_LA_CIBLE_AUTORISEE

# --unsafe wyłącza tryb bezpieczeństwa (lokalne zabezpieczenia CPU/pamięci); domyślnie nieobecne
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-minutes 1 --max-error-rate 0.05 --confirm \
    --precheck-validated --unsafe

omega-stress run replay <run-id> --confirm                     # odtwarza uruchomienie powiązane z zamrożonym profilem

omega-stress history list                                      # historia uruchomień
omega-stress history show <run-id>                              # szczegóły uruchomienia

omega-stress export <run-id> --format html --destination var/exports --theme omega-base

omega-stress calibrate run                                      # uruchamia kalibrację tej maszyny
omega-stress calibrate show                                     # pokazuje ostatnią znaną kalibrację
```

Wartości `--level` (`faible`, `bas`, `moyen`, `haut`, `puissant`, `agressif`, `violent`, `maximum`) i tekst potwierdzenia pozostają po francusku, jak reszta wiersza poleceń.

`--confirm` to wierszopoleceniowy odpowiednik pola autoryzacji w TUI: wymagany dla każdego celu, który nie jest jeszcze przypięty jako autoryzowany. Identyczne `--target-id`/`--target-url` oznaczają cel ręczny (nieprzypięty); użyj identyfikatora już przypiętego celu, aby nie podawać `--confirm` przy każdym uruchomieniu.

Dodaj `--json` do `history`/`export`/`calibrate`, aby uzyskać wyjście czytelne maszynowo, przydatne w cron/CI.

### Ogólny przebieg

1. Przy pierwszym uruchomieniu ekran startowy oferuje: Profile, Test żądań, Test połączeń, Test obciążenia, Historia, Cele, Kalibracja, Ustawienia, Pomoc.
2. Na ekranie testu u góry wciąż można wybrać zamrożony profil (opcjonalny): dwa sposoby podania celu i kryteriów, nigdy łączone w jednym uruchomieniu —
   - **z profilem**: jego wybór wypełnia cel/intensywność/czas/próg błędów, a pole celu ręcznego znika (traci wtedy sens); wypełnione wartości można zmienić przed uruchomieniem;
   - **bez profilu (tryb ręczny)**: wybrać przypięty/ostatni cel z listy lub wpisać nowy, zaznaczyć autoryzację, jeśli nie jest jeszcze przypięty jako autoryzowany, ustawić ręcznie intensywność/czas (ręczny lub profil czasu trwania D1-D6)/próg błędów.

   W obu przypadkach: pozostawić tryb bezpieczeństwa włączony lub świadomie go wyłączyć, wykonać pre-check, jeśli wymaga go poziom, a następnie uruchomić test.
3. Wynik pojawia się od razu (werdykt, metryki, przebieg), bez przechodzenia przez Historię — eksport jest proponowany bezpośrednio na tym ekranie.
4. Profil można zamrozić, aby później uruchomić ten sam test identycznie, z ekranu Profile lub odtwarzając go z Historii.

### Wartości testów

8 poziomów intensywności, identycznych w trzech rodzinach testów (zmienia się tylko sterowany wymiar) — pełna tabela:

| Typ testu | Poziom | Sterowany wymiar | Wartość docelowa | Pre-check | Dostępne czasy (tryb ręczny) |
|---|---|---|---|---|---|
| Test żądań | Słaby | Przepustowość | 250 żąd./min (≈4,2 żąd./s) | Nie | 1 do 5 min |
| Test żądań | Niski | Przepustowość | 500 żąd./min (≈8,3 żąd./s) | Nie | 1 do 5 min |
| Test żądań | Średni | Przepustowość | 1000 żąd./min (≈16,7 żąd./s) | Nie | 1 do 5 min |
| Test żądań | Wysoki | Przepustowość | 2000 żąd./min (≈33,3 żąd./s) | Nie | 1 do 5 min |
| Test żądań | Mocny | Przepustowość | 6000 żąd./min (≈100 żąd./s) | Opcjonalny | 1 do 3 min (5 po zaliczonym pre-checku) |
| Test żądań | Agresywny | Przepustowość | 10 000 żąd./min (≈167 żąd./s) | Opcjonalny | 1 do 3 min (5 po zaliczonym pre-checku) |
| Test żądań | Gwałtowny | Przepustowość | 15 000 żąd./min (≈250 żąd./s) | **Obowiązkowy** | Tylko 1 do 3 min |
| Test żądań | Maksimum | Przepustowość | 20 000 żąd./min (≈333 żąd./s) | **Obowiązkowy** | Tylko 1 do 3 min |
| Test połączeń | Słaby | Połączenia jednoczesne | 25 połączeń | Nie | 1 do 5 min |
| Test połączeń | Niski | Połączenia jednoczesne | 50 połączeń | Nie | 1 do 5 min |
| Test połączeń | Średni | Połączenia jednoczesne | 100 połączeń | Nie | 1 do 5 min |
| Test połączeń | Wysoki | Połączenia jednoczesne | 200 połączeń | Nie | 1 do 5 min |
| Test połączeń | Mocny | Połączenia jednoczesne | 1000 połączeń | Opcjonalny | 1 do 3 min (5 po zaliczonym pre-checku) |
| Test połączeń | Agresywny | Połączenia jednoczesne | 2000 połączeń | Opcjonalny | 1 do 3 min (5 po zaliczonym pre-checku) |
| Test połączeń | Gwałtowny | Połączenia jednoczesne | 3500 połączeń | **Obowiązkowy** | Tylko 1 do 3 min |
| Test połączeń | Maksimum | Połączenia jednoczesne | 5000 połączeń | **Obowiązkowy** | Tylko 1 do 3 min |
| Test obciążenia (stopniowy wzrost) | Słaby | Przepustowość, narastająca | szczyt 250 żąd./min | Nie | 1 do 5 min |
| Test obciążenia (stopniowy wzrost) | Niski | Przepustowość, narastająca | szczyt 500 żąd./min | Nie | 1 do 5 min |
| Test obciążenia (stopniowy wzrost) | Średni | Przepustowość, narastająca | szczyt 1000 żąd./min | Nie | 1 do 5 min |
| Test obciążenia (stopniowy wzrost) | Wysoki | Przepustowość, narastająca | szczyt 2000 żąd./min | Nie | 1 do 5 min |
| Test obciążenia (stopniowy wzrost) | Mocny | Przepustowość, narastająca | szczyt 6000 żąd./min | Opcjonalny | 1 do 3 min (5 po zaliczonym pre-checku) |
| Test obciążenia (stopniowy wzrost) | Agresywny | Przepustowość, narastająca | szczyt 10 000 żąd./min | Opcjonalny | 1 do 3 min (5 po zaliczonym pre-checku) |
| Test obciążenia (stopniowy wzrost) | Gwałtowny | Przepustowość, narastająca | szczyt 15 000 żąd./min | **Obowiązkowy** | Tylko 1 do 3 min |
| Test obciążenia (stopniowy wzrost) | Maksimum | Przepustowość, narastająca | szczyt 20 000 żąd./min | **Obowiązkowy** | Tylko 1 do 3 min |

- **Pre-check Nie**: test startuje od razu, bez warunku dotyczącego czasu.
- **Pre-check Opcjonalny** (Mocny/Agresywny): test startuje bez pre-checku (czasy 1-3 min), ale zaliczony pre-check odblokowuje też czasy 4-5 min.
- **Pre-check Obowiązkowy** (Gwałtowny/Maksimum): test nie wystartuje bez wcześniej zaliczonego pre-checku; czas pozostaje ograniczony do 3 min nawet z pre-checkiem (tu pre-check warunkuje dostęp do poziomu, a nie dłuższy czas).

Kolumna „Dostępne czasy” powyżej dotyczy tylko **trybu ręcznego** (maksymalnie 5 min). Powyżej tej granicy tylko [tryb profilu D1-D6](#profile-czasu-trwania-d1-d6-tryb-profilu) pozwala na dłuższe testy (do 120 min) — każdy profil D1-D6 sam określa, które poziomy pozostają dostępne przy tym czasie (`free_max_level`/`reinforced_level`, zobacz jego tabelę):

| Poziom | Maks. czas w trybie ręcznym | Maks. czas w profilu D1-D6 |
|---|---|---|
| Słaby / Niski / Średni / Wysoki | 5 min | 120 min (D6, tylko Połączenia/Obciążenie); 60 min dla Żądań (D5, D6 niezgodny z tą rodziną) |
| Mocny | 5 min (3 min bez pre-checku) | 120 min ze wzmocnionym potwierdzeniem (D6, Połączenia/Obciążenie) lub 60 min bez (D5) |
| Agresywny | 5 min (3 min bez pre-checku) | 60 min ze wzmocnionym potwierdzeniem (D5) lub 30 min bez (D4) |
| Gwałtowny | 3 min (pre-check obowiązkowy) | 30 min ze wzmocnionym potwierdzeniem (D4) lub 15 min bez (D3) |
| Maksimum | 3 min (pre-check obowiązkowy) | maksymalnie 5 min (tylko D1/D2 — żaden profil D3-D6 nie oferuje Maksimum, nawet z potwierdzeniem) |

Ta sama tabela jest dostępna bezpośrednio w aplikacji (Pomoc → Punkty odniesienia obciążenia), zawsze generowana z tych samych wartości referencyjnych (`domain/load/presets.py`, `domain/load/policies.py`) — nigdy nie powielana ręcznie.

> W Teście obciążenia w **trybie ręcznym** narastanie i plateau są automatycznie skalowane do wybranego czasu (z zachowaniem proporcji presetu): test 1-minutowy przechodzi przez całą krzywą, od 0 do szczytu, a nie tylko przez jej początek. W **trybie profilu D1-D6** tę samą gwarancję zapewnia natywnie podział każdego profilu na rozgrzewkę/narastanie/plateau/wyciszenie — zobacz [Profile czasu trwania D1-D6](#profile-czasu-trwania-d1-d6-tryb-profilu).

### Nawigacja

- Strzałki w górę/dół: przesuwanie kursora.
- `Tab` / `Shift+Tab`: przechodzenie między polami formularza.
- `Esc`: powrót (potwierdzenie wyjścia z ekranu startowego).
- `a`: wyświetlenie pomocy.
- `t`: zmiana motywu.
- `q`: wyjście (z potwierdzeniem).
- `r`: odświeża wyświetlanie, przydatne po zmianie rozmiaru terminala.
- `Ctrl+P`: paleta poleceń (zmiana motywu, zrzut ekranu, pomoc do skrótów).

Przełączaj motywy klawiszem `t`: Omega-Stress automatycznie dopasowuje kolory i bogactwo wyświetlania do wykrytych możliwości terminala, na każdym ekranie. W palecie poleceń (`Ctrl+P` → Motyw) dostępnych jest wszystkie 31 motywów (10 motywów Omega + 21 wbudowanych motywów Textual).

### Obsługiwane terminale

Cztery profile renderowania, od najbogatszego do najbardziej uproszczonego: **Pełny**, **Standardowy**, **Ograniczony**, **Mono**. Wybierany jest bardziej restrykcyjny profil spośród wykrytej rodziny terminala i rzeczywistego rozmiaru okna (nigdy bogatszy niż którakolwiek z dwóch granic).

| Terminal | Profil domyślny |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | Pełny |
| Konsole, GNOME Terminal, Terminator, xfce4-terminal | Standardowy |
| urxvt, xterm | Ograniczony |
| TTY Linuksa | Mono |
| SSH (wykryty true color/256 kolorów) | Ograniczony |
| SSH (minimalny sygnał) | Mono |
| Nierozpoznany terminal | Ograniczony (ostrożna wartość zapasowa) |

Poniżej 80 kolumn × 24 wierszy przed ekranem startowym pojawia się ekran ostrzeżenia (nigdy blokujący: aplikacja pozostaje użyteczna w trybie uproszczonym). Konsole, GNOME Terminal i Terminator są rozpoznawane po własnej charakterystycznej zmiennej środowiskowej (`KONSOLE_VERSION`, `GNOME_TERMINAL_SCREEN`/`GNOME_TERMINAL_SERVICE`, `TERMINATOR_UUID`), a nie po `TERM`, które pozostawiają z ogólną wartością zgodności — xfce4-terminal nie ustawia dotąd żadnego znanego odpowiednika, więc trafia do tego samego profilu Standardowy tylko wtedy, gdy udostępnia rozpoznawalną wartość `TERM`/`TERM_PROGRAM`; w przeciwnym razie do profilu Ograniczony.

### Ścieżki wewnętrzne i systemowe

Domyślnie Omega-Stress pracuje we własnym folderze `var/`, względnym wobec katalogu, z którego jest uruchamiany (lub `$OMEGA_STRESS_VAR_DIR`, jeśli jest ustawiona):

```text
var/db/app.db           # baza SQLite (profile, cele, historia)
var/settings.json       # zapisane ustawienia (motyw, profil renderowania, foldery domyślne)
var/exports/            # domyślne eksporty JSON/CSV/HTML
var/screenshots/        # domyślne zrzuty ekranu SVG (paleta poleceń)
var/audit.jsonl         # dziennik audytu (jeden wiersz na uruchomienie)
var/app.log             # dziennik aplikacji
```

Bezwzględna ścieżka systemowa (np. `/var/exports/`) nigdy nie jest używana domyślnie — początkowy `/` ma więc znaczenie: poza folder trafia tylko jawny eksport do folderu wybranego przez użytkownika (Ustawienia lub ekran Eksport).

## Profile czasu trwania D1-D6 (tryb profilu)

Alternatywa dla trybu ręcznego (czas 1-5 min ograniczony dla poziomu): **nazwany profil czasu trwania** ze stałym łącznym czasem i wewnętrznym podziałem na 4 fazy (rozgrzewka, narastanie, plateau, wyciszenie). Do wyboru na każdym ekranie uruchamiania (przełącznik „Tryb czasu trwania: Ręczny / Profil D1-D6”) i w CLI przez `--duration-preset`.

| Profil | Łączny czas | Rozgrzewka | Narastanie | Plateau | Wyciszenie | Maks. poziom bez potwierdzenia | Dodatkowy poziom (wzmocnione potwierdzenie) | Zgodne rodziny |
|---|---|---|---|---|---|---|---|---|
| D1 (quick) | 1 min | 5 s | 10 s | 40 s | 5 s | Maksimum | — | Żądania, Połączenia, Obciążenie |
| D2 (short) | 5 min | 15 s | 30 s | 4 min | 15 s | Maksimum | — | Żądania, Połączenia, Obciążenie |
| D3 (standard) | 15 min | 30 s | 1 min 30 | 12 min 30 | 30 s | Gwałtowny | — | Żądania, Połączenia, Obciążenie |
| D4 (resilience) | 30 min | 1 min | 3 min | 25 min | 1 min | Agresywny | Gwałtowny | Żądania, Połączenia, Obciążenie |
| D5 (extended) | 60 min | 2 min | 5 min | 51 min | 2 min | Mocny | Agresywny | Żądania, Połączenia, Obciążenie |
| D6 (soak) | 120 min | 3 min | 10 min | 104 min | 3 min | Wysoki | Mocny | Połączenia, Obciążenie (nigdy Żądania) |

- Poziom „dodatkowy” (D4-D6) jest dostępny tylko po wpisaniu dokładnie wyświetlonego na ekranie tekstu wzmocnionego potwierdzenia — nigdy przez zwykłe pole wyboru.
- D6 wyklucza Test żądań: test przepustowości jest ograniczany wolumenem, co nigdy nie ma sensu w 2-godzinnym profilu skupionym na dryfie w czasie.
- Ta sama tabela jest dostępna w aplikacji (Pomoc → Profile czasu trwania D1-D6).

## Tryb bezpieczeństwa

Pole wyboru obecne na każdym ekranie uruchamiania (domyślnie zaznaczone), które przełącza **wyłącznie** zabezpieczenia chroniące maszynę uruchamiającą Omega-Stress (CPU/pamięć lokalnego generatora):

- **Zawsze aktywne, niezależnie od tego ustawienia**: progi chroniące **testowany cel** (odsetek błędów, opóźnienie) — ich wyłączanie nigdy nie ma sensu dla produktu; to nie one są objęte tym polem.
- **Tryb bezpieczeństwa włączony (domyślnie)**: test zatrzymuje się automatycznie, jeśli sama maszyna hosta wydaje się przeciążona (CPU generatora I ogólne CPU maszyny wysokie jednocześnie, a nie tylko jedno z nich — normalne nasycenie jednego rdzenia nigdy samo nie wystarcza).
- **Tryb bezpieczeństwa wyłączony**: to lokalne zabezpieczenie zostaje usunięte. Wyświetla się wtedy przypomnienie porównujące wybrany poziom z ostatnią znaną kalibracją tej maszyny (zobacz [Kalibracja lokalna](#kalibracja-lokalna)) — przekroczenie tej obwiedni pozostaje możliwe, ale wiarygodność wyniku i stabilność maszyny stają się odpowiedzialnością użytkownika.

Dostępne także w CLI przez `--unsafe` (domyślnie nieobecne = tryb bezpieczeństwa włączony).

## Kalibracja lokalna

Mierzy rzeczywistą wydajność **tej maszyny** (nigdy testowanego celu): lokalny serwer pętli zwrotnej wbudowany w Omega-Stress otrzymuje rosnące stopniowo obciążenie, generowane przez ten sam silnik `httpx`/asyncio co prawdziwe testy.

- 7 stopni, od spoczynku (szum tła systemu) do 2000 połączeń / 12 000 żąd./s, każdy oceniany względem progów kondycji (CPU generatora I ogólne, dostępna pamięć, odsetek błędów, osiągnięta przepustowość) — ostatnie 2 stopnie są warunkowe i pomijane, jeśli poprzedni stopień nie był w dobrej kondycji.
- Wyznacza bezpieczną obwiednię (`VU_safe` / `RPS_safe`) na podstawie ostatniego zdrowego stopnia, z marginesem bezpieczeństwa (~30 % rezerwy) i poziomem pewności rosnącym wraz z osiągniętą głębokością.
- **W V1 tylko pomiar**: wynik nie jest stosowany automatycznie do ograniczania prawdziwego testu — służy jako punkt odniesienia, zwłaszcza gdy [Tryb bezpieczeństwa](#tryb-bezpieczeństwa) jest wyłączony.
- Zapisywana dla każdej maszyny (nieinwazyjny odcisk: system/architektura/liczba rdzeni/RAM, nigdy adres sprzętowy), dostępna w każdej chwili bez ponownego pomiaru.

Dostępna z ekranu **Kalibracja** w TUI (przycisk „Uruchom kalibrację”, postęp pokazywany co sekundę) lub w CLI:

```bash
omega-stress calibrate run     # uruchamia nową kalibrację
omega-stress calibrate show    # pokazuje ostatnią znaną kalibrację, bez uruchamiania nowej
```

## Konfiguracja

Wszystko ustawia się na ekranie **Ustawienia** w TUI (bez ręcznej edycji plików konfiguracyjnych):

- **Motyw**: jeden z 10 motywów Omega, stosowany od razu i zapisywany.
- **Profil renderowania**: Automatyczny (wykrywanie przy starcie) lub wymuszony ręcznie (Pełny/Standardowy/Ograniczony/Mono).
- **Domyślny folder eksportu**: wypełnia pole „miejsce docelowe” ekranu Eksport.
- **Domyślny folder zrzutów ekranu**: używany przez polecenie „Zrzut ekranu” palety (`Ctrl+P`).
- **Czyszczenie**: ostatnie cele (nigdy przypięte), wszystkie cele (łącznie z przypiętymi i ich autoryzacjami) lub cała historia — każde chronione osobnym potwierdzeniem.

Ustawienia są zapisywane w `var/settings.json`. Sam katalog główny `var/` można przekierować zmienną środowiskową `OMEGA_STRESS_VAR_DIR` (przydatne do izolowania kilku instancji lub do testów).

## Testy i jakość

```bash
pytest
ruff check .
mypy src
lint-imports   # sprawdza Dependency Rule (zobacz pyproject.toml [tool.importlinter])
```

Zestaw obejmuje ponad 570 testów (jednostkowych, integracyjnych, TUI, CLI). `lint-imports` przerywa CI, jeśli naruszono Dependency Rule lub izolację technologii zewnętrznych — zobacz [Architektura](#architektura).

## Odinstalowanie

Omega-Stress nie dotyka niczego poza własnym folderem i opcjonalną linią aliasu:

```bash
rm -rf ~/omega-stress
sed -i '/alias stress=/d' ~/.bashrc ~/.zshrc
```

`install.sh` nie tworzy żadnego pakietu systemowego, usługi ani pliku poza `~/omega-stress/` — dodatkowe odinstalowywanie nie jest potrzebne.

## Znane ograniczenia

- Generowanie obciążenia **w obrębie jednego procesu**, na jednej maszynie (`httpx`/asyncio): to nie jest narzędzie rozproszone — rzeczywiste granice (zobacz [Wartości testów](#wartości-testów)) są wyraźnie skromniejsze niż w usłudze SaaS do testów obciążenia (loader.io itp.), celowo, w ramach kontrolowanej postawy produktu. Na skromnym sprzęcie poziomy Agresywny/Gwałtowny/Maksimum w Teście połączeń mogą potrzebować znacznie więcej czasu rzeczywistego niż wybrany czas trwania, aby wysłać całe zamierzone obciążenie — przepustowość ogranicza wtedy wydajność **tej maszyny**, a nie celu; użyj [Kalibracji lokalnej](#kalibracja-lokalna), aby poznać rozsądne wartości dla swojego sprzętu.
- Automatyczne wykrywanie rodziny terminala opiera się na zmiennych środowiskowych: xfce4-terminal nie ma dotąd żadnego znanego niezawodnego znacznika (zobacz [Obsługiwane terminale](#obsługiwane-terminale)).
- `plugins/` to punkt rozszerzeń przewidziany w architekturze (ładowanie wtyczek wbudowanych/zewnętrznych), niezaimplementowany w V1: szkielet istnieje, nie jest dostarczana żadna wtyczka.
- `var/` jest względny wobec folderu projektu (nie XDG): pomyślany do lokalnego użytku przez jednego użytkownika, a nie do współdzielenia przez wielu użytkowników tej samej maszyny.
- Test obciążenia (stopniowy wzrost) w **trybie ręcznym** nie ma stopnia schodzenia („cooldown”) po plateau — dostępny jest on tylko w [profilu czasu trwania D1-D6](#profile-czasu-trwania-d1-d6-tryb-profilu), który natywnie obejmuje 4 fazy.
- Zaliczony pre-check nie jest powiązany z konkretnym celem: pozostaje ważny przez 24 h dla każdego kolejnego uruchomienia Gwałtowny/Maksimum, nie tylko dla sprawdzonego celu.
- [Kalibracja lokalna](#kalibracja-lokalna) mierzy, ale jeszcze nie stosuje automatycznie swojej bezpiecznej obwiedni do ograniczania prawdziwego testu — to celowo osobne, jeszcze nierozpoczęte zadanie.

## Licencja

MIT — zobacz `LICENSE`.
