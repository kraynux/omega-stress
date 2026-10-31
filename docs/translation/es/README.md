<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licencia MIT (ver el archivo LICENSE) -->
<div align="center">
  <img src="../../assets/omega-stress.png" alt="Omega-Stress" width="384">
</div>

# 🗲 OMEGA-STRESS

**Puesto de pruebas de carga HTTP controladas**

> Desarrollado por [kraynux](https://github.com/kraynux) para [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Página oficial: [OMEGA-STRESS](https://kraynux.snake-mackarel.ts.net/omega-stress/) &nbsp; Capturas: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-stress/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interfaz e informes exportados disponibles en **17 idiomas** — ver [Idiomas de la interfaz](#idiomas-de-la-interfaz).  
**Idiomas:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)



**Omega-Stress** es una aplicación local de terminal (TUI [Textual](https://github.com/Textualize/textual) + CLI scriptable) que dirige pruebas de carga HTTP de forma controlada y reutilizable: perfiles congelados, historial, relanzamiento, exportaciones detalladas (JSON/CSV/HTML), límites de seguridad explícitos.

El proyecto sigue los principios de la **Clean Architecture**, con una separación clara entre dominio de negocio, orquestación, infraestructura e interfaz de usuario.
---

## Índice

- [Presentación](#presentación)
- [Funcionalidades](#funcionalidades)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#lanzamiento)
- [Perfiles de duración D1-D6](#perfiles-de-duración-d1-d6-modo-perfil)
- [Modo seguridad](#modo-seguridad)
- [Calibrado local](#calibrado-local)
- [Configuración](#configuración)
- [Pruebas y calidad](#pruebas-y-calidad)
- [Desinstalación](#desinstalación)
- [Limitaciones conocidas](#limitaciones-conocidas)
- [Licencia](#licencia)

## Presentación

### Objetivos

## Lo que hace Omega-Stress (objetivo V1)

- Tres familias de prueba controladas: **Prueba de peticiones** (caudal), **Prueba de conexiones** (simultaneidad), **Prueba de carga** (subida progresiva).
- **8 niveles de intensidad** (Débil/Bajo/Medio/Alto/Potente/Agresivo/Violento/Máximo), con un modelo de pre-check en 3 escalones (nunca exigido / exigido opcional / exigido obligatorio — ver [Valores de las pruebas](#valores-de-las-pruebas)).
- **Dos modos de duración**: manual (de 1 a 5 min, limitado por nivel) o **perfil con nombre D1-D6** (duración total fija con calentamiento/rampa/meseta/vuelta a la calma — ver [Perfiles de duración D1-D6](#perfiles-de-duración-d1-d6-modo-perfil)).
- **Modo seguridad** (activo por defecto, desactivable en cada lanzamiento): salvaguardas locales de CPU/memoria de la máquina anfitriona, distintas de los umbrales que protegen el objetivo probado — ver [Modo seguridad](#modo-seguridad).
- **Calibrado local persistente**: mide la capacidad real de la máquina anfitriona (nunca del objetivo) mediante un servidor de bucle local, en escalones de carga creciente — ver [Calibrado local](#calibrado-local).
- Perfiles congelados, reutilizables y registrados en el historial — **opcionales**: una prueba se lanza igual de bien en modo manual, sin ningún perfil, eligiendo o introduciendo directamente un objetivo.
- Confirmación explícita de autorización obligatoria antes de cualquier ejecución sobre un objetivo no fijado.
- Umbrales de parada automática, nunca una carga sin límites.
- Exportaciones JSON/CSV/HTML detalladas (escalones, métricas por intervalo, veredicto, diagnóstico).
- Modo CLI no interactivo para automatización (cron, CI), que llama exactamente a los mismos casos de uso que la TUI.
- Adaptación automática al terminal (tema + perfil de renderizado degradable).

## Lo que el proyecto no hace

- No sustituye a una herramienta de escaneo de red — vocabulario y postura del producto asumidos como «prueba de carga», nunca «escaneo».
- No implementa ningún motor de carga externo (k6, etc.) — generación nativa `httpx`/asyncio.
- No inicia ninguna ejecución sin límites ni confirmación de autorización.
- No es una herramienta de carga distribuida: la generación se ejecuta en una sola máquina, en un solo proceso — ver [Limitaciones conocidas](#limitaciones-conocidas).

## Funcionalidades

- **Tres familias de prueba**, cada una con 8 niveles de intensidad (Débil/Bajo/Medio/Alto/Potente/Agresivo/Violento/Máximo) — ver la tabla [Referencias de carga](#valores-de-las-pruebas) para los valores exactos de cada nivel.
- **Perfiles de prueba congelados**: nombre, objetivo, familia, intensidad, duración, umbral de error — creados una vez y relanzados de forma idéntica desde la TUI o la CLI.
- **Perfiles de duración con nombre D1-D6** (modo «perfil»), alternativa al modo manual: una duración total fija (de 1 a 120 min) con calentamiento/rampa/meseta/vuelta a la calma, que también limita los niveles accesibles — ver [Perfiles de duración D1-D6](#perfiles-de-duración-d1-d6-modo-perfil).
- **Modo seguridad**, marcado por defecto en cada pantalla de lanzamiento: detiene una prueba si la máquina anfitriona (no el objetivo) parece estar en peligro. Desactivable con conocimiento de causa, con un recordatorio que compara el nivel elegido con el último calibrado realizado — ver [Modo seguridad](#modo-seguridad).
- **Calibrado local persistente**: mide lo que la máquina puede aguantar realmente (7 escalones de carga creciente contra un servidor de bucle local integrado), consultable desde la pantalla Calibrado — ver [Calibrado local](#calibrado-local).
- **Objetivos fijados**: una dirección fijada evita volver a marcar la autorización en cada lanzamiento; los objetivos recientes no fijados siguen visibles (10 como máximo) sin autorización implícita. Un objetivo fijado se usa de dos formas, independientes entre sí: directamente, para lanzar una prueba en modo manual sin ningún perfil, o como objetivo por defecto al crear un perfil congelado.
- **Historial completo**: cada ejecución queda registrada (veredicto, métricas, cronología por intervalo, modo seguridad utilizado); una ejecución vinculada a un perfil congelado puede repetirse de forma idéntica.
- **Exportaciones detalladas** en JSON (datos brutos reimportables), CSV (análisis tabular) o HTML (informe legible, con un tema a elegir entre las 10 paletas del proyecto). El informe HTML se escribe en el idioma elegido en Ajustes («Idioma de las exportaciones», por defecto el de la interfaz); JSON y CSV siguen siendo datos, sin traducir.
- **Pre-check** automático y obligatorio antes de cualquier prueba Violento/Máximo, opcional (pero que desbloquea duraciones adicionales) en Potente/Agresivo, con un periodo de validez (24 h).
- **Seguimiento en directo** de una prueba en curso: indicador de progreso con cuenta atrás fiable (tiempo restante calculado directamente, nunca estimado), caudal/errores/latencia p95 actualizados en cada intervalo, parada manual posible sin salir de la aplicación.
- **Ajustes centralizados**: tema (10 paletas Omega + todos los temas integrados de Textual, 31 en total desde la paleta de comandos), perfil de renderizado (automático o forzado), carpetas de exportación y de capturas de pantalla, purga de objetivos/del historial.
- **Ayuda integrada** (tecla `a`): atajos de teclado, descripción de cada pantalla (incluidas Calibrado y Modo seguridad), tabla de referencia de los valores de carga y tabla de los perfiles de duración D1-D6.
- **CLI scriptable** (`omega-stress profile|run|history|export|calibrate ...`), exactamente los mismos casos de uso que la TUI, con salida `--json` disponible para la automatización.
- **Adaptación automática al terminal**: familia y tamaño detectados al arrancar, tema y riqueza de visualización ajustados en consecuencia (ver [Terminales compatibles](#terminales-compatibles)).

## Arquitectura

Clean Architecture + Ports & Adapters en 9 paquetes (`app/`, `core/`, `domain/`, `application/`, `ports/`, `infrastructure/`, `interfaces/`, `plugins/`, `shared/`).
Detalle completo: `ARCHITECTURE.md`.

```text
src/omega_stress/
├── app/              Arranque y contenedor de inyección de dependencias (cableado manual, sin framework DI)
├── core/             Vocabulario transversal: enumeraciones, excepciones raíz, Result/Ok/Err, capacidades del sistema
├── domain/           Lógica de negocio pura: carga, perfiles, ejecuciones, objetivos, temas, terminal — sin E/S
├── application/      Orquestación: commands (acciones), queries (lecturas), pipeline de ejecución (guards/hooks)
├── ports/            Contratos Protocol/ABC que esperan los adaptadores (repositorios, exportadores, generador de carga...)
├── infrastructure/   Implementaciones concretas: SQLite, exportadores JSON/CSV/HTML, generador httpx/asyncio, detección del terminal, sonda del sistema
├── interfaces/       Dos adaptadores de presentación independientes: TUI (Textual) y CLI (argparse)
├── plugins/          Punto de extensión reservado (carga de plugins) — estructura presente, no implementada en la V1
└── shared/           Utilidades transversales sin dependencia de negocio (reloj inyectable, generación de identificadores)
```

### Principios de diseño

- `domain/` no contiene ni E/S ni dependencia de la infraestructura — lógica de negocio pura, totalmente comprobable sin mocks.
- `application/` orquesta los casos de uso mediante el dominio y los puertos, nunca directamente con una clase concreta de `infrastructure/`.
- `infrastructure/` implementa los puertos sin ser nunca importada directamente por `application/` o `domain/` — solo `interfaces/` y `app/` la referencian.
- `interfaces/` nunca debe llamar directamente a `infrastructure/` ni a `subprocess`: solo a través de `application/` (commands/queries) y de sus propios controladores.
- `ports/` define los contratos que esperan los adaptadores (Protocol), nunca una implementación.
- `core/` reúne el vocabulario común a todas las capas, sin codificar nunca una regla de negocio con cifras (umbrales, duraciones, presets — siempre en `domain/*/policies.py`).

La Dependency Rule (de las capas externas a las internas únicamente) y el aislamiento de las tecnologías de terceros (`textual`, `sqlite3`, `httpx`, `jinja2`, cada una limitada a su punto de entrada designado) se comprueban automáticamente en cada ejecución de `lint-imports` (ver [Pruebas y calidad](#pruebas-y-calidad)).

## Requisitos

- Python ≥ 3.10
- [`uv`](https://github.com/astral-sh/uv) recomendado para gestionar las dependencias (si no, `pip` estándar)

### Sistema

- Linux, en prioridad Arch Linux y distribuciones compatibles.
- Python 3.10 o superior.
- No hace falta ningún privilegio de root: Omega-Stress solo realiza llamadas HTTP salientes como usuario normal.

## Instalación

El archivo oficial se distribuye en formato `.tar.gz`. Compruebe su integridad antes de instalar:

```bash
sha256sum omega-stress.tar.gz
```

### Método 1 — script de instalación

```bash
[ -d omega-stress ] && echo "ℹ️ Ya extraído aquí, paso omitido." || tar -xzf omega-stress.tar.gz
[ -d ~/omega-stress ] && echo "ℹ️ ~/omega-stress ya existe, traslado omitido." || mv omega-stress ~/
cd ~/omega-stress/
chmod +x install.sh
./install.sh
```

### Método 2 — instalación completa resiliente

Este comando puede copiarse y pegarse tal cual y volver a ejecutarse sin error: cada paso omite lo que ya se ha hecho.

```bash
( [ -d omega-stress ] || tar -xzf omega-stress.tar.gz ) && \
( [ -d ~/omega-stress ] || mv omega-stress ~/ ) && \
cd ~/omega-stress && chmod +x install.sh && ./install.sh
```
`install.sh`:

1. Crea el entorno virtual `.venv` si aún no existe.
2. Instala las dependencias (`pip install -e .`; `pyproject.toml` sigue siendo la única fuente de verdad).
3. Hace ejecutables `omega-stress.sh` e `install.sh`.
4. Añade el alias `stress` a `~/.bashrc` y `~/.zshrc` (sin duplicado si ya está presente).

## Instalación (desarrollo)

```bash
uv sync --all-extras
# o, sin uv:
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```


### Lanzamiento

```bash
cd ~/omega-stress
./omega-stress.sh

# o simplemente escriba "stress" en un terminal nuevo si se creó el alias
```

El lanzador:

1. Detecta `.venv`, `venv` o el Python del sistema.
2. Configura `PYTHONPATH` hacia `src/`.
3. Ejecuta `python -m omega_stress` — sin argumentos abre la TUI; con un argumento, pasa a la CLI.

### Idiomas de la interfaz

La interfaz está disponible en 17 idiomas: francés, inglés, español, portugués (Brasil), italiano, alemán, neerlandés, polaco, ruso, chino simplificado, vietnamita, tailandés, indonesio, japonés, coreano, hindi y árabe. La elección se hace en Ajustes («Langue / Language») y se aplica tras reiniciar la interfaz; la variable `OMEGA_STRESS_LANG` (por ejemplo `OMEGA_STRESS_LANG=es ./omega-stress.sh`) fuerza un idioma durante una sesión. Lanzado desde omega-suite, omega-stress adopta el idioma de la suite. En una consola de texto Linux (TTY), los idiomas de escritura no latina se muestran en inglés durante la sesión. La línea de comandos sigue en francés.

### Uso en CLI

```bash
omega-stress profile list                                     # listar los perfiles
omega-stress profile create --name "Sondeo API" --target-id t-1 \
    --family request --level bas --duration-minutes 1 --max-error-rate 0.05
omega-stress profile freeze <profile-id>                       # congelar un perfil

# Pre-check obligatorio antes de cualquier lanzamiento Violento/Máximo (opcional en Potente/Agresivo)
omega-stress run precheck --target-id t-1 --target-url https://exemple.org --confirm

omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level bas --duration-minutes 1 --max-error-rate 0.05 --confirm
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level moyen --duration-minutes 3 --max-error-rate 0.05 --confirm
omega-stress run ramp --target-id t-1 --target-url https://exemple.org \
    --level puissant --duration-minutes 3 --max-error-rate 0.05 --confirm --precheck-validated

# Modo perfil D1-D6, en lugar de --duration-minutes (mutuamente excluyentes)
# D4 (resilience) permite Agresivo sin condición y Violento con confirmación reforzada
omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-preset d4 --max-error-rate 0.05 --confirm \
    --precheck-validated --confirmation-text JE_CONFIRME_LA_CIBLE_AUTORISEE

# --unsafe desactiva el modo seguridad (salvaguardas locales de CPU/memoria); ausente por defecto
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-minutes 1 --max-error-rate 0.05 --confirm \
    --precheck-validated --unsafe

omega-stress run replay <run-id> --confirm                     # repite una ejecución vinculada a un perfil congelado

omega-stress history list                                      # historial de ejecuciones
omega-stress history show <run-id>                              # detalle de una ejecución

omega-stress export <run-id> --format html --destination var/exports --theme omega-base

omega-stress calibrate run                                      # lanza un calibrado de esta máquina
omega-stress calibrate show                                     # muestra el último calibrado conocido
```

Los valores de `--level` (`faible`, `bas`, `moyen`, `haut`, `puissant`, `agressif`, `violent`, `maximum`) y el texto de confirmación siguen en francés, como el resto de la línea de comandos.

`--confirm` es el equivalente en línea de comandos de la casilla de autorización de la TUI: obligatorio para cualquier objetivo que no esté ya fijado como autorizado. Un `--target-id`/`--target-url` idéntico indica un objetivo manual (no fijado); use el identificador de un objetivo ya fijado para evitar `--confirm` en cada lanzamiento.

Añada `--json` a `history`/`export`/`calibrate` para una salida legible por máquina, aprovechable en cron/CI.

### Recorrido general

1. En el primer lanzamiento, la pantalla de inicio ofrece: Perfiles, Prueba de peticiones, Prueba de conexiones, Prueba de carga, Historial, Objetivos, Calibrado, Ajustes, Ayuda.
2. Desde una pantalla de prueba, un perfil congelado (opcional) sigue pudiendo seleccionarse arriba de la pantalla: dos formas de indicar el objetivo y los criterios, nunca combinadas en un mismo lanzamiento —
   - **con un perfil**: seleccionarlo rellena objetivo/intensidad/duración/umbral de error y el campo de objetivo manual desaparece (ya no tiene sentido); los valores rellenados siguen siendo modificables antes de lanzar;
   - **sin perfil (modo manual)**: elegir un objetivo fijado/reciente de la lista o introducir uno nuevo, marcar la autorización si no está ya fijado como autorizado, ajustar a mano intensidad/duración (manual o perfil de duración D1-D6)/umbral de error.

   En ambos casos: dejar activo el modo seguridad o desactivarlo con conocimiento de causa, lanzar un pre-check si el nivel lo exige y después lanzar la prueba.
3. El resultado se muestra de inmediato (veredicto, métricas, cronología), sin pasar por el Historial — se ofrece una exportación directamente desde esta pantalla.
4. Un perfil puede congelarse para volver a lanzar la misma prueba de forma idéntica más adelante, desde la pantalla Perfiles o repitiéndola desde el Historial.

### Valores de las pruebas

8 niveles de intensidad, idénticos en las tres familias de prueba (solo cambia la dimensión controlada) — tabla completa:

| Tipo de prueba | Nivel | Dimensión controlada | Valor objetivo | Pre-check | Duraciones disponibles (modo manual) |
|---|---|---|---|---|---|
| Prueba de peticiones | Débil | Caudal | 250 pet/min (≈4,2 pet/s) | No | 1 a 5 min |
| Prueba de peticiones | Bajo | Caudal | 500 pet/min (≈8,3 pet/s) | No | 1 a 5 min |
| Prueba de peticiones | Medio | Caudal | 1000 pet/min (≈16,7 pet/s) | No | 1 a 5 min |
| Prueba de peticiones | Alto | Caudal | 2000 pet/min (≈33,3 pet/s) | No | 1 a 5 min |
| Prueba de peticiones | Potente | Caudal | 6000 pet/min (≈100 pet/s) | Opcional | 1 a 3 min (5 con pre-check superado) |
| Prueba de peticiones | Agresivo | Caudal | 10 000 pet/min (≈167 pet/s) | Opcional | 1 a 3 min (5 con pre-check superado) |
| Prueba de peticiones | Violento | Caudal | 15 000 pet/min (≈250 pet/s) | **Obligatorio** | Solo 1 a 3 min |
| Prueba de peticiones | Máximo | Caudal | 20 000 pet/min (≈333 pet/s) | **Obligatorio** | Solo 1 a 3 min |
| Prueba de conexiones | Débil | Conexiones simultáneas | 25 conexiones | No | 1 a 5 min |
| Prueba de conexiones | Bajo | Conexiones simultáneas | 50 conexiones | No | 1 a 5 min |
| Prueba de conexiones | Medio | Conexiones simultáneas | 100 conexiones | No | 1 a 5 min |
| Prueba de conexiones | Alto | Conexiones simultáneas | 200 conexiones | No | 1 a 5 min |
| Prueba de conexiones | Potente | Conexiones simultáneas | 1000 conexiones | Opcional | 1 a 3 min (5 con pre-check superado) |
| Prueba de conexiones | Agresivo | Conexiones simultáneas | 2000 conexiones | Opcional | 1 a 3 min (5 con pre-check superado) |
| Prueba de conexiones | Violento | Conexiones simultáneas | 3500 conexiones | **Obligatorio** | Solo 1 a 3 min |
| Prueba de conexiones | Máximo | Conexiones simultáneas | 5000 conexiones | **Obligatorio** | Solo 1 a 3 min |
| Prueba de carga (subida progresiva) | Débil | Caudal, en rampa | pico de 250 pet/min | No | 1 a 5 min |
| Prueba de carga (subida progresiva) | Bajo | Caudal, en rampa | pico de 500 pet/min | No | 1 a 5 min |
| Prueba de carga (subida progresiva) | Medio | Caudal, en rampa | pico de 1000 pet/min | No | 1 a 5 min |
| Prueba de carga (subida progresiva) | Alto | Caudal, en rampa | pico de 2000 pet/min | No | 1 a 5 min |
| Prueba de carga (subida progresiva) | Potente | Caudal, en rampa | pico de 6000 pet/min | Opcional | 1 a 3 min (5 con pre-check superado) |
| Prueba de carga (subida progresiva) | Agresivo | Caudal, en rampa | pico de 10 000 pet/min | Opcional | 1 a 3 min (5 con pre-check superado) |
| Prueba de carga (subida progresiva) | Violento | Caudal, en rampa | pico de 15 000 pet/min | **Obligatorio** | Solo 1 a 3 min |
| Prueba de carga (subida progresiva) | Máximo | Caudal, en rampa | pico de 20 000 pet/min | **Obligatorio** | Solo 1 a 3 min |

- **Pre-check No**: la prueba arranca directamente, sin condición de duración.
- **Pre-check Opcional** (Potente/Agresivo): la prueba arranca sin pre-check (duraciones de 1-3 min), pero un pre-check superado desbloquea también las duraciones de 4-5 min.
- **Pre-check Obligatorio** (Violento/Máximo): la prueba no arranca sin un pre-check superado previamente; la duración sigue limitada a 3 min incluso con pre-check (aquí el pre-check condiciona el acceso al nivel, no una duración ampliada).

La columna «Duraciones disponibles» solo cubre el **modo manual** (5 min como máximo). Más allá, solo el [modo perfil D1-D6](#perfiles-de-duración-d1-d6-modo-perfil) permite pruebas más largas (hasta 120 min) — cada perfil D1-D6 fija él mismo qué niveles siguen accesibles con esa duración (`free_max_level`/`reinforced_level`, ver su propia tabla):

| Nivel | Duración máx. en modo manual | Duración máx. con un perfil D1-D6 |
|---|---|---|
| Débil / Bajo / Medio / Alto | 5 min | 120 min (D6, solo Conexiones/Carga); 60 min en Peticiones (D5, D6 no compatible con esta familia) |
| Potente | 5 min (3 min sin pre-check) | 120 min con confirmación reforzada (D6, Conexiones/Carga) o 60 min sin ella (D5) |
| Agresivo | 5 min (3 min sin pre-check) | 60 min con confirmación reforzada (D5) o 30 min sin ella (D4) |
| Violento | 3 min (pre-check obligatorio) | 30 min con confirmación reforzada (D4) o 15 min sin ella (D3) |
| Máximo | 3 min (pre-check obligatorio) | 5 min como máximo (solo D1/D2 — ningún perfil D3-D6 ofrece Máximo, ni siquiera con confirmación) |

Esta misma tabla está disponible directamente en la aplicación (Ayuda → Referencias de carga), generada siempre a partir de los mismos valores de referencia (`domain/load/presets.py`, `domain/load/policies.py`) — nunca duplicada a mano.

> En la Prueba de carga en **modo manual**, la rampa y la meseta se ajustan automáticamente a la duración elegida (manteniendo las proporciones del preset): una prueba de 1 min recorre toda la curva, de 0 al pico, y no solo su comienzo. En **modo perfil D1-D6**, la misma garantía la aporta de forma nativa el reparto calentamiento/rampa/meseta/vuelta a la calma de cada perfil — ver [Perfiles de duración D1-D6](#perfiles-de-duración-d1-d6-modo-perfil).

### Navegación

- Flechas arriba/abajo: mover el cursor.
- `Tab` / `Mayús+Tab`: moverse entre los campos de un formulario.
- `Esc`: volver atrás (confirmación de salida desde la pantalla de inicio).
- `a`: mostrar la ayuda.
- `t`: cambiar de tema.
- `q`: salir (con confirmación).
- `r`: actualiza la visualización, útil tras redimensionar el terminal.
- `Ctrl+P`: paleta de comandos (cambiar de tema, captura de pantalla, ayuda de los atajos).

Cambie de tema con `t`: Omega-Stress adapta automáticamente los colores y la riqueza de visualización a las capacidades detectadas del terminal, desde cualquier pantalla. Desde la paleta de comandos (`Ctrl+P` → Tema) se ofrecen los 31 temas disponibles (10 temas Omega + 21 temas integrados de Textual).

### Terminales compatibles

Cuatro perfiles de renderizado, del más rico al más degradado: **Completo**, **Estándar**, **Reducido**, **Mono**. El perfil elegido es el más restrictivo entre la familia de terminal detectada y el tamaño real de la ventana (nunca más rico que cualquiera de los dos topes).

| Terminal | Perfil por defecto |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | Completo |
| Konsole, GNOME Terminal, Terminator, xfce4-terminal | Estándar |
| urxvt, xterm | Reducido |
| TTY de Linux | Mono |
| SSH (color real/256 colores detectados) | Reducido |
| SSH (señal mínima) | Mono |
| Terminal no reconocido | Reducido (valor de reserva prudente) |

Por debajo de 80 columnas × 24 líneas, se muestra una pantalla de aviso antes de la pantalla de inicio (nunca bloqueante: la aplicación sigue siendo utilizable, en modo degradado). Konsole, GNOME Terminal y Terminator se reconocen por su propia variable de entorno característica (`KONSOLE_VERSION`, `GNOME_TERMINAL_SCREEN`/`GNOME_TERMINAL_SERVICE`, `TERMINATOR_UUID`) y no por `TERM`, que dejan en su valor genérico de compatibilidad — xfce4-terminal no establece ningún marcador equivalente conocido hasta la fecha, por lo que solo recurre a ese mismo perfil Estándar si expone un valor `TERM`/`TERM_PROGRAM` reconocible; si no, Reducido.

### Rutas internas y rutas del sistema

Por defecto, Omega-Stress trabaja en su propia carpeta `var/`, relativa al directorio desde el que se lanza (o `$OMEGA_STRESS_VAR_DIR` si está definida):

```text
var/db/app.db           # base SQLite (perfiles, objetivos, historial)
var/settings.json       # ajustes guardados (tema, perfil de renderizado, carpetas por defecto)
var/exports/            # exportaciones JSON/CSV/HTML por defecto
var/screenshots/        # capturas de pantalla SVG por defecto (paleta de comandos)
var/audit.jsonl         # registro de auditoría (una línea por ejecución)
var/app.log             # registro de la aplicación
```

Nunca se usa por defecto una ruta absoluta del sistema (p. ej. `/var/exports/`) — la `/` inicial es, por tanto, significativa: solo una exportación explícita hacia una carpeta elegida por el usuario (Ajustes o pantalla Exportación) sale de ella.

## Perfiles de duración D1-D6 (modo perfil)

Alternativa al modo manual (duración de 1-5 min limitada por nivel): un **perfil de duración con nombre**, con una duración total fija y un reparto interno en 4 fases (calentamiento, rampa, meseta, vuelta a la calma). Seleccionable en cada pantalla de lanzamiento (conmutador «Modo de duración: Manual / Perfil D1-D6») y en CLI mediante `--duration-preset`.

| Perfil | Duración total | Calentamiento | Rampa | Meseta | Vuelta a la calma | Nivel máx. sin confirmación | Nivel adicional (confirmación reforzada) | Familias compatibles |
|---|---|---|---|---|---|---|---|---|
| D1 (quick) | 1 min | 5 s | 10 s | 40 s | 5 s | Máximo | — | Peticiones, Conexiones, Carga |
| D2 (short) | 5 min | 15 s | 30 s | 4 min | 15 s | Máximo | — | Peticiones, Conexiones, Carga |
| D3 (standard) | 15 min | 30 s | 1 min 30 | 12 min 30 | 30 s | Violento | — | Peticiones, Conexiones, Carga |
| D4 (resilience) | 30 min | 1 min | 3 min | 25 min | 1 min | Agresivo | Violento | Peticiones, Conexiones, Carga |
| D5 (extended) | 60 min | 2 min | 5 min | 51 min | 2 min | Potente | Agresivo | Peticiones, Conexiones, Carga |
| D6 (soak) | 120 min | 3 min | 10 min | 104 min | 3 min | Alto | Potente | Conexiones, Carga (nunca Peticiones) |

- El nivel «adicional» (D4-D6) solo es accesible escribiendo exactamente el texto de confirmación reforzada que se muestra en pantalla — nunca con una simple casilla.
- D6 excluye la Prueba de peticiones: una prueba de caudal se limita por volumen, algo nunca pertinente en un perfil de 2 h centrado en la deriva en el tiempo.
- Esta misma tabla está disponible en la aplicación (Ayuda → Perfiles de duración D1-D6).

## Modo seguridad

Una casilla, presente en cada pantalla de lanzamiento (marcada por defecto), que activa o desactiva **únicamente** las salvaguardas que protegen la máquina que ejecuta Omega-Stress (CPU/memoria del generador local):

- **Siempre activos, sea cual sea este ajuste**: los umbrales que protegen el **objetivo probado** (tasa de error, latencia) — desactivarlos nunca tiene sentido para el producto; no es lo que cubre esta casilla.
- **Modo seguridad activo (por defecto)**: una prueba se detiene automáticamente si la propia máquina anfitriona parece bajo presión (CPU del generador Y CPU global de la máquina elevadas a la vez, no una de las dos por separado — la saturación normal de un solo núcleo nunca basta por sí sola).
- **Modo seguridad desactivado**: se retira esta salvaguarda local. Entonces se muestra un recordatorio que compara el nivel elegido con el último calibrado conocido de esta máquina (ver [Calibrado local](#calibrado-local)) — superar esa envolvente sigue siendo posible, pero la fiabilidad del resultado y la estabilidad de la máquina pasan a ser responsabilidad del usuario.

Disponible también en CLI mediante `--unsafe` (ausente por defecto = modo seguridad activo).

## Calibrado local

Mide la capacidad real de **esta máquina** (nunca del objetivo probado): un servidor de bucle local integrado en Omega-Stress recibe una carga creciente por escalones, generada por el mismo motor `httpx`/asyncio que las pruebas reales.

- 7 escalones, desde el reposo (ruido de fondo del sistema) hasta 2000 conexiones / 12 000 pet/s, cada uno evaluado frente a umbrales de salud (CPU del generador Y global, memoria disponible, tasa de error, caudal alcanzado) — los 2 últimos escalones son condicionales y se omiten si el escalón anterior no está sano.
- Produce una envolvente segura (`VU_safe` / `RPS_safe`) a partir del último escalón sano, con un margen de seguridad (~30 % de reserva) y un nivel de confianza que crece con la profundidad alcanzada.
- **Solo medición en la V1**: el resultado no se aplica automáticamente para limitar una prueba real — sirve de referencia informativa, sobre todo cuando el [Modo seguridad](#modo-seguridad) está desactivado.
- Guardado por máquina (huella no invasiva: SO/arquitectura/número de núcleos/RAM, nunca una dirección de hardware), consultable en cualquier momento sin volver a medir.

Accesible desde la pantalla **Calibrado** de la TUI (botón «Lanzar el calibrado», progreso mostrado segundo a segundo), o en CLI:

```bash
omega-stress calibrate run     # lanza un nuevo calibrado
omega-stress calibrate show    # muestra el último calibrado conocido, sin lanzar otro
```

## Configuración

Todo se ajusta desde la pantalla **Ajustes** de la TUI (ningún archivo de configuración que editar a mano):

- **Tema**: uno de los 10 temas Omega, aplicado de inmediato y guardado.
- **Perfil de renderizado**: Automático (detección al arrancar) o forzado manualmente (Completo/Estándar/Reducido/Mono).
- **Carpeta de exportación por defecto**: rellena el campo «destino» de la pantalla Exportación.
- **Carpeta de capturas de pantalla por defecto**: la usa el comando «Captura de pantalla» de la paleta (`Ctrl+P`).
- **Purgas**: objetivos recientes (nunca los fijados), todos los objetivos (incluidos los fijados y sus autorizaciones) o el historial completo — cada una protegida por una confirmación propia.

Los ajustes se guardan en `var/settings.json`. La propia raíz `var/` puede redirigirse mediante la variable de entorno `OMEGA_STRESS_VAR_DIR` (útil para aislar varias instancias, o para las pruebas).

## Pruebas y calidad

```bash
pytest
ruff check .
mypy src
lint-imports   # comprueba la Dependency Rule (ver pyproject.toml [tool.importlinter])
```

El conjunto cubre más de 570 pruebas (unitarias, de integración, TUI, CLI). `lint-imports` hace fallar la CI si se viola la Dependency Rule o el aislamiento de las tecnologías de terceros — ver [Arquitectura](#arquitectura).

## Desinstalación

Omega-Stress no toca nada fuera de su propia carpeta y de una línea de alias opcional:

```bash
rm -rf ~/omega-stress
sed -i '/alias stress=/d' ~/.bashrc ~/.zshrc
```

`install.sh` no crea ningún paquete del sistema, servicio ni archivo fuera de `~/omega-stress/` — no hace falta ninguna desinstalación adicional.

## Limitaciones conocidas

- Generación de carga **en el propio proceso**, en una sola máquina (`httpx`/asyncio): no es una herramienta distribuida — los topes reales (ver [Valores de las pruebas](#valores-de-las-pruebas)) son claramente más modestos que los de un servicio SaaS de pruebas de carga (loader.io, etc.), a propósito, por postura de producto controlado. En hardware modesto, los niveles Agresivo/Violento/Máximo de la Prueba de conexiones pueden tardar bastante más tiempo real que la duración elegida en emitir toda la carga prevista — es entonces la capacidad de **esta máquina**, no la del objetivo, la que limita el caudal real; use el [Calibrado local](#calibrado-local) para conocer los valores razonables en su hardware.
- La detección automática de la familia de terminal se basa en variables de entorno: xfce4-terminal no tiene ningún marcador fiable conocido hasta la fecha (ver [Terminales compatibles](#terminales-compatibles)).
- `plugins/` es un punto de extensión previsto por la arquitectura (carga de plugins integrados/externos), no implementado en la V1: la estructura existe, no se entrega ningún plugin.
- `var/` es relativo a la carpeta del proyecto (no XDG): pensado para un uso local monousuario, no para compartirlo entre varios usuarios de la misma máquina.
- La Prueba de carga (subida progresiva) en **modo manual** no incluye escalón de bajada («cooldown») tras la meseta — solo disponible con un [perfil de duración D1-D6](#perfiles-de-duración-d1-d6-modo-perfil), que incluye las 4 fases de forma nativa.
- Un pre-check superado no está ligado a un objetivo concreto: sigue siendo válido 24 h para cualquier lanzamiento Violento/Máximo posterior, no solo sobre el objetivo comprobado.
- El [Calibrado local](#calibrado-local) mide, pero todavía no aplica automáticamente su envolvente segura para limitar una prueba real — un trabajo deliberadamente aparte, aún sin empezar.

## Licencia

MIT — ver `LICENSE`.
