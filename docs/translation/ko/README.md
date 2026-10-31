<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT 라이선스 (LICENSE 파일 참조) -->
<div align="center">
  <img src="../../assets/omega-stress.png" alt="Omega-Stress" width="384">
</div>

# 🗲 OMEGA-STRESS

**통제된 HTTP 부하 테스트 스테이션**

> [kraynux](https://github.com/kraynux)가 [Omega-Server](https://kraynux.snake-mackarel.ts.net)를 위해 개발   

공식 페이지: [OMEGA-STRESS](https://kraynux.snake-mackarel.ts.net/omega-stress/) &nbsp; 미리 보기: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-stress/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 인터페이스와 내보낸 보고서는 **17개 언어**로 제공됩니다 — [인터페이스 언어](#인터페이스-언어)를 참조하세요.  
**언어:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)



**Omega-Stress**는 로컬 터미널 애플리케이션([Textual](https://github.com/Textualize/textual) TUI + 스크립트 가능한 CLI)으로, 범위가 정해지고 재현 가능한 HTTP 부하 테스트를 조율합니다. 고정 프로필, 기록, 재실행, 상세 내보내기(JSON/CSV/HTML), 명확한 안전 한도를 갖추고 있습니다.

이 프로젝트는 **Clean Architecture** 원칙을 따르며, 업무 도메인, 오케스트레이션, 인프라, 사용자 인터페이스를 명확히 분리합니다.
---

## 목차

- [개요](#개요)
- [기능](#기능)
- [아키텍처](#아키텍처)
- [사전 요구 사항](#사전-요구-사항)
- [설치](#설치)
- [사용법](#실행)
- [시간 프로필 D1-D6](#시간-프로필-d1-d6-프로필-모드)
- [안전 모드](#안전-모드)
- [로컬 보정](#로컬-보정)
- [구성](#구성)
- [테스트와 품질](#테스트와-품질)
- [제거](#제거)
- [알려진 제한 사항](#알려진-제한-사항)
- [라이선스](#라이선스)

## 개요

### 목표

## Omega-Stress가 하는 일 (V1 목표)

- 통제된 세 가지 테스트 계열: **요청 테스트**(처리량), **연결 테스트**(동시성), **부하 테스트**(점진적 증가).
- **8단계 강도**(미약/낮음/중간/높음/강력/공격적/격렬/최대)와 3단계 사전 점검 모델(필수 아님 / 선택적 필수 / 항상 필수 — [테스트 값](#테스트-값) 참조).
- **두 가지 시간 모드**: 수동(1~5분, 레벨별 상한) 또는 **이름 있는 프로필 D1-D6**(워밍업/상승/유지/하강을 포함한 고정 총 시간 — [시간 프로필 D1-D6](#시간-프로필-d1-d6-프로필-모드) 참조).
- **안전 모드**(기본 활성, 실행할 때마다 비활성화 가능): 호스트 머신의 CPU/메모리를 지키는 로컬 보호 장치로, 테스트 대상을 보호하는 임계값과는 별개입니다 — [안전 모드](#안전-모드) 참조.
- **저장되는 로컬 보정**: 로컬 루프백 서버에 단계적으로 부하를 높여 호스트 머신(대상이 아님)의 실제 처리 능력을 측정합니다 — [로컬 보정](#로컬-보정) 참조.
- 고정되고 재사용 가능하며 기록에 남는 프로필 — **선택 사항**: 프로필 없이도 대상을 직접 선택하거나 입력하면 수동 모드에서 테스트가 똑같이 잘 동작합니다.
- 고정되지 않은 대상에 대해서는 실행할 때마다 명시적인 권한 확인이 필수입니다.
- 자동 중지 임계값이 있으며, 한도 없는 부하는 절대 걸지 않습니다.
- 상세한 JSON/CSV/HTML 내보내기(단계, 구간별 지표, 판정, 진단).
- 자동화(cron, CI)를 위한 비대화형 CLI 모드로, TUI와 완전히 같은 사용 사례를 호출합니다.
- 터미널에 자동 적응(테마 + 단순화 가능한 표시 프로필).

## 이 프로젝트가 하지 않는 일

- 네트워크 스캔 도구를 대체하지 않습니다 — 용어와 제품의 입장은 의도적으로 "부하 테스트"이며, 결코 "스캔"이 아닙니다.
- 외부 부하 엔진(k6 등)을 구현하지 않습니다 — `httpx`/asyncio를 사용한 자체 부하 생성입니다.
- 한도와 권한 확인 없이 실행을 시작하는 일은 결코 없습니다.
- 분산형 부하 도구가 아닙니다: 부하 생성은 한 대의 머신, 하나의 프로세스에서 실행됩니다 — [알려진 제한 사항](#알려진-제한-사항) 참조.

## 기능

- **세 가지 테스트 계열**, 각각 8단계 강도(미약/낮음/중간/높음/강력/공격적/격렬/최대) — 레벨별 정확한 값은 [부하 기준점](#테스트-값) 표를 참조하세요.
- **고정 테스트 프로필**: 이름, 대상, 계열, 강도, 시간, 오류 임계값 — 한 번 만들면 TUI나 CLI에서 똑같이 다시 실행할 수 있습니다.
- **이름 있는 시간 프로필 D1-D6**("프로필" 모드), 수동 모드의 대안: 워밍업/상승/유지/하강을 포함한 고정 총 시간(1~120분)이며, 사용할 수 있는 레벨도 제한합니다 — [시간 프로필 D1-D6](#시간-프로필-d1-d6-프로필-모드) 참조.
- **안전 모드**, 모든 실행 화면에서 기본으로 체크됨: 호스트 머신(대상이 아님)이 위험해 보이면 테스트를 중단합니다. 알고서 비활성화할 수 있으며, 이때 선택한 레벨과 최근 보정을 비교하는 안내가 표시됩니다 — [안전 모드](#안전-모드) 참조.
- **저장되는 로컬 보정**: 머신이 실제로 얼마나 견딜 수 있는지 측정하며(내장 로컬 루프백 서버를 대상으로 점점 커지는 7단계 부하), 보정 화면에서 확인할 수 있습니다 — [로컬 보정](#로컬-보정) 참조.
- **고정된 대상**: 고정한 주소는 실행할 때마다 권한을 다시 체크할 필요가 없습니다. 고정되지 않은 최근 대상은 계속 표시되지만(최대 10개) 암묵적 권한은 없습니다. 고정된 대상은 서로 독립적인 두 가지 방법으로 쓸 수 있습니다: 프로필 없이 수동 모드에서 테스트를 바로 실행하거나, 고정 프로필을 만들 때 기본 대상으로 사용합니다.
- **완전한 기록**: 모든 실행이 기록됩니다(판정, 지표, 구간별 타임라인, 사용한 안전 모드). 고정 프로필에 연결된 실행은 똑같이 다시 실행할 수 있습니다.
- **상세 내보내기**: JSON(다시 가져올 수 있는 원시 데이터), CSV(표 형식 분석), HTML(읽기 쉬운 보고서, 프로젝트의 10개 팔레트 중 테마 선택). HTML 보고서는 설정에서 선택한 언어("내보내기 언어", 기본값은 인터페이스 언어)로 작성되며, JSON과 CSV는 데이터로 남아 번역되지 않습니다.
- **사전 점검**: 격렬/최대 테스트 전에는 매번 자동이며 필수, 강력/공격적에서는 선택(다만 더 긴 시간을 열어 줌). 유효 기간(24시간)이 있습니다.
- 실행 중인 테스트의 **실시간 모니터링**: 신뢰할 수 있는 카운트다운이 있는 진행 표시(남은 시간은 추정이 아니라 직접 계산), 처리량/오류/p95 지연 시간을 구간마다 갱신, 앱을 나가지 않고 수동 중지 가능.
- **중앙 집중식 설정**: 테마(Omega 팔레트 10개 + Textual 내장 테마 전부, 명령 팔레트로 총 31개), 표시 프로필(자동 또는 고정), 내보내기와 스크린샷 폴더, 대상/기록 삭제.
- **내장 도움말**(`a` 키): 키보드 단축키, 화면별 설명(보정과 안전 모드 포함), 부하 값 참조 표, 시간 프로필 D1-D6 표.
- **스크립트 가능한 CLI**(`omega-stress profile|run|history|export|calibrate ...`), TUI와 완전히 같은 사용 사례이며 자동화용 `--json` 출력을 제공합니다.
- **터미널에 자동 적응**: 시작 시 종류와 크기를 감지하고 테마와 표시의 풍부함을 조정합니다([지원 터미널](#지원-터미널) 참조).

## 아키텍처

Clean Architecture + Ports & Adapters, 9개 패키지(`app/`, `core/`, `domain/`, `application/`, `ports/`, `infrastructure/`, `interfaces/`, `plugins/`, `shared/`).
전체 내용: `ARCHITECTURE.md`.

```text
src/omega_stress/
├── app/              부트스트랩과 의존성 주입 컨테이너(수동 연결, DI 프레임워크 없음)
├── core/             공통 어휘: 열거형, 루트 예외, Result/Ok/Err, 시스템 기능
├── domain/           순수 업무 로직: 부하, 프로필, 실행, 대상, 테마, 터미널 — I/O 없음
├── application/      오케스트레이션: commands(동작), queries(조회), 실행 파이프라인(guards/hooks)
├── ports/            어댑터가 기대하는 Protocol/ABC 계약(저장소, 내보내기, 부하 생성기...)
├── infrastructure/   구체 구현: SQLite, JSON/CSV/HTML 내보내기, httpx/asyncio 생성기, 터미널 감지, 시스템 프로브
├── interfaces/       서로 독립적인 두 표시 어댑터: TUI(Textual)와 CLI(argparse)
├── plugins/          예약된 확장 지점(플러그인 로딩) — 뼈대는 있으나 V1에서는 미구현
└── shared/           업무 의존성 없는 공통 유틸리티(주입 가능한 시계, 식별자 생성)
```

### 설계 원칙

- `domain/`에는 I/O도 인프라 의존성도 없습니다 — 순수 업무 로직이며 목(mock) 없이 완전히 테스트할 수 있습니다.
- `application/`은 도메인과 포트를 통해 사용 사례를 조율하며, `infrastructure/`의 구체 클래스를 직접 사용하지 않습니다.
- `infrastructure/`는 포트를 구현하며 `application/`이나 `domain/`에서 직접 가져오는 일이 없습니다 — 참조하는 것은 `interfaces/`와 `app/`뿐입니다.
- `interfaces/`는 `infrastructure/`나 `subprocess`를 직접 호출해서는 안 됩니다: `application/`(commands/queries)과 자체 컨트롤러를 거칠 뿐입니다.
- `ports/`는 어댑터가 기대하는 계약(Protocol)을 정의하며, 구현은 결코 담지 않습니다.
- `core/`는 모든 계층이 공유하는 어휘를 모으지만, 수치가 있는 업무 규칙(임계값, 시간, 프리셋 — 항상 `domain/*/policies.py`에 있음)은 절대 담지 않습니다.

Dependency Rule(바깥 계층에서 안쪽 계층으로만)과 서드파티 기술 격리(`textual`, `sqlite3`, `httpx`, `jinja2` 각각 지정된 진입점으로 제한)는 `lint-imports`를 실행할 때마다 자동으로 검증됩니다([테스트와 품질](#테스트와-품질) 참조).

## 사전 요구 사항

- Python ≥ 3.10
- 의존성 관리는 [`uv`](https://github.com/astral-sh/uv) 권장(없으면 표준 `pip`)

### 시스템

- Linux, 특히 Arch Linux와 호환 배포판.
- Python 3.10 이상.
- root 권한 불필요: Omega-Stress는 일반 사용자로 외부 방향 HTTP 호출만 수행합니다.

## 설치

공식 아카이브는 `.tar.gz` 형식으로 제공됩니다. 설치 전에 무결성을 확인하세요:

```bash
sha256sum omega-stress.tar.gz
```

### 방법 1 — 설치 스크립트

```bash
[ -d omega-stress ] && echo "ℹ️ 이미 여기에 압축이 풀려 있어 이 단계를 건너뜁니다." || tar -xzf omega-stress.tar.gz
[ -d ~/omega-stress ] && echo "ℹ️ ~/omega-stress가 이미 있어 이동을 건너뜁니다." || mv omega-stress ~/
cd ~/omega-stress/
chmod +x install.sh
./install.sh
```

### 방법 2 — 견고한 일괄 설치

이 명령은 그대로 복사해 붙여 넣을 수 있고, 여러 번 실행해도 오류가 나지 않습니다: 각 단계는 이미 끝난 작업을 건너뜁니다.

```bash
( [ -d omega-stress ] || tar -xzf omega-stress.tar.gz ) && \
( [ -d ~/omega-stress ] || mv omega-stress ~/ ) && \
cd ~/omega-stress && chmod +x install.sh && ./install.sh
```
`install.sh`:

1. 가상 환경 `.venv`가 없으면 만듭니다.
2. 의존성을 설치합니다(`pip install -e .`; `pyproject.toml`이 유일한 기준 정보입니다).
3. `omega-stress.sh`와 `install.sh`를 실행 가능하게 합니다.
4. 별칭 `stress`를 `~/.bashrc`와 `~/.zshrc`에 추가합니다(이미 있으면 중복하지 않음).

## 설치 (개발)

```bash
uv sync --all-extras
# 또는 uv 없이:
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```


### 실행

```bash
cd ~/omega-stress
./omega-stress.sh

# 별칭을 만들었다면 새 터미널에서 "stress"만 입력하면 됩니다
```

실행기는:

1. `.venv`, `venv` 또는 시스템 Python을 감지합니다.
2. `PYTHONPATH`를 `src/`로 설정합니다.
3. `python -m omega_stress`를 실행합니다 — 인수가 없으면 TUI를 열고, 인수가 있으면 CLI로 넘깁니다.

### 인터페이스 언어

인터페이스는 17개 언어로 제공됩니다: 프랑스어, 영어, 스페인어, 포르투갈어(브라질), 이탈리아어, 독일어, 네덜란드어, 폴란드어, 러시아어, 중국어 간체, 베트남어, 태국어, 인도네시아어, 일본어, 한국어, 힌디어, 아랍어. 설정("Langue / Language")에서 선택하며 인터페이스를 다시 시작한 뒤 적용됩니다. 변수 `OMEGA_STRESS_LANG`(예: `OMEGA_STRESS_LANG=ko ./omega-stress.sh`)으로 한 세션 동안 언어를 강제할 수 있습니다. omega-suite에서 실행하면 omega-stress는 스위트의 언어를 따릅니다. Linux 텍스트 콘솔(TTY)에서는 라틴 문자가 아닌 언어가 그 세션 동안 영어로 표시됩니다. 명령줄은 프랑스어로 유지됩니다.

### CLI 사용법

```bash
omega-stress profile list                                     # 프로필 목록
omega-stress profile create --name "API 탐색" --target-id t-1 \
    --family request --level bas --duration-minutes 1 --max-error-rate 0.05
omega-stress profile freeze <profile-id>                       # 프로필 고정

# 격렬/최대 실행 전에는 매번 사전 점검 필수(강력/공격적은 선택)
omega-stress run precheck --target-id t-1 --target-url https://exemple.org --confirm

omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level bas --duration-minutes 1 --max-error-rate 0.05 --confirm
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level moyen --duration-minutes 3 --max-error-rate 0.05 --confirm
omega-stress run ramp --target-id t-1 --target-url https://exemple.org \
    --level puissant --duration-minutes 3 --max-error-rate 0.05 --confirm --precheck-validated

# --duration-minutes 대신 프로필 모드 D1-D6(함께 쓸 수 없음)
# D4 (resilience)는 공격적을 조건 없이, 격렬을 강화된 확인과 함께 허용
omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-preset d4 --max-error-rate 0.05 --confirm \
    --precheck-validated --confirmation-text JE_CONFIRME_LA_CIBLE_AUTORISEE

# --unsafe는 안전 모드(로컬 CPU/메모리 보호)를 끔. 기본값은 지정 안 함
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-minutes 1 --max-error-rate 0.05 --confirm \
    --precheck-validated --unsafe

omega-stress run replay <run-id> --confirm                     # 고정 프로필에 연결된 실행을 다시 실행

omega-stress history list                                      # 실행 기록
omega-stress history show <run-id>                              # 실행 상세

omega-stress export <run-id> --format html --destination var/exports --theme omega-base

omega-stress calibrate run                                      # 이 머신의 보정 실행
omega-stress calibrate show                                     # 알려진 마지막 보정 표시
```

`--level` 값(`faible`, `bas`, `moyen`, `haut`, `puissant`, `agressif`, `violent`, `maximum`)과 확인 문구는 명령줄의 나머지 부분과 마찬가지로 프랑스어로 유지됩니다.

`--confirm`은 TUI의 권한 체크박스에 해당하는 명령줄 옵션입니다: 권한이 있는 것으로 고정되지 않은 모든 대상에 필수입니다. `--target-id`/`--target-url`이 같으면 수동(고정되지 않은) 대상을 뜻합니다. 실행할 때마다 `--confirm`을 붙이지 않으려면 이미 고정된 대상의 식별자를 사용하세요.

`history`/`export`/`calibrate`에 `--json`을 붙이면 기계가 읽을 수 있는 출력이 나와 cron/CI에서 유용합니다.

### 일반적인 흐름

1. 처음 실행하면 메인 화면에 다음이 표시됩니다: 프로필, 요청 테스트, 연결 테스트, 부하 테스트, 기록, 대상, 보정, 설정, 도움말.
2. 테스트 화면 상단에서 고정 프로필(선택 사항)을 고를 수도 있습니다: 대상과 조건을 정하는 두 가지 방법이며, 한 번의 실행에서 함께 쓰이지 않습니다 —
   - **프로필 사용**: 선택하면 대상/강도/시간/오류 임계값이 채워지고 수동 대상 입력란은 사라집니다(더 이상 필요 없음). 채워진 값은 실행 전에 바꿀 수 있습니다.
   - **프로필 없이(수동 모드)**: 고정/최근 대상을 목록에서 고르거나 새로 입력하고, 권한 있는 것으로 고정되지 않았다면 권한을 체크한 뒤, 강도/시간(수동 또는 시간 프로필 D1-D6)/오류 임계값을 직접 설정합니다.

   두 경우 모두: 안전 모드를 켜 두거나 알고서 끄고, 레벨이 요구하면 사전 점검을 한 뒤 테스트를 실행합니다.
3. 결과는 기록을 거치지 않고 바로 표시됩니다(판정, 지표, 타임라인) — 이 화면에서 바로 내보낼 수 있습니다.
4. 프로필을 고정해 두면 프로필 화면에서, 또는 기록에서 다시 실행해 같은 테스트를 나중에 똑같이 실행할 수 있습니다.

### 테스트 값

8단계 강도는 세 가지 테스트 계열에서 동일합니다(통제하는 차원만 다름) — 전체 표:

| 테스트 종류 | 레벨 | 통제하는 차원 | 목표 값 | 사전 점검 | 사용 가능한 시간(수동 모드) |
|---|---|---|---|---|---|
| 요청 테스트 | 미약 | 처리량 | 250 req/분 (≈4.2 req/초) | 아니요 | 1~5분 |
| 요청 테스트 | 낮음 | 처리량 | 500 req/분 (≈8.3 req/초) | 아니요 | 1~5분 |
| 요청 테스트 | 중간 | 처리량 | 1000 req/분 (≈16.7 req/초) | 아니요 | 1~5분 |
| 요청 테스트 | 높음 | 처리량 | 2000 req/분 (≈33.3 req/초) | 아니요 | 1~5분 |
| 요청 테스트 | 강력 | 처리량 | 6000 req/분 (≈100 req/초) | 선택 | 1~3분 (사전 점검 통과 시 5분) |
| 요청 테스트 | 공격적 | 처리량 | 10,000 req/분 (≈167 req/초) | 선택 | 1~3분 (사전 점검 통과 시 5분) |
| 요청 테스트 | 격렬 | 처리량 | 15,000 req/분 (≈250 req/초) | **필수** | 1~3분만 |
| 요청 테스트 | 최대 | 처리량 | 20,000 req/분 (≈333 req/초) | **필수** | 1~3분만 |
| 연결 테스트 | 미약 | 동시 연결 | 연결 25개 | 아니요 | 1~5분 |
| 연결 테스트 | 낮음 | 동시 연결 | 연결 50개 | 아니요 | 1~5분 |
| 연결 테스트 | 중간 | 동시 연결 | 연결 100개 | 아니요 | 1~5분 |
| 연결 테스트 | 높음 | 동시 연결 | 연결 200개 | 아니요 | 1~5분 |
| 연결 테스트 | 강력 | 동시 연결 | 연결 1000개 | 선택 | 1~3분 (사전 점검 통과 시 5분) |
| 연결 테스트 | 공격적 | 동시 연결 | 연결 2000개 | 선택 | 1~3분 (사전 점검 통과 시 5분) |
| 연결 테스트 | 격렬 | 동시 연결 | 연결 3500개 | **필수** | 1~3분만 |
| 연결 테스트 | 최대 | 동시 연결 | 연결 5000개 | **필수** | 1~3분만 |
| 부하 테스트(점진적 증가) | 미약 | 처리량, 점진적 상승 | 최고 250 req/분 | 아니요 | 1~5분 |
| 부하 테스트(점진적 증가) | 낮음 | 처리량, 점진적 상승 | 최고 500 req/분 | 아니요 | 1~5분 |
| 부하 테스트(점진적 증가) | 중간 | 처리량, 점진적 상승 | 최고 1000 req/분 | 아니요 | 1~5분 |
| 부하 테스트(점진적 증가) | 높음 | 처리량, 점진적 상승 | 최고 2000 req/분 | 아니요 | 1~5분 |
| 부하 테스트(점진적 증가) | 강력 | 처리량, 점진적 상승 | 최고 6000 req/분 | 선택 | 1~3분 (사전 점검 통과 시 5분) |
| 부하 테스트(점진적 증가) | 공격적 | 처리량, 점진적 상승 | 최고 10,000 req/분 | 선택 | 1~3분 (사전 점검 통과 시 5분) |
| 부하 테스트(점진적 증가) | 격렬 | 처리량, 점진적 상승 | 최고 15,000 req/분 | **필수** | 1~3분만 |
| 부하 테스트(점진적 증가) | 최대 | 처리량, 점진적 상승 | 최고 20,000 req/분 | **필수** | 1~3분만 |

- **사전 점검 아니요**: 테스트가 바로 시작되며 시간 조건이 없습니다.
- **사전 점검 선택**(강력/공격적): 사전 점검 없이도 테스트가 시작되지만(시간 1~3분), 사전 점검을 통과하면 4~5분 시간도 열립니다.
- **사전 점검 필수**(격렬/최대): 통과한 사전 점검이 없으면 테스트가 시작되지 않습니다. 사전 점검을 해도 시간은 3분으로 제한됩니다(여기서 사전 점검은 레벨 사용 여부를 정하는 것이지 시간 연장이 아닙니다).

위의 "사용 가능한 시간" 열은 **수동 모드**만 다룹니다(최대 5분). 그 이상은 [프로필 모드 D1-D6](#시간-프로필-d1-d6-프로필-모드)만이 더 긴 테스트(최대 120분)를 허용합니다 — 그 시간에 어떤 레벨을 쓸 수 있는지는 각 프로필 D1-D6이 직접 정합니다(`free_max_level`/`reinforced_level`, 프로필 전용 표 참조):

| 레벨 | 수동 모드 최대 시간 | 프로필 D1-D6 최대 시간 |
|---|---|---|
| 미약 / 낮음 / 중간 / 높음 | 5분 | 120분(D6, 연결/부하만); 요청은 60분(D5, D6는 이 계열과 호환되지 않음) |
| 강력 | 5분(사전 점검 없이는 3분) | 강화된 확인 시 120분(D6, 연결/부하), 없으면 60분(D5) |
| 공격적 | 5분(사전 점검 없이는 3분) | 강화된 확인 시 60분(D5), 없으면 30분(D4) |
| 격렬 | 3분(사전 점검 필수) | 강화된 확인 시 30분(D4), 없으면 15분(D3) |
| 최대 | 3분(사전 점검 필수) | 최대 5분(D1/D2만 — 확인이 있어도 D3-D6 프로필은 최대를 제공하지 않음) |

같은 표를 앱 안(도움말 → 부하 기준점)에서 바로 볼 수 있으며, 항상 같은 기준 값(`domain/load/presets.py`, `domain/load/policies.py`)에서 생성됩니다 — 손으로 옮겨 적지 않습니다.

> **수동 모드**의 부하 테스트에서는 상승과 유지 구간이 선택한 시간에 맞게 자동으로 조정됩니다(프리셋의 비율 유지): 1분 테스트도 시작 부분만이 아니라 0부터 최고점까지 곡선 전체를 지나갑니다. **프로필 모드 D1-D6**에서는 각 프로필의 워밍업/상승/유지/하강 구분이 같은 보장을 기본으로 제공합니다 — [시간 프로필 D1-D6](#시간-프로필-d1-d6-프로필-모드) 참조.

### 탐색

- 위/아래 화살표: 커서 이동.
- `Tab` / `Shift+Tab`: 양식 입력란 사이 이동.
- `Esc`: 뒤로(메인 화면에서는 종료 확인).
- `a`: 도움말 표시.
- `t`: 테마 변경.
- `q`: 종료(확인 있음).
- `r`: 화면 새로 고침, 터미널 크기를 바꾼 뒤 유용합니다.
- `Ctrl+P`: 명령 팔레트(테마 변경, 스크린샷, 단축키 도움말).

`t`로 테마를 바꿀 수 있습니다: Omega-Stress는 어느 화면에서든 감지한 터미널의 기능에 맞게 색과 표시의 풍부함을 자동으로 조정합니다. 명령 팔레트(`Ctrl+P` → 테마)에서는 사용 가능한 31개 테마(Omega 10개 + Textual 내장 21개)를 모두 고를 수 있습니다.

### 지원 터미널

가장 풍부한 것부터 가장 단순한 것까지 네 가지 표시 프로필: **전체**, **표준**, **간소**, **흑백**. 적용되는 프로필은 감지한 터미널 종류와 실제 창 크기 중 더 엄격한 쪽입니다(두 상한 중 어느 것보다도 풍부해지지 않음).

| 터미널 | 기본 프로필 |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | 전체 |
| Konsole, GNOME Terminal, Terminator, xfce4-terminal | 표준 |
| urxvt, xterm | 간소 |
| Linux TTY | 흑백 |
| SSH(true color/256색 감지) | 간소 |
| SSH(최소 신호) | 흑백 |
| 알 수 없는 터미널 | 간소(신중한 대체값) |

80열 × 24행 미만이면 메인 화면 전에 경고 화면이 나타납니다(막지는 않음: 앱은 간소 모드로 계속 쓸 수 있습니다). Konsole, GNOME Terminal, Terminator는 호환성을 위해 일반 값으로 두는 `TERM` 대신 각자의 고유 환경 변수(`KONSOLE_VERSION`, `GNOME_TERMINAL_SCREEN`/`GNOME_TERMINAL_SERVICE`, `TERMINATOR_UUID`)로 식별됩니다 — xfce4-terminal은 지금까지 알려진 동등한 표식이 없어, 인식 가능한 `TERM`/`TERM_PROGRAM` 값을 보일 때만 같은 표준 프로필이 되고 그 밖에는 간소가 됩니다.

### 내부 경로와 시스템 경로

기본적으로 Omega-Stress는 실행한 디렉터리를 기준으로 한 자체 `var/` 폴더(설정되어 있으면 `$OMEGA_STRESS_VAR_DIR`)에서 동작합니다:

```text
var/db/app.db           # SQLite 데이터베이스(프로필, 대상, 기록)
var/settings.json       # 저장된 설정(테마, 표시 프로필, 기본 폴더)
var/exports/            # 기본 JSON/CSV/HTML 내보내기
var/screenshots/        # 기본 SVG 스크린샷(명령 팔레트)
var/audit.jsonl         # 감사 로그(실행당 한 줄)
var/app.log             # 애플리케이션 로그
```

절대 시스템 경로(예: `/var/exports/`)는 기본으로 쓰이지 않습니다 — 그래서 앞의 `/`에는 의미가 있습니다: 이 폴더 밖으로 나가는 것은 사용자가 고른 폴더(설정 또는 내보내기 화면)로의 명시적 내보내기뿐입니다.

## 시간 프로필 D1-D6 (프로필 모드)

수동 모드(시간 1~5분, 레벨별 상한)의 대안: **이름 있는 시간 프로필**은 고정 총 시간을 가지며 내부적으로 4단계(워밍업, 상승, 유지, 하강)로 나뉩니다. 모든 실행 화면("시간 모드: 수동 / 프로필 D1-D6" 전환)과 CLI의 `--duration-preset`으로 고를 수 있습니다.

| 프로필 | 총 시간 | 워밍업 | 상승 | 유지 | 하강 | 확인 없는 최대 레벨 | 추가 레벨(강화된 확인) | 호환 계열 |
|---|---|---|---|---|---|---|---|---|
| D1 (quick) | 1분 | 5초 | 10초 | 40초 | 5초 | 최대 | — | 요청, 연결, 부하 |
| D2 (short) | 5분 | 15초 | 30초 | 4분 | 15초 | 최대 | — | 요청, 연결, 부하 |
| D3 (standard) | 15분 | 30초 | 1분 30초 | 12분 30초 | 30초 | 격렬 | — | 요청, 연결, 부하 |
| D4 (resilience) | 30분 | 1분 | 3분 | 25분 | 1분 | 공격적 | 격렬 | 요청, 연결, 부하 |
| D5 (extended) | 60분 | 2분 | 5분 | 51분 | 2분 | 강력 | 공격적 | 요청, 연결, 부하 |
| D6 (soak) | 120분 | 3분 | 10분 | 104분 | 3분 | 높음 | 강력 | 연결, 부하(요청은 불가) |

- "추가" 레벨(D4-D6)은 화면에 표시되는 강화된 확인 문구를 정확히 입력해야만 쓸 수 있습니다 — 단순한 체크박스로는 결코 안 됩니다.
- D6는 요청 테스트를 제외합니다: 처리량 테스트는 총량으로 상한이 정해지며, 시간에 따른 변화를 보는 2시간 프로필에는 의미가 없습니다.
- 같은 표를 앱 안(도움말 → 시간 프로필 D1-D6)에서 볼 수 있습니다.

## 안전 모드

모든 실행 화면에 있는 체크박스(기본으로 체크됨)로, Omega-Stress가 실행되는 머신을 보호하는 장치(로컬 생성기의 CPU/메모리)**만** 켜고 끕니다:

- **이 설정과 상관없이 항상 활성**: **테스트 대상**을 보호하는 임계값(오류율, 지연 시간) — 이를 끄는 것은 제품상 결코 의미가 없으며, 이 체크박스가 다루는 부분이 아닙니다.
- **안전 모드 켜짐(기본)**: 호스트 머신 자체가 힘들어 보이면 테스트가 자동으로 중지됩니다(생성기 CPU와 머신 전체 CPU가 동시에 높을 때이며, 둘 중 하나만으로는 아님 — 한 코어가 평소처럼 포화되는 것만으로는 결코 충분하지 않음).
- **안전 모드 꺼짐**: 이 로컬 보호 장치가 해제됩니다. 이어서 선택한 레벨과 이 머신의 알려진 마지막 보정을 비교하는 안내가 표시됩니다([로컬 보정](#로컬-보정) 참조) — 이 안전 한도를 넘는 것은 여전히 가능하지만, 결과의 신뢰성과 머신의 안정성은 사용자의 책임이 됩니다.

CLI에서도 `--unsafe`로 사용할 수 있습니다(기본은 지정 안 함 = 안전 모드 켜짐).

## 로컬 보정

**이 머신**(테스트 대상이 아님)의 실제 처리 능력을 측정합니다: Omega-Stress에 내장된 로컬 루프백 서버가 실제 테스트와 같은 `httpx`/asyncio 엔진이 생성하는 점점 커지는 부하를 받습니다.

- 7단계, 유휴 상태(시스템 배경 잡음)부터 연결 2000개 / 12,000 req/초까지. 각 단계는 건강 임계값(생성기 CPU와 전체 CPU, 사용 가능한 메모리, 오류율, 달성 처리량)으로 평가됩니다 — 마지막 2단계는 조건부로, 이전 단계가 건강하지 않으면 건너뜁니다.
- 마지막 건강한 단계에서 안전 여유(약 30 % 여유분)와, 도달한 깊이에 따라 높아지는 신뢰도를 갖춘 안전 한도(`VU_safe` / `RPS_safe`)를 도출합니다.
- **V1에서는 측정만**: 결과가 실제 테스트를 제한하도록 자동 적용되지는 않습니다 — 참고용 기준점이며, 특히 [안전 모드](#안전-모드)를 끌 때 유용합니다.
- 머신별로 저장되며(비침습적 지문: OS/아키텍처/코어 수/RAM, 하드웨어 주소는 절대 사용하지 않음), 다시 측정하지 않고 언제든 볼 수 있습니다.

TUI의 **보정** 화면("보정 시작" 버튼, 진행 상황을 초 단위로 표시) 또는 CLI에서 사용할 수 있습니다:

```bash
omega-stress calibrate run     # 새 보정 실행
omega-stress calibrate show    # 새로 실행하지 않고 알려진 마지막 보정 표시
```

## 구성

모든 것은 TUI의 **설정** 화면에서 합니다(손으로 편집할 구성 파일 없음):

- **테마**: Omega 테마 10개 중 하나, 즉시 적용되고 저장됩니다.
- **표시 프로필**: 자동(시작 시 감지) 또는 수동 고정(전체/표준/간소/흑백).
- **기본 내보내기 폴더**: 내보내기 화면의 "대상 위치" 입력란을 미리 채웁니다.
- **기본 스크린샷 폴더**: 팔레트(`Ctrl+P`)의 "스크린샷" 명령이 사용합니다.
- **삭제**: 최근 대상(고정된 것은 절대 포함 안 함), 모든 대상(고정된 것과 그 권한 포함), 또는 전체 기록 — 각각 별도의 확인으로 보호됩니다.

설정은 `var/settings.json`에 저장됩니다. 루트 `var/` 자체도 환경 변수 `OMEGA_STRESS_VAR_DIR`로 옮길 수 있습니다(여러 인스턴스를 분리하거나 테스트할 때 유용).

## 테스트와 품질

```bash
pytest
ruff check .
mypy src
lint-imports   # Dependency Rule 검증(pyproject.toml [tool.importlinter] 참조)
```

테스트 모음에는 570개 이상의 테스트(단위, 통합, TUI, CLI)가 있습니다. Dependency Rule이나 서드파티 기술 격리를 위반하면 `lint-imports`가 CI를 실패시킵니다 — [아키텍처](#아키텍처) 참조.

## 제거

Omega-Stress는 자체 폴더와 선택 사항인 별칭 한 줄 외에는 아무것도 건드리지 않습니다:

```bash
rm -rf ~/omega-stress
sed -i '/alias stress=/d' ~/.bashrc ~/.zshrc
```

`install.sh`는 시스템 패키지, 서비스, `~/omega-stress/` 밖의 파일을 만들지 않습니다 — 추가 제거 작업이 필요 없습니다.

## 알려진 제한 사항

- 부하 생성은 한 대의 머신에서 **같은 프로세스 안**(`httpx`/asyncio)에서 이루어집니다: 분산 도구가 아닙니다 — 실제 상한([테스트 값](#테스트-값) 참조)은 SaaS 부하 테스트 서비스(loader.io 등)보다 훨씬 소박하며, 통제된 제품이라는 입장에 따른 의도적인 선택입니다. 소박한 하드웨어에서는 연결 테스트의 공격적/격렬/최대 레벨이 목표 부하를 모두 보내는 데 선택한 시간보다 눈에 띄게 긴 실제 시간이 걸릴 수 있습니다 — 그때 실제 처리량을 제한하는 것은 대상이 아니라 **이 머신**의 능력입니다. 하드웨어에 맞는 값을 알려면 [로컬 보정](#로컬-보정)을 사용하세요.
- 터미널 종류 자동 감지는 환경 변수에 의존합니다: xfce4-terminal은 지금까지 신뢰할 수 있는 알려진 표식이 없습니다([지원 터미널](#지원-터미널) 참조).
- `plugins/`는 아키텍처가 계획한 확장 지점(내장/외부 플러그인 로딩)이지만 V1에서는 미구현입니다: 뼈대는 있지만 포함된 플러그인은 없습니다.
- `var/`는 프로젝트 폴더를 기준으로 합니다(XDG 아님): 한 사용자의 로컬 사용을 위해 설계되었으며, 같은 머신에서 여러 사용자가 공유하는 용도가 아닙니다.
- **수동 모드**의 부하 테스트(점진적 증가)에는 유지 구간 뒤 하강 단계("cooldown")가 없습니다 — 이는 4단계를 이미 포함하는 [시간 프로필 D1-D6](#시간-프로필-d1-d6-프로필-모드)에서만 쓸 수 있습니다.
- 통과한 사전 점검은 특정 대상에 묶이지 않습니다: 점검한 대상뿐 아니라 이후의 모든 격렬/최대 실행에 24시간 동안 유효합니다.
- [로컬 보정](#로컬-보정)은 측정하지만, 그 안전 한도를 실제 테스트의 제한으로 자동 적용하지는 아직 않습니다 — 의도적으로 분리된 작업이며 아직 시작하지 않았습니다.

## 라이선스

MIT — `LICENSE` 참조.
