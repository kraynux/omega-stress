<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licencia MIT (consulta el archivo LICENSE) -->
<div align="center">
  <img src="docs/assets/omega-stress.png" alt="Omega-Stress" width="256">
</div>

# 🗲 OMEGA-STRESS

**Estación controlada de pruebas de carga HTTP**

> Desarrollado por **kraynux** para **Omega-server**  
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Página oficial: [OMEGA-STRESS](https://kraynux.snake-mackarel.ts.net/omega-stress/) &nbsp; Vista previa: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-stress/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

**Idiomas:**  
[Français](README.md) · [English](README.en.md) · [Español](README.es.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md)


**Omega-Stress** es una aplicación local de terminal (TUI de [Textual](https://github.com/Textualize/textual) + CLI programable) para ejecutar pruebas de carga HTTP controladas y reutilizables: perfiles fijos, historial, repetición, exportaciones detalladas (JSON/CSV/HTML) y límites de seguridad explícitos.

El proyecto sigue los principios de **Clean Architecture**, con una separación clara entre el dominio de negocio, la orquestación, la infraestructura y la interfaz de usuario.



---

## Contenido

- [Descripción general](#descripción-general)
- [Funcionalidades](#funcionalidades)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Perfiles de duración D1-D6](#perfiles-de-duración-d1-d6-modo-perfil)
- [Modo de seguridad](#modo-de-seguridad)
- [Calibración local](#calibración-local)
- [Configuración](#configuración)
- [Pruebas y calidad](#pruebas-y-calidad)
- [Desinstalación](#desinstalación)
- [Limitaciones conocidas](#limitaciones-conocidas)
- [Licencia](#licencia)

## Descripción general

### Objetivos

## Qué hace Omega-Stress (objetivo V1)

- Tres familias de pruebas controladas: **Prueba de solicitudes** (rendimiento), **Prueba de conexiones** (concurrencia) y **Prueba de carga** (incremento progresivo).
- **8 niveles de intensidad** (Bajo/Mínimo/Medio/Alto/Potente/Agresivo/Violento/Máximo), con un modelo de precomprobación de 3 niveles (sin requisito / requisito opcional / requisito obligatorio; consulta [Valores de las pruebas](#valores-de-las-pruebas)).
- **Dos modos de duración**: manual (de 1 a 5 minutos, limitado por nivel) o **perfil D1-D6** con nombre (duración total fija con calentamiento/rampa/meseta/enfriamiento; consulta [Perfiles de duración D1-D6](#perfiles-de-duración-d1-d6-modo-perfil)).
- **Modo de seguridad** (activo por defecto y desactivable en cada lanzamiento): protecciones locales de CPU/memoria para la máquina anfitriona, separadas de los umbrales que protegen al objetivo probado; consulta [Modo de seguridad](#modo-de-seguridad).
- **Calibración local persistente**: mide la capacidad real de la máquina anfitriona (nunca la del objetivo) mediante un servidor loopback, con etapas de carga creciente; consulta [Calibración local](#calibración-local).
- Perfiles fijos, reutilizables y con historial.
- Confirmación explícita de autorización obligatoria antes de cada ejecución sobre un objetivo no fijado.
- Umbrales de parada automática; nunca se permite una carga sin límites.
- Exportaciones detalladas JSON/CSV/HTML (etapas, métricas por intervalo, veredicto y diagnóstico).
- Modo CLI no interactivo para automatización (cron, CI), que utiliza exactamente los mismos casos de uso que la TUI.
- Adaptación automática al terminal (tema y perfil de renderizado degradable).

## Qué no hace el proyecto

- No sustituye a una herramienta de escaneo de red: la terminología y la postura del producto utilizan deliberadamente «prueba de carga», nunca «escaneo».
- No implementa un motor de carga externo (k6, etc.): la generación es nativa mediante `httpx`/asyncio.
- Nunca inicia una ejecución sin límites ni confirmación de autorización.
- No es una herramienta de carga distribuida: la generación se ejecuta en una sola máquina y un solo proceso; consulta [Limitaciones conocidas](#limitaciones-conocidas).

## Funcionalidades

- **Tres familias de pruebas**, cada una con 8 niveles de intensidad (Bajo/Mínimo/Medio/Alto/Potente/Agresivo/Violento/Máximo); consulta la tabla [Referencias de carga](#valores-de-las-pruebas) para conocer los valores exactos.
- **Perfiles de prueba fijos**: nombre, objetivo, familia, intensidad, duración y umbral de errores; se crean una vez y se repiten de forma idéntica desde la TUI o el CLI.
- **Perfiles de duración D1-D6 con nombre** (modo «perfil»), alternativa al modo manual: duración total fija de 1 a 120 minutos con calentamiento/rampa/meseta/enfriamiento, que también limita los niveles disponibles; consulta [Perfiles de duración D1-D6](#perfiles-de-duración-d1-d6-modo-perfil).
- **Modo de seguridad**, marcado por defecto en cada pantalla de lanzamiento: detiene una prueba si parece estar en peligro la máquina anfitriona, no el objetivo. Se puede desactivar conscientemente, mostrando un recordatorio que compara el nivel elegido con la última calibración; consulta [Modo de seguridad](#modo-de-seguridad).
- **Calibración local persistente**: mide lo que la máquina puede soportar realmente (7 etapas de carga creciente contra un servidor loopback integrado), disponible desde la pantalla Calibración; consulta [Calibración local](#calibración-local).
- **Objetivos fijados**: una dirección fijada no necesita volver a marcar la autorización en cada lanzamiento; los objetivos recientes no fijados siguen visibles (máximo 10) sin implicar autorización.
- **Historial completo**: cada ejecución se registra (veredicto, métricas, cronología por intervalo y estado del modo de seguridad); una ejecución asociada a un perfil fijo puede repetirse de forma idéntica.
- **Exportaciones detalladas** en JSON (datos brutos reimportables), CSV (análisis tabular) o HTML (informe legible con una de las 10 paletas del proyecto).
- **Precomprobación automática**, obligatoria antes de cualquier prueba Violenta/Máxima y opcional (pero desbloquea duraciones adicionales) para Potente/Agresiva, con una validez de 24 horas.
- **Supervisión en directo**: barra de progreso con cuenta atrás fiable (el tiempo restante se calcula directamente, nunca se estima), rendimiento/errores/latencia p95 actualizados en cada intervalo y parada manual sin salir de la aplicación.
- **Ajustes centralizados**: tema (10 paletas Omega y todos los temas integrados de Textual, 31 en total mediante la paleta de comandos), perfil de renderizado (automático o forzado), carpetas de exportación y capturas, y limpieza de objetivos/historial.
- **Ayuda integrada** (tecla `a`): atajos de teclado, descripción de cada pantalla (incluidas Calibración y Modo de seguridad), tabla de referencia de carga y tabla de perfiles de duración D1-D6.
- **CLI programable** (`omega-stress profile|run|history|export|calibrate ...`), con los mismos casos de uso que la TUI y salida `--json` para automatización.
- **Adaptación automática al terminal**: familia y tamaño detectados al iniciar; el tema y la riqueza visual se ajustan en consecuencia; consulta [Terminales compatibles](#terminales-compatibles).

## Arquitectura

Clean Architecture + Ports & Adapters en 9 paquetes (`app/`, `core/`, `domain/`, `application/`, `ports/`, `infrastructure/`, `interfaces/`, `plugins/`, `shared/`).
Detalles completos: `ARCHITECTURE.md`.

```text
src/omega_stress/
├── app/              Bootstrap y contenedor de inyección de dependencias (cableado manual, sin framework DI)
├── core/             Vocabulario transversal: enumeraciones, excepciones raíz, Result/Ok/Err y capacidades del sistema
├── domain/           Lógica de negocio pura: carga, perfiles, ejecuciones, objetivos, temas y terminal; sin I/O
├── application/      Orquestación: commands, queries y pipeline de ejecución (guards/hooks)
├── ports/            Contratos Protocol/ABC esperados por los adaptadores (repositories, exporters, generador de carga...)
├── infrastructure/  Implementaciones concretas: SQLite, exportadores JSON/CSV/HTML, generador httpx/asyncio, detección de terminal y sonda del sistema
├── interfaces/       Dos adaptadores independientes de presentación: TUI (Textual) y CLI (argparse)
├── plugins/          Punto de extensión reservado (carga de plugins); existe el scaffolding, pero no está implementado en V1
└── shared/           Utilidades transversales sin dependencias de negocio (reloj inyectable y generación de identificadores)
```

### Principios de diseño

- `domain/` no contiene I/O ni dependencias de infraestructura: lógica de negocio pura, completamente comprobable sin mocks.
- `application/` orquesta los casos de uso mediante el dominio y los puertos, nunca directamente mediante una clase concreta de `infrastructure/`.
- `infrastructure/` implementa los puertos y nunca es importada directamente por `application/` o `domain/`; solo `interfaces/` y `app/` la referencian.
- `interfaces/` nunca debe llamar directamente a `infrastructure/` ni a `subprocess`: solo a comandos/queries de `application/` y a sus propios controladores.
- `ports/` define los contratos de los adaptadores (Protocol), nunca implementaciones.
- `core/` agrupa el vocabulario transversal a todas las capas, sin codificar reglas de negocio numéricas (umbrales, duraciones y presets siempre están en `domain/*/policies.py`).

La Dependency Rule (las capas externas solo dependen de las internas) y el aislamiento de tecnologías de terceros (`textual`, `sqlite3`, `httpx` y `jinja2`, cada una confinada a su punto de entrada) se comprueban automáticamente cada vez que se ejecuta `lint-imports`; consulta [Pruebas y calidad](#pruebas-y-calidad).

## Requisitos

- Python ≥ 3.10.
- Se recomienda [`uv`](https://github.com/astral-sh/uv) para gestionar dependencias; también funciona el `pip` estándar.

### Sistema

- Linux, principalmente Arch Linux y distribuciones compatibles.
- Python 3.10 o superior.
- No se requieren privilegios de root: Omega-Stress solo realiza peticiones HTTP salientes como usuario normal.

## Instalación

El archivo oficial se proporciona en formato `.tar.gz`. Verifica su integridad antes de instalarlo:

```bash
sha256sum omega-stress.tar.gz
```

### Método 1 — script de instalación

```bash
[ -d omega-stress ] && echo "ℹ️ Ya está extraído aquí; se omite el paso." || tar -xzf omega-stress.tar.gz
[ -d ~/omega-stress ] && echo "ℹ️ ~/omega-stress ya existe; se omite el desplazamiento." || mv omega-stress ~/
cd ~/omega-stress/
chmod +x install.sh
./install.sh
```

### Método 2 — instalación completa resistente

Este comando se puede copiar y pegar tal cual y volver a ejecutar sin errores: cada paso omite lo que ya se haya completado.

```bash
( [ -d omega-stress ] || tar -xzf omega-stress.tar.gz ) && \
( [ -d ~/omega-stress ] || mv omega-stress ~/ ) && \
cd ~/omega-stress && chmod +x install.sh && ./install.sh
```

`install.sh`:

1. Crea el entorno virtual `.venv` si todavía no existe.
2. Instala las dependencias (`pip install -e .`; `pyproject.toml` sigue siendo la única fuente de verdad).
3. Hace ejecutables `omega-stress.sh` e `install.sh`.
4. Añade el alias `stress` a `~/.bashrc` y `~/.zshrc` sin duplicarlo.

## Instalación para desarrollo

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

# o simplemente escribe "stress" en un terminal nuevo si se creó el alias
```

El lanzador:

1. Detecta `.venv`, `venv` o Python del sistema.
2. Configura `PYTHONPATH` hacia `src/`.
3. Ejecuta `python -m omega_stress`: sin argumentos abre la TUI y con argumentos delega en el CLI.

### Uso del CLI

```bash
omega-stress profile list                                     # listar perfiles
omega-stress profile create --name "Sondeo API" --target-id t-1 \
    --family request --level basic --duration-minutes 1 --max-error-rate 0.05
omega-stress profile freeze <profile-id>                       # fijar un perfil

# Precomprobación obligatoria antes de cualquier lanzamiento Violento/Máximo (opcional para Potente/Agresivo)
omega-stress run precheck --target-id t-1 --target-url https://example.org --confirm

omega-stress run request --target-id t-1 --target-url https://example.org \
    --level basic --duration-minutes 1 --max-error-rate 0.05 --confirm
omega-stress run connection --target-id t-1 --target-url https://example.org \
    --level medium --duration-minutes 3 --max-error-rate 0.05 --confirm
omega-stress run ramp --target-id t-1 --target-url https://example.org \
    --level powerful --duration-minutes 3 --max-error-rate 0.05 --confirm --precheck-validated

# Modo de perfil D1-D6 en lugar de --duration-minutes (mutuamente excluyentes)
# D4 (resilience) permite Agresivo sin condiciones y Violento con confirmación reforzada
omega-stress run request --target-id t-1 --target-url https://example.org \
    --level violent --duration-preset d4 --max-error-rate 0.05 --confirm \
    --precheck-validated --confirmation-text CONFIRMO_EL_OBJETIVO_AUTORIZADO

# --unsafe desactiva el modo de seguridad (protecciones locales de CPU/memoria); ausente por defecto
aomega-stress run connection --target-id t-1 --target-url https://example.org \
    --level violent --duration-minutes 1 --max-error-rate 0.05 --confirm \
    --precheck-validated --unsafe

omega-stress run replay <run-id> --confirm                     # repetir una ejecución vinculada a un perfil fijado

omega-stress history list                                      # historial de ejecuciones
omega-stress history show <run-id>                              # detalles de una ejecución

omega-stress export <run-id> --format html --destination var/exports --theme omega-base

omega-stress calibrate run                                      # calibrar esta máquina
omega-stress calibrate show                                     # mostrar la última calibración conocida
```

`--confirm` equivale a la casilla de autorización de la TUI y es obligatorio para cualquier objetivo que no esté fijado y autorizado. Los valores idénticos de `--target-id`/`--target-url` indican un objetivo manual no fijado; utiliza el identificador de un objetivo ya fijado para evitar `--confirm` en cada lanzamiento.

Añade `--json` a `history`, `export` o `calibrate` para obtener una salida legible por máquinas, adecuada para cron/CI.

## Perfiles de duración D1-D6 (modo perfil)

Alternativa al modo manual (1–5 minutos limitados por nivel): un **perfil de duración con nombre**, duración total fija y cuatro fases internas (calentamiento, rampa, meseta y enfriamiento). Se puede seleccionar en cada pantalla de lanzamiento (conmutador «Modo de duración: Manual / Perfil D1-D6») y en CLI mediante `--duration-preset`.

| Perfil | Duración total | Calentamiento | Rampa | Meseta | Enfriamiento | Nivel máximo sin confirmación | Nivel adicional (confirmación reforzada) | Familias compatibles |
|---|---|---|---|---|---|---|---|---|
| D1 (quick) | 1 min | 5 s | 10 s | 40 s | 5 s | Máximo | — | Solicitudes, Conexiones, Carga |
| D2 (short) | 5 min | 15 s | 30 s | 4 min | 15 s | Máximo | — | Solicitudes, Conexiones, Carga |
| D3 (standard) | 15 min | 30 s | 1 min 30 s | 12 min 30 s | 30 s | Violento | — | Solicitudes, Conexiones, Carga |
| D4 (resilience) | 30 min | 1 min | 3 min | 25 min | 1 min | Agresivo | Violento | Solicitudes, Conexiones, Carga |
| D5 (extended) | 60 min | 2 min | 5 min | 51 min | 2 min | Potente | Agresivo | Solicitudes, Conexiones, Carga |
| D6 (soak) | 120 min | 3 min | 10 min | 104 min | 3 min | Alto | Potente | Conexiones, Carga (nunca Solicitudes) |

- El nivel adicional (D4-D6) solo está disponible escribiendo exactamente el texto de confirmación reforzada mostrado en pantalla; una simple casilla no es suficiente.
- D6 excluye la Prueba de solicitudes: una prueba de rendimiento está limitada por volumen y no resulta pertinente en un perfil de dos horas centrado en la deriva temporal.
- La misma tabla está disponible en la aplicación (Ayuda → Perfiles de duración D1-D6).

## Modo de seguridad

Una casilla presente en cada pantalla de lanzamiento (marcada por defecto) que controla **únicamente** las protecciones de la máquina que ejecuta Omega-Stress (CPU/memoria del generador local):

- **Siempre activos independientemente de este ajuste**: los umbrales que protegen al **objetivo probado** (tasa de errores y latencia). Desactivarlos nunca tendría sentido; esta casilla no los controla.
- **Modo de seguridad activo (por defecto)**: la prueba se detiene automáticamente si la propia máquina anfitriona parece estar bajo presión (CPU del generador y CPU total de la máquina altos al mismo tiempo; uno solo nunca basta).
- **Modo de seguridad desactivado**: se retira la protección local. Aparece un recordatorio que compara el nivel elegido con la última calibración conocida de la máquina (consulta [Calibración local](#calibración-local)). Es posible superar ese margen, pero la fiabilidad del resultado y la estabilidad de la máquina pasan a ser responsabilidad del usuario.

También está disponible en CLI mediante `--unsafe` (ausente por defecto significa que el modo de seguridad está activo).

## Calibración local

Mide la capacidad real de **esta máquina** (nunca la del objetivo probado): un servidor loopback integrado de Omega-Stress recibe etapas de carga creciente generadas por el mismo motor `httpx`/asyncio que las pruebas reales.

- 7 etapas, desde reposo (ruido de fondo del sistema) hasta 2000 conexiones / 12 000 solicitudes por segundo, evaluadas mediante umbrales de salud (CPU del generador y global, memoria disponible, tasa de errores y rendimiento alcanzado). Las 2 últimas etapas son condicionales y se omiten si la anterior no es saludable.
- Produce un margen seguro (`VU_safe` / `RPS_safe`) a partir de la última etapa saludable, con un margen de seguridad (aproximadamente un 30 % de reserva) y confianza creciente según la profundidad alcanzada.
- **Solo mide en V1**: el resultado no se aplica automáticamente para limitar una prueba real; sirve como referencia informativa, especialmente cuando el [Modo de seguridad](#modo-de-seguridad) está desactivado.
- Se guarda por máquina mediante una huella no invasiva (SO/arquitectura/número de núcleos/RAM, nunca una dirección de hardware) y se puede consultar en cualquier momento sin repetir la medición.

Está disponible desde la pantalla TUI **Calibración** («Ejecutar calibración», con progreso segundo a segundo) o mediante CLI:

```bash
omega-stress calibrate run     # ejecutar una nueva calibración
omega-stress calibrate show    # mostrar la última calibración sin ejecutar otra
```

## Configuración

Todo se configura desde la pantalla TUI **Ajustes**; no es necesario editar manualmente ningún archivo de configuración:

- **Tema**: elegir entre los 10 temas Omega; se aplica inmediatamente y queda guardado.
- **Perfil de renderizado**: Automático (detectado al iniciar) o forzado manualmente (Completo/Estándar/Reducido/Mono).
- **Carpeta de exportación predeterminada**: rellena previamente el destino de la pantalla Exportar.
- **Carpeta de capturas predeterminada**: utilizada por el comando «Captura de pantalla» de la paleta (`Ctrl+P`).
- **Limpieza**: objetivos recientes (nunca los fijados), todos los objetivos (incluidos los fijados y sus autorizaciones) o el historial completo; cada acción tiene su propia confirmación.

Los ajustes se guardan en `var/settings.json`. La raíz `var/` se puede redirigir mediante `OMEGA_STRESS_VAR_DIR`, útil para aislar varias instancias o pruebas.

## Pruebas y calidad

```bash
pytest
ruff check .
mypy src
lint-imports   # verifica la Dependency Rule (consulta [tool.importlinter] en pyproject.toml)
```

La suite contiene más de 570 pruebas (unitarias, integración, TUI y CLI). `lint-imports` hace fallar la CI si se viola la Dependency Rule o el aislamiento de tecnologías de terceros; consulta [Arquitectura](#arquitectura).

## Desinstalación

Omega-Stress no modifica nada fuera de su propio directorio y una línea de alias opcional:

```bash
rm -rf ~/omega-stress
sed -i '/alias stress=/d' ~/.bashrc ~/.zshrc
```

`install.sh` no crea paquetes de sistema, servicios ni archivos fuera de `~/omega-stress/`; no se requiere ninguna desinstalación adicional.

## Limitaciones conocidas

- **Generación de carga dentro del proceso** en una sola máquina (`httpx`/asyncio): no es una herramienta distribuida. Los límites reales (consulta [Valores de las pruebas](#valores-de-las-pruebas)) son deliberadamente mucho más modestos que los de servicios SaaS como loader.io. En hardware modesto, las pruebas de conexiones en niveles Agresivo/Violento/Máximo pueden tardar bastante más tiempo real que la duración seleccionada para emitir toda la carga objetivo; el rendimiento de **esta máquina**, no el objetivo, limita entonces el rendimiento real. Usa [Calibración local](#calibración-local) para conocer valores razonables para tu hardware.
- La detección automática de la familia del terminal depende de variables de entorno; xfce4-terminal no dispone actualmente de un marcador fiable conocido (consulta [Terminales compatibles](#terminales-compatibles)).
- `plugins/` es un punto de extensión arquitectónico para cargar plugins integrados/externos, no implementado en V1: existe el scaffolding, pero no se incluye ningún plugin.
- `var/` es relativo al directorio del proyecto (no XDG): está pensado para un uso local de un solo usuario, no para compartirlo entre varios usuarios en la misma máquina.
- El modo manual de **Prueba de carga** no tiene una fase de enfriamiento después de la meseta; solo está disponible mediante un [perfil de duración D1-D6](#perfiles-de-duración-d1-d6-modo-perfil), que incluye las cuatro fases de forma nativa.
- Una precomprobación validada no está vinculada a un objetivo concreto: sigue siendo válida durante 24 horas para cualquier lanzamiento posterior Violento/Máximo, no solo para el objetivo precomprobado.
- La [Calibración local](#calibración-local) mide, pero todavía no aplica automáticamente su margen seguro para limitar una prueba real; es una tarea separada que aún no se ha iniciado.

## Licencia

MIT — consulta `LICENSE`.
