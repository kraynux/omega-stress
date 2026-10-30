<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT 许可证（见 LICENSE 文件） -->
<div align="center">
  <img src="../../assets/omega-stress.png" alt="Omega-Stress" width="384">
</div>

# 🗲 OMEGA-STRESS

**受控的 HTTP 负载测试工作台**

> 由 **kraynux** 为 **Omega-server** 打造 
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

官方页面：[OMEGA-STRESS](https://kraynux.snake-mackarel.ts.net/omega-stress/) &nbsp; 截图：[Screenshots](https://kraynux.snake-mackarel.ts.net/omega-stress/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 界面和导出的报告提供 **17 种语言** — 见[界面语言](#界面语言)。  
**语言：**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)



**Omega-Stress** 是一个本地终端应用（[Textual](https://github.com/Textualize/textual) TUI + 可脚本化 CLI），以受控、可复用的方式执行 HTTP 负载测试：冻结的配置档案、历史、重新运行、详细导出（JSON/CSV/HTML）、明确的安全边界。

项目遵循 **Clean Architecture** 原则，业务领域、编排、基础设施和用户界面之间界限分明。
---

## 目录

- [简介](#简介)
- [功能](#功能)
- [架构](#架构)
- [前提条件](#前提条件)
- [安装](#安装)
- [使用](#启动)
- [时长配置文件 D1-D6](#时长配置文件-d1-d6配置文件模式)
- [安全模式](#安全模式)
- [本地校准](#本地校准)
- [配置](#配置)
- [测试与质量](#测试与质量)
- [卸载](#卸载)
- [已知限制](#已知限制)
- [许可证](#许可证)

## 简介

### 目标

## Omega-Stress 能做什么（V1 目标）

- 三种受控的测试类型：**请求测试**（吞吐量）、**连接测试**（并发）、**负载测试**（逐步加压）。
- **8 个强度级别**（微弱/低/中/高/强劲/激进/猛烈/最大），配有三档预检查模型（从不要求 / 可选要求 / 强制要求 — 见[测试数值](#测试数值)）。
- **两种时长模式**：手动（1 至 5 分钟，按级别限制）或**命名的时长配置文件 D1-D6**（固定总时长，含预热/爬升/平台/冷却 — 见[时长配置文件 D1-D6](#时长配置文件-d1-d6配置文件模式)）。
- **安全模式**（默认开启，每次启动时都可关闭）：主机本地的 CPU/内存保护，与保护被测目标的阈值相互独立 — 见[安全模式](#安全模式)。
- **持久的本地校准**：通过本地回环服务器，以逐级增加的负载测量主机（绝不是目标）的真实承载能力 — 见[本地校准](#本地校准)。
- 冻结的、可复用的、记录在历史中的配置档案 — **可选**：直接选择或输入目标，完全不用配置档案，也能在手动模式下照样运行测试。
- 对任何未固定的目标运行测试前，必须明确确认授权。
- 自动停止阈值，绝不施加无上限的负载。
- 详细的 JSON/CSV/HTML 导出（各级、按区间的指标、结论、诊断）。
- 用于自动化（cron、CI）的非交互 CLI 模式，调用的用例与 TUI 完全相同。
- 自动适配终端（主题 + 可降级的渲染配置）。

## 项目不做什么

- 它不取代网络扫描工具 — 产品的用词和定位明确是“负载测试”，绝不是“扫描”。
- 它不实现任何外部负载引擎（k6 等）— 使用原生 `httpx`/asyncio 生成负载。
- 未设边界、未确认授权时，它绝不启动任何运行。
- 它不是分布式负载工具：负载在单台机器、单个进程中生成 — 见[已知限制](#已知限制)。

## 功能

- **三种测试类型**，每种都有 8 个强度级别（微弱/低/中/高/强劲/激进/猛烈/最大）— 各级别的确切数值见[负载参考](#测试数值)表。
- **冻结的测试配置档案**：名称、目标、类型、强度、时长、错误阈值 — 创建一次，即可在 TUI 或 CLI 中原样重新运行。
- **命名的时长配置文件 D1-D6**（“配置文件”模式），手动模式之外的另一选择：固定总时长（1 至 120 分钟），含预热/爬升/平台/冷却，同时也限制可用的级别 — 见[时长配置文件 D1-D6](#时长配置文件-d1-d6配置文件模式)。
- **安全模式**，在每个启动屏上默认勾选：如果主机（而不是目标）看起来处于危险中，就停止测试。可在知情的前提下关闭，届时会提示将所选级别与最近一次校准进行比较 — 见[安全模式](#安全模式)。
- **持久的本地校准**：测量本机真正能承受的负载（对内置本地回环服务器进行 7 级逐步加压），可在校准屏幕中查看 — 见[本地校准](#本地校准)。
- **固定的目标**：固定的地址在每次启动时无需再次勾选授权；未固定的最近目标仍然可见（最多 10 个），但不会被默认授权。固定的目标可以用于两种互不相关的方式：直接用于在无配置档案的手动模式下启动测试，或在创建冻结配置档案时作为默认目标。
- **完整的历史**：每次运行都会被记录（结论、指标、按区间的时间线、所用的安全模式）；与冻结配置档案关联的运行可以原样重放。
- **详细导出**：JSON（可重新导入的原始数据）、CSV（表格分析）或 HTML（易读的报告，可从项目的 10 种配色中选择主题）。HTML 报告使用设置中选择的语言编写（“导出语言”，默认与界面相同）；JSON 和 CSV 作为数据保持不翻译。
- **预检查**：任何猛烈/最大级别的测试前自动且强制执行；在强劲/激进级别上可选（但可解锁更长的时长），有效期为 24 小时。
- **实时跟踪**正在运行的测试：进度条带可靠的倒计时（剩余时间直接计算，绝不估算），吞吐量/错误/p95 延迟在每个区间更新，无需退出应用即可手动停止。
- **集中的设置**：主题（10 种 Omega 配色 + Textual 全部内置主题，通过命令面板共 31 种）、渲染配置（自动或强制）、导出和截图文件夹、清理目标/历史。
- **内置帮助**（`a` 键）：键盘快捷键、各屏幕说明（包括校准和安全模式）、负载数值参考表以及时长配置文件 D1-D6 表。
- **可脚本化的 CLI**（`omega-stress profile|run|history|export|calibrate ...`），用例与 TUI 完全相同，并提供用于自动化的 `--json` 输出。
- **自动适配终端**：启动时检测终端类型和尺寸，并据此调整主题和显示丰富程度（见[支持的终端](#支持的终端)）。

## 架构

Clean Architecture + Ports & Adapters，共 9 个包（`app/`、`core/`、`domain/`、`application/`、`ports/`、`infrastructure/`、`interfaces/`、`plugins/`、`shared/`）。
完整细节：`ARCHITECTURE.md`。

```text
src/omega_stress/
├── app/              启动与依赖注入容器（手动装配，不用 DI 框架）
├── core/             通用词汇：枚举、根异常、Result/Ok/Err、系统能力
├── domain/           纯业务逻辑：负载、配置档案、运行、目标、主题、终端 — 无 I/O
├── application/      编排：commands（操作）、queries（读取）、执行流水线（guards/hooks）
├── ports/            适配器所需的 Protocol/ABC 契约（仓储、导出器、负载生成器……）
├── infrastructure/   具体实现：SQLite、JSON/CSV/HTML 导出器、httpx/asyncio 生成器、终端检测、系统探针
├── interfaces/       两个独立的展示适配器：TUI（Textual）和 CLI（argparse）
├── plugins/          预留的扩展点（插件加载）— 骨架已存在，V1 中未实现
└── shared/           无业务依赖的通用工具（可注入的时钟、标识符生成）
```

### 设计原则

- `domain/` 不包含 I/O，也不依赖基础设施 — 纯业务逻辑，无需模拟对象即可完整测试。
- `application/` 通过领域和端口编排用例，绝不直接使用 `infrastructure/` 中的具体类。
- `infrastructure/` 实现端口，但绝不被 `application/` 或 `domain/` 直接导入 — 只有 `interfaces/` 和 `app/` 引用它。
- `interfaces/` 绝不能直接调用 `infrastructure/` 或 `subprocess`：只能通过 `application/`（commands/queries）及其自己的控制器。
- `ports/` 定义适配器所需的契约（Protocol），绝不包含实现。
- `core/` 汇集各层共用的词汇，绝不在其中写入带数值的业务规则（阈值、时长、预设 — 一律放在 `domain/*/policies.py`）。

Dependency Rule（只能由外层指向内层）以及第三方技术的隔离（`textual`、`sqlite3`、`httpx`、`jinja2` 各自限定在指定的入口点）会在每次运行 `lint-imports` 时自动检查（见[测试与质量](#测试与质量)）。

## 前提条件

- Python ≥ 3.10
- 建议使用 [`uv`](https://github.com/astral-sh/uv) 管理依赖（否则使用标准的 `pip`）

### 系统

- Linux，优先 Arch Linux 及兼容发行版。
- Python 3.10 或更高版本。
- 无需 root 权限：Omega-Stress 只以普通用户身份发起出站 HTTP 请求。

## 安装

官方归档以 `.tar.gz` 格式提供。安装前请校验其完整性：

```bash
sha256sum omega-stress.tar.gz
```

### 方法 1 — 安装脚本

```bash
[ -d omega-stress ] && echo "ℹ️ 此处已解压，跳过此步骤。" || tar -xzf omega-stress.tar.gz
[ -d ~/omega-stress ] && echo "ℹ️ ~/omega-stress 已存在，跳过移动。" || mv omega-stress ~/
cd ~/omega-stress/
chmod +x install.sh
./install.sh
```

### 方法 2 — 稳健的完整安装

这条命令可以原样复制粘贴，并可重复执行而不出错：每一步都会跳过已经完成的部分。

```bash
( [ -d omega-stress ] || tar -xzf omega-stress.tar.gz ) && \
( [ -d ~/omega-stress ] || mv omega-stress ~/ ) && \
cd ~/omega-stress && chmod +x install.sh && ./install.sh
```
`install.sh`：

1. 如果虚拟环境 `.venv` 尚不存在，则创建它。
2. 安装依赖（`pip install -e .`；`pyproject.toml` 仍是唯一的权威来源）。
3. 使 `omega-stress.sh` 和 `install.sh` 可执行。
4. 将别名 `stress` 添加到 `~/.bashrc` 和 `~/.zshrc`（已存在时不会重复添加）。

## 安装（开发环境）

```bash
uv sync --all-extras
# 或者不用 uv：
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```


### 启动

```bash
cd ~/omega-stress
./omega-stress.sh

# 如果已创建别名，也可以在新终端中直接输入 "stress"
```

启动器：

1. 检测 `.venv`、`venv` 或系统 Python。
2. 将 `PYTHONPATH` 设置为 `src/`。
3. 运行 `python -m omega_stress` — 不带参数时打开 TUI；带参数时转交给 CLI。

### 界面语言

界面提供 17 种语言：法语、英语、西班牙语、葡萄牙语（巴西）、意大利语、德语、荷兰语、波兰语、俄语、简体中文、越南语、泰语、印尼语、日语、韩语、印地语和阿拉伯语。在设置中选择（“Langue / Language”），重启界面后生效；变量 `OMEGA_STRESS_LANG`（例如 `OMEGA_STRESS_LANG=zh-CN ./omega-stress.sh`）可在一次会话中强制使用某种语言。从 omega-suite 启动时，omega-stress 使用套件的语言。在 Linux 文本控制台（TTY）上，非拉丁文字的语言在本次会话中以英语显示。命令行保持法语。

### 使用 CLI

```bash
omega-stress profile list                                     # 列出配置档案
omega-stress profile create --name "API 探测" --target-id t-1 \
    --family request --level bas --duration-minutes 1 --max-error-rate 0.05
omega-stress profile freeze <profile-id>                       # 冻结配置档案

# 任何猛烈/最大级别的运行前必须预检查（强劲/激进级别可选）
omega-stress run precheck --target-id t-1 --target-url https://exemple.org --confirm

omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level bas --duration-minutes 1 --max-error-rate 0.05 --confirm
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level moyen --duration-minutes 3 --max-error-rate 0.05 --confirm
omega-stress run ramp --target-id t-1 --target-url https://exemple.org \
    --level puissant --duration-minutes 3 --max-error-rate 0.05 --confirm --precheck-validated

# 使用时长配置文件模式 D1-D6，代替 --duration-minutes（二者互斥）
# D4（resilience）无条件允许激进级别，猛烈级别需加强确认
omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-preset d4 --max-error-rate 0.05 --confirm \
    --precheck-validated --confirmation-text JE_CONFIRME_LA_CIBLE_AUTORISEE

# --unsafe 关闭安全模式（本地 CPU/内存保护）；默认不带此参数
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-minutes 1 --max-error-rate 0.05 --confirm \
    --precheck-validated --unsafe

omega-stress run replay <run-id> --confirm                     # 重放与冻结配置档案关联的运行

omega-stress history list                                      # 运行历史
omega-stress history show <run-id>                              # 某次运行的详情

omega-stress export <run-id> --format html --destination var/exports --theme omega-base

omega-stress calibrate run                                      # 对本机进行校准
omega-stress calibrate show                                     # 显示最近一次已知的校准
```

`--level` 的取值（`faible`、`bas`、`moyen`、`haut`、`puissant`、`agressif`、`violent`、`maximum`）和确认文本与命令行的其他部分一样保持法语。

`--confirm` 是 TUI 授权复选框在命令行中的对应项：对任何尚未固定为已授权的目标都是必需的。`--target-id`/`--target-url` 取值相同表示手动（未固定）目标；使用已固定目标的标识符，即可避免每次启动都要加 `--confirm`。

在 `history`/`export`/`calibrate` 后加上 `--json`，可得到机器可读的输出，便于在 cron/CI 中使用。

### 总体流程

1. 首次启动时，主屏提供：配置档案、请求测试、连接测试、负载测试、历史、目标、校准、设置、帮助。
2. 在测试屏幕顶部仍可选择一个冻结的配置档案（可选）：指定目标和条件有两种方式，同一次启动中绝不混用 —
   - **使用配置档案**：选中后会预先填写目标/强度/时长/错误阈值，手动目标字段随之消失（此时已无意义）；启动前预填的值仍可修改；
   - **不使用配置档案（手动模式）**：从列表中选择一个固定/最近的目标或输入一个新目标；如果它尚未固定为已授权，勾选授权；手动设置强度/时长（手动或时长配置文件 D1-D6）/错误阈值。

   两种情况下：保持安全模式开启，或在知情的前提下关闭；如果级别要求，先执行预检查，然后启动测试。
3. 结果立即显示（结论、指标、时间线），无需再去历史中查看 — 此屏幕上直接提供导出。
4. 可以冻结配置档案，以便日后在配置档案屏幕中原样重新运行同一测试，或从历史中重放。

### 测试数值

8 个强度级别，在三种测试类型中完全相同（只是控制的维度不同）— 完整表格：

| 测试类型 | 级别 | 控制的维度 | 目标值 | 预检查 | 可用时长（手动模式） |
|---|---|---|---|---|---|
| 请求测试 | 微弱 | 吞吐量 | 250 次请求/分钟（≈4.2 次/秒） | 否 | 1 至 5 分钟 |
| 请求测试 | 低 | 吞吐量 | 500 次请求/分钟（≈8.3 次/秒） | 否 | 1 至 5 分钟 |
| 请求测试 | 中 | 吞吐量 | 1000 次请求/分钟（≈16.7 次/秒） | 否 | 1 至 5 分钟 |
| 请求测试 | 高 | 吞吐量 | 2000 次请求/分钟（≈33.3 次/秒） | 否 | 1 至 5 分钟 |
| 请求测试 | 强劲 | 吞吐量 | 6000 次请求/分钟（≈100 次/秒） | 可选 | 1 至 3 分钟（预检查通过后可达 5） |
| 请求测试 | 激进 | 吞吐量 | 10,000 次请求/分钟（≈167 次/秒） | 可选 | 1 至 3 分钟（预检查通过后可达 5） |
| 请求测试 | 猛烈 | 吞吐量 | 15,000 次请求/分钟（≈250 次/秒） | **强制** | 仅 1 至 3 分钟 |
| 请求测试 | 最大 | 吞吐量 | 20,000 次请求/分钟（≈333 次/秒） | **强制** | 仅 1 至 3 分钟 |
| 连接测试 | 微弱 | 并发连接数 | 25 个连接 | 否 | 1 至 5 分钟 |
| 连接测试 | 低 | 并发连接数 | 50 个连接 | 否 | 1 至 5 分钟 |
| 连接测试 | 中 | 并发连接数 | 100 个连接 | 否 | 1 至 5 分钟 |
| 连接测试 | 高 | 并发连接数 | 200 个连接 | 否 | 1 至 5 分钟 |
| 连接测试 | 强劲 | 并发连接数 | 1000 个连接 | 可选 | 1 至 3 分钟（预检查通过后可达 5） |
| 连接测试 | 激进 | 并发连接数 | 2000 个连接 | 可选 | 1 至 3 分钟（预检查通过后可达 5） |
| 连接测试 | 猛烈 | 并发连接数 | 3500 个连接 | **强制** | 仅 1 至 3 分钟 |
| 连接测试 | 最大 | 并发连接数 | 5000 个连接 | **强制** | 仅 1 至 3 分钟 |
| 负载测试（逐步加压） | 微弱 | 吞吐量，逐步爬升 | 峰值 250 次请求/分钟 | 否 | 1 至 5 分钟 |
| 负载测试（逐步加压） | 低 | 吞吐量，逐步爬升 | 峰值 500 次请求/分钟 | 否 | 1 至 5 分钟 |
| 负载测试（逐步加压） | 中 | 吞吐量，逐步爬升 | 峰值 1000 次请求/分钟 | 否 | 1 至 5 分钟 |
| 负载测试（逐步加压） | 高 | 吞吐量，逐步爬升 | 峰值 2000 次请求/分钟 | 否 | 1 至 5 分钟 |
| 负载测试（逐步加压） | 强劲 | 吞吐量，逐步爬升 | 峰值 6000 次请求/分钟 | 可选 | 1 至 3 分钟（预检查通过后可达 5） |
| 负载测试（逐步加压） | 激进 | 吞吐量，逐步爬升 | 峰值 10,000 次请求/分钟 | 可选 | 1 至 3 分钟（预检查通过后可达 5） |
| 负载测试（逐步加压） | 猛烈 | 吞吐量，逐步爬升 | 峰值 15,000 次请求/分钟 | **强制** | 仅 1 至 3 分钟 |
| 负载测试（逐步加压） | 最大 | 吞吐量，逐步爬升 | 峰值 20,000 次请求/分钟 | **强制** | 仅 1 至 3 分钟 |

- **预检查：否**：测试直接开始，没有时长条件。
- **预检查：可选**（强劲/激进）：测试无需预检查即可开始（时长 1-3 分钟），但预检查通过后还会解锁 4-5 分钟的时长。
- **预检查：强制**（猛烈/最大）：没有事先通过的预检查，测试不会开始；即使通过预检查，时长也仍限制在 3 分钟（这里预检查决定的是能否使用该级别，而不是延长时长）。

上表中的“可用时长”一列只涵盖**手动模式**（最多 5 分钟）。超出这一范围，只有[时长配置文件模式 D1-D6](#时长配置文件-d1-d6配置文件模式) 允许更长的测试（最长 120 分钟）— 每个 D1-D6 配置文件自行决定在该时长下哪些级别仍然可用（`free_max_level`/`reinforced_level`，见其自身的表格）：

| 级别 | 手动模式最长时长 | 通过 D1-D6 配置文件的最长时长 |
|---|---|---|
| 微弱 / 低 / 中 / 高 | 5 分钟 | 120 分钟（D6，仅连接/负载）；请求测试为 60 分钟（D5，D6 与该类型不兼容） |
| 强劲 | 5 分钟（无预检查时 3 分钟） | 加强确认后 120 分钟（D6，连接/负载），否则 60 分钟（D5） |
| 激进 | 5 分钟（无预检查时 3 分钟） | 加强确认后 60 分钟（D5），否则 30 分钟（D4） |
| 猛烈 | 3 分钟（必须预检查） | 加强确认后 30 分钟（D4），否则 15 分钟（D3） |
| 最大 | 3 分钟（必须预检查） | 最多 5 分钟（仅 D1/D2 — 任何 D3-D6 配置文件都不提供最大级别，加强确认也不行） |

同一张表也可直接在应用中查看（帮助 → 负载参考），始终由同一组参考值生成（`domain/load/presets.py`、`domain/load/policies.py`）— 从不手工复制。

> 在**手动模式**的负载测试中，爬升和平台会自动按所选时长缩放（保留预设的比例）：1 分钟的测试也会走完从 0 到峰值的整条曲线，而不只是开头一段。在**时长配置文件模式 D1-D6** 中，同样的保证由每个配置文件的预热/爬升/平台/冷却划分原生提供 — 见[时长配置文件 D1-D6](#时长配置文件-d1-d6配置文件模式)。

### 导航

- 上/下方向键：移动光标。
- `Tab` / `Shift+Tab`：在表单字段之间移动。
- `Esc`：返回（在主屏上会确认是否退出）。
- `a`：显示帮助。
- `t`：切换主题。
- `q`：退出（需确认）。
- `r`：刷新显示，调整终端大小后很有用。
- `Ctrl+P`：命令面板（切换主题、截图、快捷键帮助）。

用 `t` 在主题之间切换：Omega-Stress 会在任何屏幕上根据检测到的终端能力自动调整颜色和显示丰富程度。在命令面板中（`Ctrl+P` → 主题）可选择全部 31 种主题（10 种 Omega 主题 + 21 种 Textual 内置主题）。

### 支持的终端

四种渲染配置，从最丰富到最简化：**完整**、**标准**、**精简**、**单色**。实际采用的是检测到的终端类型与窗口实际尺寸二者中更严格的一个（绝不比其中任何一个上限更丰富）。

| 终端 | 默认配置 |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | 完整 |
| Konsole, GNOME Terminal, Terminator, xfce4-terminal | 标准 |
| urxvt、xterm | 精简 |
| Linux TTY | 单色 |
| SSH（检测到真彩色/256 色） | 精简 |
| SSH（信号极少） | 单色 |
| 无法识别的终端 | 精简（谨慎的回退） |

当终端小于 80 列 × 24 行时，主屏之前会显示一个警告屏（从不阻止使用：应用仍可在简化模式下使用）。Konsole、GNOME Terminal 和 Terminator 通过各自特有的环境变量识别（`KONSOLE_VERSION`、`GNOME_TERMINAL_SCREEN`/`GNOME_TERMINAL_SERVICE`、`TERMINATOR_UUID`），而不是通过 `TERM`——它们会把 `TERM` 保留为通用的兼容值。xfce4-terminal 目前没有已知的等效标记，因此只有在它提供可识别的 `TERM`/`TERM_PROGRAM` 值时才会归入同一个标准配置，否则归入精简。

### 内部路径与系统路径

默认情况下，Omega-Stress 在自己的 `var/` 文件夹中工作，路径相对于启动它的目录（如设置了 `$OMEGA_STRESS_VAR_DIR` 则使用它）：

```text
var/db/app.db           # SQLite 数据库（配置档案、目标、历史）
var/settings.json       # 保存的设置（主题、渲染配置、默认文件夹）
var/exports/            # 默认的 JSON/CSV/HTML 导出
var/screenshots/        # 默认的 SVG 截图（命令面板）
var/audit.jsonl         # 审计日志（每次运行一行）
var/app.log             # 应用日志
```

默认绝不会使用系统绝对路径（例如 `/var/exports/`）— 因此开头的 `/` 是有意义的：只有导出到用户明确选择的文件夹（设置或导出屏幕）时才会离开该文件夹。

## 时长配置文件 D1-D6（配置文件模式）

手动模式（时长 1-5 分钟，按级别限制）之外的另一选择：一个**命名的时长配置文件**，总时长固定，内部分为 4 个阶段（预热、爬升、平台、冷却）。可在每个启动屏上选择（切换“时长模式：手动 / 配置文件 D1-D6”），在 CLI 中通过 `--duration-preset` 选择。

| 配置文件 | 总时长 | 预热 | 爬升 | 平台 | 冷却 | 无需确认的最高级别 | 额外级别（加强确认） | 兼容的类型 |
|---|---|---|---|---|---|---|---|---|
| D1 (quick) | 1 分钟 | 5 秒 | 10 秒 | 40 秒 | 5 秒 | 最大 | — | 请求、连接、负载 |
| D2 (short) | 5 分钟 | 15 秒 | 30 秒 | 4 分钟 | 15 秒 | 最大 | — | 请求、连接、负载 |
| D3 (standard) | 15 分钟 | 30 秒 | 1 分 30 秒 | 12 分 30 秒 | 30 秒 | 猛烈 | — | 请求、连接、负载 |
| D4 (resilience) | 30 分钟 | 1 分钟 | 3 分钟 | 25 分钟 | 1 分钟 | 激进 | 猛烈 | 请求、连接、负载 |
| D5 (extended) | 60 分钟 | 2 分钟 | 5 分钟 | 51 分钟 | 2 分钟 | 强劲 | 激进 | 请求、连接、负载 |
| D6 (soak) | 120 分钟 | 3 分钟 | 10 分钟 | 104 分钟 | 3 分钟 | 高 | 强劲 | 连接、负载（绝不用于请求） |

- “额外”级别（D4-D6）只有在准确输入屏幕上显示的加强确认文本后才可使用 — 绝不是简单地勾选一个复选框。
- D6 不包括请求测试：吞吐量测试以总量为界，对于关注长时间漂移的 2 小时配置文件毫无意义。
- 同一张表也可在应用中查看（帮助 → 时长配置文件 D1-D6）。

## 安全模式

每个启动屏上都有一个复选框（默认勾选），它**只**切换保护运行 Omega-Stress 的机器的那些保护措施（本地生成器的 CPU/内存）：

- **无论此设置如何都始终生效**：保护**被测目标**的阈值（错误率、延迟）— 关闭它们对产品而言毫无意义；这不是此复选框所管的范围。
- **安全模式开启（默认）**：如果主机本身看起来压力过大（生成器 CPU 与整机 CPU 同时偏高，而不是其中之一单独偏高 — 单个核心的正常饱和本身永远不够），测试会自动停止。
- **安全模式关闭**：这一本地保护被移除。此时会显示提示，将所选级别与本机最近一次已知的校准进行比较（见[本地校准](#本地校准)）— 仍然可以超出这一安全范围，但结果的可靠性和机器的稳定性将由用户自行负责。

在 CLI 中也可通过 `--unsafe` 使用（默认不带此参数 = 安全模式开启）。

## 本地校准

测量**本机**（绝不是被测目标）的真实承载能力：内置于 Omega-Stress 的本地回环服务器会逐级承受不断增加的负载，负载由与真实测试相同的 `httpx`/asyncio 引擎生成。

- 共 7 级，从空闲（系统背景噪声）一直到 2000 个连接 / 每秒 12,000 次请求，每一级都按健康阈值评估（生成器 CPU 与整机 CPU、可用内存、错误率、达到的吞吐量）— 最后 2 级是有条件的，如果前一级不健康就会跳过。
- 根据最后一个健康的级别得出安全范围（`VU_safe` / `RPS_safe`），留有安全余量（约 30 % 的储备），可信度随达到的深度提高。
- **V1 中仅做测量**：结果不会自动用于限制真实测试 — 它作为参考信息，尤其在[安全模式](#安全模式)关闭时有用。
- 按机器保存（非侵入式指纹：操作系统/架构/核心数/内存，绝不使用硬件地址），无需重新测量即可随时查看。

可从 TUI 的**校准**屏幕访问（“开始校准”按钮，进度逐秒显示），也可在 CLI 中使用：

```bash
omega-stress calibrate run     # 进行一次新的校准
omega-stress calibrate show    # 显示最近一次已知的校准，不重新校准
```

## 配置

一切都在 TUI 的**设置**屏幕中调整（无需手动编辑任何配置文件）：

- **主题**：10 种 Omega 主题之一，立即应用并保存。
- **渲染配置**：自动（启动时检测）或手动强制（完整/标准/精简/单色）。
- **默认导出文件夹**：预先填写导出屏幕中的“目标位置”字段。
- **默认截图文件夹**：供命令面板中的“截图”命令使用（`Ctrl+P`）。
- **清理**：最近的目标（绝不包括固定的目标）、全部目标（包括固定的目标及其授权）或全部历史 — 每一项都受单独的确认保护。

设置保存在 `var/settings.json` 中。`var/` 根目录本身可通过环境变量 `OMEGA_STRESS_VAR_DIR` 重定向（便于隔离多个实例，或用于测试）。

## 测试与质量

```bash
pytest
ruff check .
mypy src
lint-imports   # 检查 Dependency Rule（见 pyproject.toml [tool.importlinter]）
```

测试套件包含 570 多个测试（单元、集成、TUI、CLI）。如果违反了 Dependency Rule 或第三方技术的隔离，`lint-imports` 会让 CI 失败 — 见[架构](#架构)。

## 卸载

Omega-Stress 不会改动其自身文件夹之外的任何内容，只有一行可选的别名：

```bash
rm -rf ~/omega-stress
sed -i '/alias stress=/d' ~/.bashrc ~/.zshrc
```

`install.sh` 不会在 `~/omega-stress/` 之外创建任何系统软件包、服务或文件 — 不需要额外的卸载步骤。

## 已知限制

- 负载在**进程内**、单台机器上生成（`httpx`/asyncio）：这不是分布式工具 — 实际上限（见[测试数值](#测试数值)）明显低于 SaaS 负载测试服务（loader.io 等），这是有意为之的受控产品定位。在配置一般的硬件上，连接测试的激进/猛烈/最大级别发出全部目标负载所需的实际时间可能明显长于所选时长 — 此时限制实际吞吐量的是**本机**的能力，而不是目标；请使用[本地校准](#本地校准)了解适合你硬件的合理数值。
- 终端类型的自动检测依赖环境变量：xfce4-terminal 目前没有已知的可靠标记（见[支持的终端](#支持的终端)）。
- `plugins/` 是架构预留的扩展点（加载内置/外部插件），V1 中未实现：骨架已存在，但不提供任何插件。
- `var/` 相对于项目文件夹（不是 XDG）：面向本地单用户使用，不适合同一台机器上的多用户共享。
- **手动模式**的负载测试（逐步加压）在平台之后没有降压（“cooldown”）阶段 — 只有[时长配置文件 D1-D6](#时长配置文件-d1-d6配置文件模式) 才原生包含全部 4 个阶段。
- 通过的预检查不与特定目标绑定：在 24 小时内对之后任何猛烈/最大级别的启动都有效，而不仅限于被预检查的目标。
- [本地校准](#本地校准)只做测量，尚未自动应用其安全范围来限制真实测试 — 这是一项有意单独处理、尚未开始的工作。

## 许可证

MIT — 见 `LICENSE`。
