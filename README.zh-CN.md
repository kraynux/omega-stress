<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT 许可证（见 LICENSE 文件） -->
<div align="center">
  <img src="docs/assets/omega-stress.png" alt="Omega-Stress" width="256">
</div>

# 🗲 OMEGA-STRESS

**受控 HTTP 压力测试工作站**

> 由 **kraynux** 为 **Omega-server** 开发  
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

官方页面：[OMEGA-STRESS](https://kraynux.snake-mackarel.ts.net/omega-stress/) &nbsp; 预览：[Screenshots](https://kraynux.snake-mackarel.ts.net/omega-stress/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

**语言：**  
[Français](README.md) · [English](README.en.md) · [Español](README.es.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md)


**Omega-Stress** 是一个本地终端应用（基于 [Textual](https://github.com/Textualize/textual) 的 TUI + 可脚本化 CLI），用于以受控且可复用的方式执行 HTTP 压力测试：固定配置文件、历史记录、重放、详细导出（JSON/CSV/HTML）以及明确的安全边界。

项目遵循 **Clean Architecture** 原则，清晰分离业务领域、编排层、基础设施和用户界面。



---

## 目录

- [概述](#概述)
- [功能](#功能)
- [架构](#架构)
- [要求](#要求)
- [安装](#安装)
- [使用](#使用)
- [D1-D6 时长配置文件](#d1-d6-时长配置文件配置文件模式)
- [安全模式](#安全模式)
- [本地校准](#本地校准)
- [配置](#配置)
- [测试与质量](#测试与质量)
- [卸载](#卸载)
- [已知限制](#已知限制)
- [许可证](#许可证)

## 概述

### 目标

## Omega-Stress 的功能（V1 目标）

- 三类受控测试：**请求测试**（吞吐量）、**连接测试**（并发数）和**压力测试**（渐进式增加负载）。
- **8 个强度等级**（低/基础/中/高/强力/激进/暴力/最大），采用三级预检查模型（从不限制 / 可选限制 / 强制限制；参阅[测试值](#测试值)）。
- **两种时长模式**：手动模式（1 到 5 分钟，受等级限制）或命名的 **D1-D6 配置文件**（固定总时长，包含预热/爬升/平台/冷却；参阅[D1-D6 时长配置文件](#d1-d6-时长配置文件配置文件模式)）。
- **安全模式**（默认启用，可在每次启动时禁用）：保护主机 CPU/内存的本地护栏，与保护测试目标的阈值相互独立；参阅[安全模式](#安全模式)。
- **持久化本地校准**：通过 loopback 服务器和逐级增加的负载，测量主机的实际容量（从不测量目标）；参阅[本地校准](#本地校准)。
- 固定、可复用并带历史记录的配置文件。
- 对未固定目标进行每次测试前，都必须明确确认授权。
- 自动停止阈值；永远不会执行无上限负载。
- 详细 JSON/CSV/HTML 导出（阶段、每个区间的指标、结论和诊断）。
- 支持自动化（cron、CI）的非交互 CLI，调用与 TUI 完全相同的用例。
- 自动适配终端（主题和可降级的渲染配置）。

## 项目不做什么

- 不替代网络扫描工具：产品术语和安全姿态明确使用“压力测试”，而不是“扫描”。
- 不实现外部压力引擎（k6 等）：使用原生 `httpx`/asyncio 生成负载。
- 不会在缺少边界和授权确认时启动测试。
- 不是分布式压力测试工具：负载生成在一台机器、一个进程中运行；参阅[已知限制](#已知限制)。

## 功能

- **三类测试**，每类包含 8 个强度等级（低/基础/中/高/强力/激进/暴力/最大）；确切数值见[负载参考](#测试值)表。
- **固定测试配置文件**：名称、目标、类型、强度、时长和错误阈值；创建一次后，可从 TUI 或 CLI 以相同参数重复执行。
- **命名的 D1-D6 时长配置文件**（“配置文件”模式）是手动模式的替代方案：固定总时长为 1 到 120 分钟，包含预热/爬升/平台/冷却，并同时限制可用强度等级；参阅[D1-D6 时长配置文件](#d1-d6-时长配置文件配置文件模式)。
- **安全模式**在每个启动界面默认勾选：如果主机（而非目标）似乎处于危险状态，则停止测试。可以在明确了解后禁用，并显示选定等级与最近一次校准结果的比较提醒；参阅[安全模式](#安全模式)。
- **持久化本地校准**：通过内置 loopback 服务器的 7 个递增负载阶段，测量机器实际可承受的负载；可从“校准”界面查看；参阅[本地校准](#本地校准)。
- **固定目标**：固定地址无需每次启动时重新勾选授权；最近的未固定目标仍会显示（最多 10 个），但不会因此获得隐式授权。
- **完整历史记录**：每次运行都记录结论、指标、每个区间的时间线以及安全模式状态；与固定配置文件关联的运行可以原样重放。
- **详细导出**：JSON（可重新导入的原始数据）、CSV（表格分析）或 HTML（可读报告，可选项目的 10 种调色板）。
- **自动预检查**：暴力/最大测试前强制执行；强力/激进测试可选，但通过后可以解锁更长时长，有效期为 24 小时。
- **实时监控**：运行中显示可靠的进度倒计时（剩余时间直接计算，从不估算），每个区间更新吞吐量/错误数/p95 延迟，并可在不退出应用的情况下手动停止。
- **集中设置**：主题（10 个 Omega 调色板和所有 Textual 内置主题，通过命令面板共 31 个）、渲染配置（自动或强制）、导出与截图目录，以及目标/历史清理。
- **内置帮助**（`a` 键）：键盘快捷键、每个界面的说明（包括校准和安全模式）、负载参考表和 D1-D6 时长配置表。
- **可脚本化 CLI**（`omega-stress profile|run|history|export|calibrate ...`）：与 TUI 使用完全相同的用例，并支持用于自动化的 `--json` 输出。
- **自动终端适配**：启动时检测终端类型和尺寸，并据此调整主题与显示丰富度；参阅[支持的终端](#支持的终端)。

## 架构

基于 Clean Architecture + Ports & Adapters，划分为 9 个包（`app/`、`core/`、`domain/`、`application/`、`ports/`、`infrastructure/`、`interfaces/`、`plugins/`、`shared/`）。
完整说明：`ARCHITECTURE.md`。

```text
src/omega_stress/
├── app/              启动引导和依赖注入容器（手动组装，不使用 DI 框架）
├── core/             跨领域词汇：枚举、根异常、Result/Ok/Err、系统能力
├── domain/           纯业务逻辑：负载、配置文件、运行、目标、主题和终端；无 I/O
├── application/      编排：命令、查询和执行管线（guards/hooks）
├── ports/            适配器所需的 Protocol/ABC 契约（repositories、exporters、负载生成器……）
├── infrastructure/  具体实现：SQLite、JSON/CSV/HTML 导出器、httpx/asyncio 生成器、终端检测和系统探针
├── interfaces/       两个独立的展示适配器：TUI（Textual）和 CLI（argparse）
├── plugins/          预留的扩展点（插件加载）；V1 仅有脚手架，尚未实现
└── shared/           无业务依赖的跨领域工具（可注入时钟、ID 生成）
```

### 设计原则

- `domain/` 不包含 I/O 或基础设施依赖：它是纯业务逻辑，可以完全在不使用 mock 的情况下测试。
- `application/` 通过 domain 和 ports 编排用例，从不直接调用 `infrastructure/` 中的具体类。
- `infrastructure/` 实现 ports，`application/` 和 `domain/` 不会直接导入它；只有 `interfaces/` 与 `app/` 可以引用它。
- `interfaces/` 不得直接调用 `infrastructure/` 或 `subprocess`：只能通过 `application/` 的 commands/queries 和自身控制器调用。
- `ports/` 定义适配器契约（Protocol），不包含实现。
- `core/` 汇集所有层共用的词汇，但不在此编码数值型业务规则（阈值、时长和预设始终位于 `domain/*/policies.py`）。

Dependency Rule（外部层只能依赖内部层）以及第三方技术隔离（`textual`、`sqlite3`、`httpx`、`jinja2` 各自限制在指定入口）会在每次运行 `lint-imports` 时自动检查；参阅[测试与质量](#测试与质量)。

## 要求

- Python ≥ 3.10。
- 推荐使用 [`uv`](https://github.com/astral-sh/uv) 管理依赖，也可以使用标准 `pip`。

### 系统

- Linux，优先支持 Arch Linux 及兼容发行版。
- Python 3.10 或更高版本。
- 不需要 root 权限：Omega-Stress 只以普通用户身份发送 HTTP 请求。

## 安装

官方归档以 `.tar.gz` 格式提供。安装前请验证完整性：

```bash
sha256sum omega-stress.tar.gz
```

### 方法 1 — 安装脚本

```bash
[ -d omega-stress ] && echo "ℹ️ 已在此处解压，跳过该步骤。" || tar -xzf omega-stress.tar.gz
[ -d ~/omega-stress ] && echo "ℹ️ ~/omega-stress 已存在，跳过移动。" || mv omega-stress ~/
cd ~/omega-stress/
chmod +x install.sh
./install.sh
```

### 方法 2 — 可重复执行的完整安装

可以直接复制粘贴并安全地重复执行：每一步都会跳过已经完成的操作。

```bash
( [ -d omega-stress ] || tar -xzf omega-stress.tar.gz ) && \
( [ -d ~/omega-stress ] || mv omega-stress ~/ ) && \
cd ~/omega-stress && chmod +x install.sh && ./install.sh
```

`install.sh` 会：

1. 在不存在时创建 `.venv` 虚拟环境。
2. 安装依赖（`pip install -e .`；`pyproject.toml` 仍是唯一可信来源）。
3. 为 `omega-stress.sh` 和 `install.sh` 添加执行权限。
4. 将 `stress` 别名添加到 `~/.bashrc` 和 `~/.zshrc`，如果已存在则不会重复添加。

## 开发安装

```bash
uv sync --all-extras
# 或不使用 uv：
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### 启动

```bash
cd ~/omega-stress
./omega-stress.sh

# 如果已创建别名，也可以在新终端中直接输入 "stress"
```

启动器会：

1. 检测 `.venv`、`venv` 或系统 Python。
2. 将 `PYTHONPATH` 设置为 `src/`。
3. 运行 `python -m omega_stress`：无参数时打开 TUI，有参数时转交 CLI。

### CLI 使用

```bash
omega-stress profile list                                     # 列出配置文件
omega-stress profile create --name "API 探测" --target-id t-1 \
    --family request --level basic --duration-minutes 1 --max-error-rate 0.05
omega-stress profile freeze <profile-id>                       # 固定配置文件

# 每次暴力/最大启动前必须进行预检查（强力/激进可选）
omega-stress run precheck --target-id t-1 --target-url https://example.org --confirm

omega-stress run request --target-id t-1 --target-url https://example.org \
    --level basic --duration-minutes 1 --max-error-rate 0.05 --confirm
omega-stress run connection --target-id t-1 --target-url https://example.org \
    --level medium --duration-minutes 3 --max-error-rate 0.05 --confirm
omega-stress run ramp --target-id t-1 --target-url https://example.org \
    --level powerful --duration-minutes 3 --max-error-rate 0.05 --confirm --precheck-validated

# 使用 D1-D6 配置文件模式代替 --duration-minutes（二者互斥）
# D4（韧性）允许激进级别无需额外条件，暴力级别需要加强确认
omega-stress run request --target-id t-1 --target-url https://example.org \
    --level violent --duration-preset d4 --max-error-rate 0.05 --confirm \
    --precheck-validated --confirmation-text 我确认目标已获授权

# --unsafe 禁用安全模式（本地 CPU/内存护栏）；默认不指定，安全模式保持启用
omega-stress run connection --target-id t-1 --target-url https://example.org \
    --level violent --duration-minutes 1 --max-error-rate 0.05 --confirm \
    --precheck-validated --unsafe

omega-stress run replay <run-id> --confirm                     # 重放与固定配置文件关联的运行

omega-stress history list                                      # 运行历史
omega-stress history show <run-id>                              # 运行详情

omega-stress export <run-id> --format html --destination var/exports --theme omega-base

omega-stress calibrate run                                      # 校准本机
omega-stress calibrate show                                     # 显示最近一次已知校准
```

`--confirm` 等价于 TUI 中的授权复选框。对于尚未固定并授权的目标，这是必需参数。`--target-id`/`--target-url` 使用相同值表示手动的非固定目标；使用已固定目标的标识符，可以避免每次启动都指定 `--confirm`。

在 `history`、`export` 或 `calibrate` 后添加 `--json`，即可输出适合 cron/CI 使用的机器可读数据。

## D1-D6 时长配置文件（配置文件模式）

这是手动模式（按等级限制 1–5 分钟）的替代方案：一个**命名的时长配置文件**，具有固定总时长和 4 个内部阶段（预热、爬升、平台和冷却）。每个启动界面都可以选择它（切换“时长模式：手动 / D1-D6 配置文件”），CLI 则使用 `--duration-preset`。

| 配置文件 | 总时长 | 预热 | 爬升 | 平台 | 冷却 | 无确认的最高等级 | 额外等级（加强确认） | 兼容类型 |
|---|---|---|---|---|---|---|---|---|
| D1 (quick) | 1 分钟 | 5 秒 | 10 秒 | 40 秒 | 5 秒 | 最大 | — | 请求、连接、压力 |
| D2 (short) | 5 分钟 | 15 秒 | 30 秒 | 4 分钟 | 15 秒 | 最大 | — | 请求、连接、压力 |
| D3 (standard) | 15 分钟 | 30 秒 | 1 分 30 秒 | 12 分 30 秒 | 30 秒 | 暴力 | — | 请求、连接、压力 |
| D4 (resilience) | 30 分钟 | 1 分钟 | 3 分钟 | 25 分钟 | 1 分钟 | 激进 | 暴力 | 请求、连接、压力 |
| D5 (extended) | 60 分钟 | 2 分钟 | 5 分钟 | 51 分钟 | 2 分钟 | 强力 | 激进 | 请求、连接、压力 |
| D6 (soak) | 120 分钟 | 3 分钟 | 10 分钟 | 104 分钟 | 3 分钟 | 高 | 强力 | 连接、压力（从不支持请求） |

- 额外等级（D4-D6）只能通过准确输入屏幕显示的加强确认文本来启用；简单勾选复选框永远不够。
- D6 不包含请求测试：吞吐量测试受总量限制，不适合用于关注时间漂移的两小时配置文件。
- 应用内也提供相同的表格（帮助 → D1-D6 时长配置文件）。

## 安全模式

每个启动界面都有一个复选框（默认勾选），它**只**控制保护 Omega-Stress 所在机器的护栏（本地生成器的 CPU/内存）：

- **无论此设置如何，以下保护始终启用**：保护**测试目标**的阈值（错误率和延迟）。禁用这些阈值没有产品意义；此复选框不控制它们。
- **安全模式启用（默认）**：如果主机本身似乎处于压力之下，测试会自动停止（生成器 CPU 和整机 CPU 同时较高；只有一个指标升高永远不足以触发停止）。
- **安全模式禁用**：移除本地护栏。之后会显示提醒，将选择的等级与本机最近一次已知校准进行比较（参阅[本地校准](#本地校准)）。仍然可以超出该范围，但结果可靠性和机器稳定性由用户自行负责。

CLI 中也可以通过 `--unsafe` 使用（默认不指定表示安全模式启用）。

## 本地校准

测量**本机**的实际容量（从不测量测试目标）：Omega-Stress 内置的 loopback 服务器接收逐级增加的负载，这些负载使用与真实测试相同的 `httpx`/asyncio 引擎生成。

- 7 个阶段，从空闲状态（系统背景噪声）到 2000 个连接 / 12,000 请求每秒；每个阶段都依据健康阈值进行评估（生成器 CPU 与全局 CPU、可用内存、错误率和达到的吞吐量）。最后 2 个阶段为条件阶段，如果上一阶段不健康则跳过。
- 根据最后一个健康阶段生成安全范围（`VU_safe` / `RPS_safe`），保留约 30% 的安全余量，并根据达到的阶段深度提高可信度。
- **V1 仅执行测量**：结果不会自动用于限制真实测试，只作为信息参考，尤其是在禁用[安全模式](#安全模式)时。
- 按机器持久化保存，使用非侵入式指纹（操作系统/架构/核心数/RAM，从不使用硬件地址），随时可以查看，无需重新测量。

可从 TUI 的**校准**界面使用（“运行校准”，逐秒显示进度），也可以通过 CLI：

```bash
omega-stress calibrate run     # 运行新的校准
omega-stress calibrate show    # 显示最近一次校准，不重新运行
```

## 配置

所有内容都可以在 TUI 的**设置**界面中配置，无需手动编辑配置文件：

- **主题**：从 10 个 Omega 主题中选择，立即应用并持久化。
- **渲染配置**：自动（启动时检测）或手动强制（完整/标准/精简/单色）。
- **默认导出目录**：预先填写导出界面的目标字段。
- **默认截图目录**：由命令面板中的“截图”命令（`Ctrl+P`）使用。
- **清理**：最近目标（从不清理固定目标）、所有目标（包括固定目标及其授权）或完整历史；每项操作都有独立确认。

设置保存在 `var/settings.json`。可以通过 `OMEGA_STRESS_VAR_DIR` 重定向 `var/` 根目录，适合隔离多个实例或测试。

## 测试与质量

```bash
pytest
ruff check .
mypy src
lint-imports   # 检查 Dependency Rule（参阅 pyproject.toml 中的 [tool.importlinter]）
```

测试套件包含超过 570 个测试（单元、集成、TUI 和 CLI）。如果违反 Dependency Rule 或第三方技术隔离规则，`lint-imports` 会使 CI 失败；参阅[架构](#架构)。

## 卸载

Omega-Stress 不会修改自身目录和一条可选别名行之外的任何内容：

```bash
rm -rf ~/omega-stress
sed -i '/alias stress=/d' ~/.bashrc ~/.zshrc
```

`install.sh` 不会在 `~/omega-stress/` 之外创建系统包、服务或文件，因此无需额外卸载操作。

## 已知限制

- **单机进程内负载生成**（`httpx`/asyncio）：这不是分布式工具。实际限制（参阅[测试值](#测试值)）有意低于 loader.io 等 SaaS 压力测试服务。在配置较低的硬件上，连接测试的激进/暴力/最大等级可能需要明显超过所选时长，才能产生完整目标负载；实际吞吐量受**本机**而不是目标的能力限制。请使用[本地校准](#本地校准)确定适合硬件的值。
- 自动终端类型检测依赖环境变量；目前尚无已知的可靠 xfce4-terminal 标识（参阅[支持的终端](#支持的终端)）。
- `plugins/` 是为内置/外部插件加载预留的架构扩展点，V1 尚未实现：已有脚手架，但没有随项目发布插件。
- `var/` 相对于项目目录（不是 XDG）：面向本地单用户使用，不适合同一机器上的多用户共享。
- 手动**压力测试**模式在平台阶段后没有冷却阶段；只有[D1-D6 时长配置文件](#d1-d6-时长配置文件配置文件模式)原生包含全部 4 个阶段。
- 已通过验证的预检查不绑定到特定目标：在 24 小时内对任何后续暴力/最大启动都有效，而不仅仅是预检查过的目标。
- [本地校准](#本地校准)目前只进行测量，还不会自动应用安全范围来限制真实测试；这是一个刻意独立且尚未开始的工作项。

## 许可证

MIT — 参阅 `LICENSE`。
