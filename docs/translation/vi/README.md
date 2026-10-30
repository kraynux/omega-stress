<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Giấy phép MIT (xem tệp LICENSE) -->
<div align="center">
  <img src="../../assets/omega-stress.png" alt="Omega-Stress" width="384">
</div>

# 🗲 OMEGA-STRESS

**Trạm kiểm thử tải HTTP có kiểm soát**

> Được **kraynux** xây dựng cho **Omega-server** 
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Trang chính thức: [OMEGA-STRESS](https://kraynux.snake-mackarel.ts.net/omega-stress/) &nbsp; Ảnh chụp màn hình: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-stress/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Giao diện và báo cáo xuất có sẵn bằng **17 ngôn ngữ** — xem [Ngôn ngữ giao diện](#ngôn-ngữ-giao-diện).  
**Ngôn ngữ:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)



**Omega-Stress** là một ứng dụng terminal cục bộ (TUI [Textual](https://github.com/Textualize/textual) + CLI viết script được) điều khiển các bài kiểm thử tải HTTP một cách có kiểm soát và dùng lại được: hồ sơ đóng băng, lịch sử, chạy lại, xuất chi tiết (JSON/CSV/HTML), giới hạn an toàn rõ ràng.

Dự án theo các nguyên tắc của **Clean Architecture**, tách bạch rõ giữa miền nghiệp vụ, điều phối, hạ tầng và giao diện người dùng.
---

## Mục lục

- [Giới thiệu](#giới-thiệu)
- [Tính năng](#tính-năng)
- [Kiến trúc](#kiến-trúc)
- [Yêu cầu](#yêu-cầu)
- [Cài đặt](#cài-đặt)
- [Sử dụng](#khởi-chạy)
- [Hồ sơ thời lượng D1-D6](#hồ-sơ-thời-lượng-d1-d6-chế-độ-hồ-sơ)
- [Chế độ an toàn](#chế-độ-an-toàn)
- [Hiệu chuẩn cục bộ](#hiệu-chuẩn-cục-bộ)
- [Cấu hình](#cấu-hình)
- [Kiểm thử và chất lượng](#kiểm-thử-và-chất-lượng)
- [Gỡ cài đặt](#gỡ-cài-đặt)
- [Giới hạn đã biết](#giới-hạn-đã-biết)
- [Giấy phép](#giấy-phép)

## Giới thiệu

### Mục tiêu

## Omega-Stress làm gì (mục tiêu V1)

- Ba nhóm kiểm thử có kiểm soát: **Kiểm thử yêu cầu** (thông lượng), **Kiểm thử kết nối** (đồng thời), **Kiểm thử tải** (tăng dần).
- **8 mức cường độ** (Yếu/Thấp/Trung bình/Cao/Mạnh/Hung hãn/Dữ dội/Tối đa), với mô hình kiểm tra trước gồm 3 bậc (không bao giờ yêu cầu / yêu cầu tùy chọn / yêu cầu bắt buộc — xem [Giá trị kiểm thử](#giá-trị-kiểm-thử)).
- **Hai chế độ thời lượng**: thủ công (1 đến 5 phút, giới hạn theo mức) hoặc **hồ sơ có tên D1-D6** (tổng thời lượng cố định với khởi động/tăng dần/ổn định/hạ nhiệt — xem [Hồ sơ thời lượng D1-D6](#hồ-sơ-thời-lượng-d1-d6-chế-độ-hồ-sơ)).
- **Chế độ an toàn** (bật mặc định, có thể tắt ở mỗi lần chạy): các giới hạn CPU/bộ nhớ cục bộ của máy chủ chạy công cụ, tách biệt với các ngưỡng bảo vệ mục tiêu được kiểm thử — xem [Chế độ an toàn](#chế-độ-an-toàn).
- **Hiệu chuẩn cục bộ được lưu lại**: đo năng lực thực của máy chạy công cụ (không bao giờ là của mục tiêu) qua một máy chủ vòng lặp cục bộ, theo các bậc tải tăng dần — xem [Hiệu chuẩn cục bộ](#hiệu-chuẩn-cục-bộ).
- Hồ sơ đóng băng, dùng lại được, được ghi vào lịch sử — **tùy chọn**: một bài kiểm thử vẫn chạy tốt ở chế độ thủ công, hoàn toàn không cần hồ sơ, bằng cách chọn hoặc nhập trực tiếp một mục tiêu.
- Bắt buộc xác nhận cấp phép rõ ràng trước mọi lần chạy trên một mục tiêu chưa được ghim.
- Ngưỡng dừng tự động, không bao giờ có tải không giới hạn.
- Xuất JSON/CSV/HTML chi tiết (các bậc, chỉ số theo khoảng, kết luận, chẩn đoán).
- Chế độ CLI không tương tác cho tự động hóa (cron, CI), gọi đúng những ca sử dụng giống TUI.
- Tự động thích ứng với terminal (giao diện màu + hồ sơ hiển thị có thể giản lược).

## Những gì dự án không làm

- Nó không thay thế công cụ quét mạng — từ ngữ và định vị sản phẩm được chủ ý là “kiểm thử tải”, không bao giờ là “quét”.
- Nó không triển khai bất kỳ động cơ tải bên ngoài nào (k6, v.v.) — tạo tải gốc bằng `httpx`/asyncio.
- Nó không bao giờ khởi chạy khi chưa có giới hạn và chưa có xác nhận cấp phép.
- Nó không phải công cụ tải phân tán: việc tạo tải chạy trên một máy, trong một tiến trình — xem [Giới hạn đã biết](#giới-hạn-đã-biết).

## Tính năng

- **Ba nhóm kiểm thử**, mỗi nhóm có 8 mức cường độ (Yếu/Thấp/Trung bình/Cao/Mạnh/Hung hãn/Dữ dội/Tối đa) — xem bảng [Mốc tải](#giá-trị-kiểm-thử) để biết giá trị chính xác của từng mức.
- **Hồ sơ kiểm thử đóng băng**: tên, mục tiêu, nhóm, cường độ, thời lượng, ngưỡng lỗi — tạo một lần, chạy lại y hệt từ TUI hoặc CLI.
- **Hồ sơ thời lượng có tên D1-D6** (chế độ “hồ sơ”), một lựa chọn thay cho chế độ thủ công: tổng thời lượng cố định (1 đến 120 phút) với khởi động/tăng dần/ổn định/hạ nhiệt, đồng thời giới hạn các mức được phép dùng — xem [Hồ sơ thời lượng D1-D6](#hồ-sơ-thời-lượng-d1-d6-chế-độ-hồ-sơ).
- **Chế độ an toàn**, được đánh dấu mặc định trên mỗi màn hình khởi chạy: dừng bài kiểm thử nếu máy chạy công cụ (không phải mục tiêu) có vẻ gặp nguy hiểm. Có thể tắt khi đã hiểu rõ, kèm lời nhắc so sánh mức đã chọn với lần hiệu chuẩn gần nhất — xem [Chế độ an toàn](#chế-độ-an-toàn).
- **Hiệu chuẩn cục bộ được lưu lại**: đo xem máy thực sự chịu được bao nhiêu (7 bậc tải tăng dần đối với một máy chủ vòng lặp cục bộ tích hợp), xem được từ màn hình Hiệu chuẩn — xem [Hiệu chuẩn cục bộ](#hiệu-chuẩn-cục-bộ).
- **Mục tiêu đã ghim**: một địa chỉ đã ghim không cần đánh dấu lại cấp phép ở mỗi lần chạy; các mục tiêu gần đây chưa ghim vẫn hiển thị (tối đa 10) mà không được ngầm cấp phép. Một mục tiêu đã ghim dùng được theo hai cách độc lập: trực tiếp, để khởi chạy bài kiểm thử ở chế độ thủ công không cần hồ sơ, hoặc làm mục tiêu mặc định khi tạo một hồ sơ đóng băng.
- **Lịch sử đầy đủ**: mỗi lần chạy đều được ghi lại (kết luận, chỉ số, diễn biến theo khoảng, chế độ an toàn đã dùng); một lần chạy gắn với hồ sơ đóng băng có thể được chạy lại y hệt.
- **Xuất chi tiết** dạng JSON (dữ liệu thô nhập lại được), CSV (phân tích dạng bảng) hoặc HTML (báo cáo dễ đọc, với giao diện màu chọn trong 10 bảng màu của dự án). Báo cáo HTML được viết bằng ngôn ngữ chọn trong Thiết lập (“Ngôn ngữ bản xuất”, mặc định là ngôn ngữ giao diện); JSON và CSV vẫn là dữ liệu, không được dịch.
- **Kiểm tra trước** tự động và bắt buộc trước mọi bài kiểm thử Dữ dội/Tối đa, tùy chọn (nhưng mở khóa thêm thời lượng) ở mức Mạnh/Hung hãn, có thời hạn hiệu lực (24 giờ).
- **Theo dõi trực tiếp** một bài kiểm thử đang chạy: thanh tiến trình có đếm ngược đáng tin cậy (thời gian còn lại được tính trực tiếp, không bao giờ ước lượng), thông lượng/lỗi/độ trễ p95 được cập nhật ở mỗi khoảng, có thể dừng thủ công mà không phải thoát ứng dụng.
- **Thiết lập tập trung**: giao diện màu (10 bảng màu Omega + mọi giao diện tích hợp của Textual, tổng cộng 31 qua bảng lệnh), hồ sơ hiển thị (tự động hoặc ép buộc), thư mục xuất và thư mục chụp màn hình, xóa mục tiêu/lịch sử.
- **Trợ giúp tích hợp** (phím `a`): phím tắt, mô tả từng màn hình (kể cả Hiệu chuẩn và Chế độ an toàn), bảng tham chiếu giá trị tải và bảng các hồ sơ thời lượng D1-D6.
- **CLI viết script được** (`omega-stress profile|run|history|export|calibrate ...`), đúng những ca sử dụng của TUI, có đầu ra `--json` cho tự động hóa.
- **Tự động thích ứng với terminal**: nhận diện loại và kích thước terminal khi khởi động, điều chỉnh giao diện màu và mức phong phú hiển thị tương ứng (xem [Terminal được hỗ trợ](#terminal-được-hỗ-trợ)).

## Kiến trúc

Clean Architecture + Ports & Adapters trong 9 gói (`app/`, `core/`, `domain/`, `application/`, `ports/`, `infrastructure/`, `interfaces/`, `plugins/`, `shared/`).
Chi tiết đầy đủ: `ARCHITECTURE.md`.

```text
src/omega_stress/
├── app/              Khởi động và bộ chứa tiêm phụ thuộc (đấu nối thủ công, không dùng framework DI)
├── core/             Từ vựng dùng chung: kiểu liệt kê, ngoại lệ gốc, Result/Ok/Err, năng lực hệ thống
├── domain/           Logic nghiệp vụ thuần: tải, hồ sơ, lần chạy, mục tiêu, giao diện màu, terminal — không I/O
├── application/      Điều phối: commands (hành động), queries (đọc), pipeline thực thi (guards/hooks)
├── ports/            Hợp đồng Protocol/ABC mà các bộ chuyển đổi cần (kho lưu trữ, bộ xuất, bộ tạo tải...)
├── infrastructure/   Triển khai cụ thể: SQLite, bộ xuất JSON/CSV/HTML, bộ tạo httpx/asyncio, nhận diện terminal, đầu dò hệ thống
├── interfaces/       Hai bộ chuyển đổi trình bày độc lập: TUI (Textual) và CLI (argparse)
├── plugins/          Điểm mở rộng dành sẵn (nạp plugin) — đã có khung, chưa triển khai ở V1
└── shared/           Tiện ích dùng chung không phụ thuộc nghiệp vụ (đồng hồ có thể tiêm, tạo mã định danh)
```

### Nguyên tắc thiết kế

- `domain/` không chứa I/O cũng không phụ thuộc vào hạ tầng — logic nghiệp vụ thuần, kiểm thử được hoàn toàn mà không cần mock.
- `application/` điều phối các ca sử dụng qua domain và các cổng, không bao giờ dùng trực tiếp một lớp cụ thể trong `infrastructure/`.
- `infrastructure/` triển khai các cổng mà không bao giờ bị `application/` hay `domain/` nhập trực tiếp — chỉ `interfaces/` và `app/` tham chiếu tới nó.
- `interfaces/` không bao giờ được gọi trực tiếp `infrastructure/` hay `subprocess`: chỉ qua `application/` (commands/queries) và các controller riêng của nó.
- `ports/` định nghĩa các hợp đồng mà bộ chuyển đổi cần (Protocol), không bao giờ là phần triển khai.
- `core/` gom từ vựng chung của mọi tầng, không bao giờ đưa vào đó quy tắc nghiệp vụ có con số (ngưỡng, thời lượng, preset — luôn nằm trong `domain/*/policies.py`).

Dependency Rule (chỉ từ tầng ngoài vào tầng trong) và việc cô lập công nghệ bên thứ ba (`textual`, `sqlite3`, `httpx`, `jinja2`, mỗi thứ chỉ ở điểm vào đã định) được kiểm tra tự động mỗi lần chạy `lint-imports` (xem [Kiểm thử và chất lượng](#kiểm-thử-và-chất-lượng)).

## Yêu cầu

- Python ≥ 3.10
- Khuyên dùng [`uv`](https://github.com/astral-sh/uv) để quản lý phụ thuộc (nếu không thì `pip` tiêu chuẩn)

### Hệ thống

- Linux, ưu tiên Arch Linux và các bản phân phối tương thích.
- Python 3.10 trở lên.
- Không cần quyền root: Omega-Stress chỉ thực hiện các lệnh gọi HTTP đi ra với tư cách người dùng thường.

## Cài đặt

Bản lưu trữ chính thức được cung cấp ở định dạng `.tar.gz`. Hãy kiểm tra tính toàn vẹn trước khi cài đặt:

```bash
sha256sum omega-stress.tar.gz
```

### Cách 1 — script cài đặt

```bash
[ -d omega-stress ] && echo "ℹ️ Đã giải nén ở đây, bỏ qua bước này." || tar -xzf omega-stress.tar.gz
[ -d ~/omega-stress ] && echo "ℹ️ ~/omega-stress đã tồn tại, bỏ qua việc di chuyển." || mv omega-stress ~/
cd ~/omega-stress/
chmod +x install.sh
./install.sh
```

### Cách 2 — cài đặt đầy đủ, bền vững

Lệnh này có thể sao chép và dán nguyên văn, chạy lại mà không lỗi: mỗi bước sẽ bỏ qua những gì đã làm.

```bash
( [ -d omega-stress ] || tar -xzf omega-stress.tar.gz ) && \
( [ -d ~/omega-stress ] || mv omega-stress ~/ ) && \
cd ~/omega-stress && chmod +x install.sh && ./install.sh
```
`install.sh`:

1. Tạo môi trường ảo `.venv` nếu chưa có.
2. Cài các phụ thuộc (`pip install -e .`; `pyproject.toml` vẫn là nguồn chuẩn duy nhất).
3. Cấp quyền thực thi cho `omega-stress.sh` và `install.sh`.
4. Thêm bí danh `stress` vào `~/.bashrc` và `~/.zshrc` (không trùng lặp nếu đã có).

## Cài đặt (phát triển)

```bash
uv sync --all-extras
# hoặc, không dùng uv:
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```


### Khởi chạy

```bash
cd ~/omega-stress
./omega-stress.sh

# hoặc chỉ cần gõ "stress" trong một terminal mới nếu đã tạo bí danh
```

Trình khởi chạy:

1. Nhận diện `.venv`, `venv` hoặc Python của hệ thống.
2. Đặt `PYTHONPATH` trỏ tới `src/`.
3. Chạy `python -m omega_stress` — không có đối số thì mở TUI; có đối số thì chuyển sang CLI.

### Ngôn ngữ giao diện

Giao diện có sẵn bằng 17 ngôn ngữ: tiếng Pháp, tiếng Anh, tiếng Tây Ban Nha, tiếng Bồ Đào Nha (Brasil), tiếng Ý, tiếng Đức, tiếng Hà Lan, tiếng Ba Lan, tiếng Nga, tiếng Trung giản thể, tiếng Việt, tiếng Thái, tiếng Indonesia, tiếng Nhật, tiếng Hàn, tiếng Hindi và tiếng Ả Rập. Ngôn ngữ được chọn trong Thiết lập (“Langue / Language”) và có hiệu lực sau khi khởi động lại giao diện; biến `OMEGA_STRESS_LANG` (ví dụ `OMEGA_STRESS_LANG=vi ./omega-stress.sh`) buộc dùng một ngôn ngữ trong một phiên. Khi được chạy từ omega-suite, omega-stress dùng ngôn ngữ của bộ công cụ. Trên console văn bản Linux (TTY), giao diện hiển thị bằng tiếng Anh trong phiên đó đối với tiếng Việt và các ngôn ngữ không dùng chữ Latinh. Dòng lệnh vẫn bằng tiếng Pháp.

### Dùng CLI

```bash
omega-stress profile list                                     # liệt kê các hồ sơ
omega-stress profile create --name "Thăm dò API" --target-id t-1 \
    --family request --level bas --duration-minutes 1 --max-error-rate 0.05
omega-stress profile freeze <profile-id>                       # đóng băng một hồ sơ

# Bắt buộc kiểm tra trước mọi lần chạy Dữ dội/Tối đa (tùy chọn với Mạnh/Hung hãn)
omega-stress run precheck --target-id t-1 --target-url https://exemple.org --confirm

omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level bas --duration-minutes 1 --max-error-rate 0.05 --confirm
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level moyen --duration-minutes 3 --max-error-rate 0.05 --confirm
omega-stress run ramp --target-id t-1 --target-url https://exemple.org \
    --level puissant --duration-minutes 3 --max-error-rate 0.05 --confirm --precheck-validated

# Chế độ hồ sơ D1-D6, thay cho --duration-minutes (loại trừ lẫn nhau)
# D4 (resilience) cho phép Hung hãn không điều kiện, Dữ dội khi có xác nhận tăng cường
omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-preset d4 --max-error-rate 0.05 --confirm \
    --precheck-validated --confirmation-text JE_CONFIRME_LA_CIBLE_AUTORISEE

# --unsafe tắt chế độ an toàn (giới hạn CPU/bộ nhớ cục bộ); mặc định không có
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-minutes 1 --max-error-rate 0.05 --confirm \
    --precheck-validated --unsafe

omega-stress run replay <run-id> --confirm                     # chạy lại một lần chạy gắn với hồ sơ đóng băng

omega-stress history list                                      # lịch sử các lần chạy
omega-stress history show <run-id>                              # chi tiết một lần chạy

omega-stress export <run-id> --format html --destination var/exports --theme omega-base

omega-stress calibrate run                                      # chạy hiệu chuẩn cho máy này
omega-stress calibrate show                                     # hiện lần hiệu chuẩn gần nhất đã biết
```

Các giá trị của `--level` (`faible`, `bas`, `moyen`, `haut`, `puissant`, `agressif`, `violent`, `maximum`) và văn bản xác nhận vẫn bằng tiếng Pháp, giống phần còn lại của dòng lệnh.

`--confirm` là tương đương trên dòng lệnh của ô cấp phép trong TUI: bắt buộc với mọi mục tiêu chưa được ghim là đã cấp phép. `--target-id`/`--target-url` giống nhau nghĩa là mục tiêu thủ công (chưa ghim); hãy dùng mã định danh của một mục tiêu đã ghim để khỏi phải thêm `--confirm` ở mỗi lần chạy.

Thêm `--json` vào `history`/`export`/`calibrate` để có đầu ra máy đọc được, dùng trong cron/CI.

### Trình tự chung

1. Ở lần khởi chạy đầu tiên, màn hình chính đề xuất: Hồ sơ, Kiểm thử yêu cầu, Kiểm thử kết nối, Kiểm thử tải, Lịch sử, Mục tiêu, Hiệu chuẩn, Thiết lập, Trợ giúp.
2. Từ một màn hình kiểm thử, vẫn có thể chọn một hồ sơ đóng băng (tùy chọn) ở đầu màn hình: hai cách nhập mục tiêu và tiêu chí, không bao giờ kết hợp trong cùng một lần chạy —
   - **có hồ sơ**: chọn nó sẽ điền sẵn mục tiêu/cường độ/thời lượng/ngưỡng lỗi, và trường mục tiêu thủ công biến mất (lúc đó không còn ý nghĩa); các giá trị điền sẵn vẫn sửa được trước khi chạy;
   - **không có hồ sơ (chế độ thủ công)**: chọn một mục tiêu đã ghim/gần đây trong danh sách hoặc nhập mục tiêu mới, đánh dấu cấp phép nếu nó chưa được ghim là đã cấp phép, tự đặt cường độ/thời lượng (thủ công hoặc hồ sơ thời lượng D1-D6)/ngưỡng lỗi.

   Trong cả hai trường hợp: giữ chế độ an toàn bật hoặc tắt nó khi đã hiểu rõ, chạy kiểm tra trước nếu mức yêu cầu, rồi khởi chạy bài kiểm thử.
3. Kết quả hiện ngay (kết luận, chỉ số, diễn biến), không cần quay qua Lịch sử — màn hình này đề xuất xuất trực tiếp.
4. Có thể đóng băng một hồ sơ để sau này chạy lại y hệt cùng bài kiểm thử, từ màn hình Hồ sơ hoặc chạy lại từ Lịch sử.

### Giá trị kiểm thử

8 mức cường độ, giống nhau ở cả ba nhóm kiểm thử (chỉ đại lượng được điều khiển là khác) — bảng đầy đủ:

| Loại kiểm thử | Mức | Đại lượng điều khiển | Giá trị nhắm tới | Kiểm tra trước | Thời lượng có sẵn (chế độ thủ công) |
|---|---|---|---|---|---|
| Kiểm thử yêu cầu | Yếu | Thông lượng | 250 yc/phút (≈4,2 yc/giây) | Không | 1 đến 5 phút |
| Kiểm thử yêu cầu | Thấp | Thông lượng | 500 yc/phút (≈8,3 yc/giây) | Không | 1 đến 5 phút |
| Kiểm thử yêu cầu | Trung bình | Thông lượng | 1000 yc/phút (≈16,7 yc/giây) | Không | 1 đến 5 phút |
| Kiểm thử yêu cầu | Cao | Thông lượng | 2000 yc/phút (≈33,3 yc/giây) | Không | 1 đến 5 phút |
| Kiểm thử yêu cầu | Mạnh | Thông lượng | 6000 yc/phút (≈100 yc/giây) | Tùy chọn | 1 đến 3 phút (5 nếu đã qua kiểm tra trước) |
| Kiểm thử yêu cầu | Hung hãn | Thông lượng | 10.000 yc/phút (≈167 yc/giây) | Tùy chọn | 1 đến 3 phút (5 nếu đã qua kiểm tra trước) |
| Kiểm thử yêu cầu | Dữ dội | Thông lượng | 15.000 yc/phút (≈250 yc/giây) | **Bắt buộc** | Chỉ 1 đến 3 phút |
| Kiểm thử yêu cầu | Tối đa | Thông lượng | 20.000 yc/phút (≈333 yc/giây) | **Bắt buộc** | Chỉ 1 đến 3 phút |
| Kiểm thử kết nối | Yếu | Kết nối đồng thời | 25 kết nối | Không | 1 đến 5 phút |
| Kiểm thử kết nối | Thấp | Kết nối đồng thời | 50 kết nối | Không | 1 đến 5 phút |
| Kiểm thử kết nối | Trung bình | Kết nối đồng thời | 100 kết nối | Không | 1 đến 5 phút |
| Kiểm thử kết nối | Cao | Kết nối đồng thời | 200 kết nối | Không | 1 đến 5 phút |
| Kiểm thử kết nối | Mạnh | Kết nối đồng thời | 1000 kết nối | Tùy chọn | 1 đến 3 phút (5 nếu đã qua kiểm tra trước) |
| Kiểm thử kết nối | Hung hãn | Kết nối đồng thời | 2000 kết nối | Tùy chọn | 1 đến 3 phút (5 nếu đã qua kiểm tra trước) |
| Kiểm thử kết nối | Dữ dội | Kết nối đồng thời | 3500 kết nối | **Bắt buộc** | Chỉ 1 đến 3 phút |
| Kiểm thử kết nối | Tối đa | Kết nối đồng thời | 5000 kết nối | **Bắt buộc** | Chỉ 1 đến 3 phút |
| Kiểm thử tải (tăng dần) | Yếu | Thông lượng, tăng dần | đỉnh 250 yc/phút | Không | 1 đến 5 phút |
| Kiểm thử tải (tăng dần) | Thấp | Thông lượng, tăng dần | đỉnh 500 yc/phút | Không | 1 đến 5 phút |
| Kiểm thử tải (tăng dần) | Trung bình | Thông lượng, tăng dần | đỉnh 1000 yc/phút | Không | 1 đến 5 phút |
| Kiểm thử tải (tăng dần) | Cao | Thông lượng, tăng dần | đỉnh 2000 yc/phút | Không | 1 đến 5 phút |
| Kiểm thử tải (tăng dần) | Mạnh | Thông lượng, tăng dần | đỉnh 6000 yc/phút | Tùy chọn | 1 đến 3 phút (5 nếu đã qua kiểm tra trước) |
| Kiểm thử tải (tăng dần) | Hung hãn | Thông lượng, tăng dần | đỉnh 10.000 yc/phút | Tùy chọn | 1 đến 3 phút (5 nếu đã qua kiểm tra trước) |
| Kiểm thử tải (tăng dần) | Dữ dội | Thông lượng, tăng dần | đỉnh 15.000 yc/phút | **Bắt buộc** | Chỉ 1 đến 3 phút |
| Kiểm thử tải (tăng dần) | Tối đa | Thông lượng, tăng dần | đỉnh 20.000 yc/phút | **Bắt buộc** | Chỉ 1 đến 3 phút |

- **Kiểm tra trước: Không**: bài kiểm thử bắt đầu ngay, không có điều kiện về thời lượng.
- **Kiểm tra trước: Tùy chọn** (Mạnh/Hung hãn): bài kiểm thử bắt đầu mà không cần kiểm tra trước (thời lượng 1-3 phút), nhưng một lần kiểm tra trước đã qua sẽ mở khóa thêm thời lượng 4-5 phút.
- **Kiểm tra trước: Bắt buộc** (Dữ dội/Tối đa): bài kiểm thử không bắt đầu nếu chưa qua kiểm tra trước; thời lượng vẫn bị giới hạn ở 3 phút ngay cả khi đã kiểm tra trước (ở đây kiểm tra trước quyết định quyền dùng mức, không phải thời lượng dài hơn).

Cột “Thời lượng có sẵn” ở trên chỉ áp dụng cho **chế độ thủ công** (tối đa 5 phút). Vượt quá mức đó, chỉ [chế độ hồ sơ D1-D6](#hồ-sơ-thời-lượng-d1-d6-chế-độ-hồ-sơ) mới cho phép bài kiểm thử dài hơn (tới 120 phút) — mỗi hồ sơ D1-D6 tự quyết định những mức nào còn dùng được ở thời lượng đó (`free_max_level`/`reinforced_level`, xem bảng riêng của nó):

| Mức | Thời lượng tối đa ở chế độ thủ công | Thời lượng tối đa qua một hồ sơ D1-D6 |
|---|---|---|
| Yếu / Thấp / Trung bình / Cao | 5 phút | 120 phút (D6, chỉ Kết nối/Tải); 60 phút với Yêu cầu (D5, D6 không tương thích với nhóm này) |
| Mạnh | 5 phút (3 phút nếu không kiểm tra trước) | 120 phút khi có xác nhận tăng cường (D6, Kết nối/Tải) hoặc 60 phút nếu không (D5) |
| Hung hãn | 5 phút (3 phút nếu không kiểm tra trước) | 60 phút khi có xác nhận tăng cường (D5) hoặc 30 phút nếu không (D4) |
| Dữ dội | 3 phút (bắt buộc kiểm tra trước) | 30 phút khi có xác nhận tăng cường (D4) hoặc 15 phút nếu không (D3) |
| Tối đa | 3 phút (bắt buộc kiểm tra trước) | tối đa 5 phút (chỉ D1/D2 — không hồ sơ D3-D6 nào cung cấp mức Tối đa, kể cả khi có xác nhận) |

Bảng này cũng có sẵn ngay trong ứng dụng (Trợ giúp → Mốc tải), luôn được tạo từ cùng các giá trị tham chiếu (`domain/load/presets.py`, `domain/load/policies.py`) — không bao giờ sao chép bằng tay.

> Với Kiểm thử tải ở **chế độ thủ công**, phần tăng dần và phần ổn định được tự động co giãn theo thời lượng đã chọn (giữ tỉ lệ của preset): một bài kiểm thử 1 phút vẫn đi hết đường cong, từ 0 tới đỉnh, chứ không chỉ phần đầu. Ở **chế độ hồ sơ D1-D6**, cách chia khởi động/tăng dần/ổn định/hạ nhiệt của mỗi hồ sơ đã bảo đảm điều tương tự — xem [Hồ sơ thời lượng D1-D6](#hồ-sơ-thời-lượng-d1-d6-chế-độ-hồ-sơ).

### Điều hướng

- Mũi tên lên/xuống: di chuyển con trỏ.
- `Tab` / `Shift+Tab`: di chuyển giữa các trường của biểu mẫu.
- `Esc`: quay lại (xác nhận thoát từ màn hình chính).
- `a`: hiện trợ giúp.
- `t`: đổi giao diện màu.
- `q`: thoát (có xác nhận).
- `r`: làm mới hiển thị, hữu ích sau khi đổi kích thước terminal.
- `Ctrl+P`: bảng lệnh (đổi giao diện màu, chụp màn hình, trợ giúp phím tắt).

Chuyển giao diện màu bằng `t`: Omega-Stress tự động điều chỉnh màu sắc và mức phong phú hiển thị theo năng lực terminal đã nhận diện, ở bất kỳ màn hình nào. Từ bảng lệnh (`Ctrl+P` → Giao diện), cả 31 giao diện màu đều được đề xuất (10 giao diện Omega + 21 giao diện tích hợp của Textual).

### Terminal được hỗ trợ

Bốn hồ sơ hiển thị, từ phong phú nhất đến giản lược nhất: **Đầy đủ**, **Tiêu chuẩn**, **Giản lược**, **Đơn sắc**. Hồ sơ được chọn là hồ sơ hạn chế hơn giữa loại terminal nhận diện được và kích thước thực của cửa sổ (không bao giờ phong phú hơn bất kỳ mức trần nào trong hai).

| Terminal | Hồ sơ mặc định |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | Đầy đủ |
| Konsole, GNOME Terminal, Terminator, xfce4-terminal | Tiêu chuẩn |
| urxvt, xterm | Giản lược |
| TTY Linux | Đơn sắc |
| SSH (nhận diện được màu thật/256 màu) | Giản lược |
| SSH (tín hiệu tối thiểu) | Đơn sắc |
| Terminal không nhận diện được | Giản lược (dự phòng thận trọng) |

Dưới 80 cột × 24 dòng, một màn hình cảnh báo hiện ra trước màn hình chính (không bao giờ chặn: ứng dụng vẫn dùng được ở chế độ giản lược). Konsole, GNOME Terminal và Terminator được nhận diện qua biến môi trường đặc trưng riêng (`KONSOLE_VERSION`, `GNOME_TERMINAL_SCREEN`/`GNOME_TERMINAL_SERVICE`, `TERMINATOR_UUID`) thay vì `TERM`, vốn được chúng để ở giá trị tương thích chung — xfce4-terminal tới nay chưa đặt dấu hiệu tương đương nào được biết, nên chỉ rơi vào cùng hồ sơ Tiêu chuẩn đó nếu nó cung cấp giá trị `TERM`/`TERM_PROGRAM` nhận diện được, nếu không thì Giản lược.

### Đường dẫn nội bộ và đường dẫn hệ thống

Mặc định, Omega-Stress làm việc trong thư mục `var/` riêng của nó, tương đối với thư mục khởi chạy (hoặc `$OMEGA_STRESS_VAR_DIR` nếu được đặt):

```text
var/db/app.db           # cơ sở dữ liệu SQLite (hồ sơ, mục tiêu, lịch sử)
var/settings.json       # thiết lập đã lưu (giao diện màu, hồ sơ hiển thị, thư mục mặc định)
var/exports/            # bản xuất JSON/CSV/HTML mặc định
var/screenshots/        # ảnh chụp màn hình SVG mặc định (bảng lệnh)
var/audit.jsonl         # nhật ký kiểm tra (mỗi lần chạy một dòng)
var/app.log             # nhật ký ứng dụng
```

Đường dẫn hệ thống tuyệt đối (ví dụ `/var/exports/`) không bao giờ được dùng mặc định — vì vậy dấu `/` ở đầu là có ý nghĩa: chỉ một lần xuất rõ ràng tới thư mục do người dùng chọn (Thiết lập hoặc màn hình Xuất) mới ra khỏi thư mục này.

## Hồ sơ thời lượng D1-D6 (chế độ hồ sơ)

Lựa chọn thay cho chế độ thủ công (thời lượng 1-5 phút, giới hạn theo mức): một **hồ sơ thời lượng có tên**, với tổng thời lượng cố định và chia nội bộ thành 4 giai đoạn (khởi động, tăng dần, ổn định, hạ nhiệt). Chọn được trên mỗi màn hình khởi chạy (công tắc “Chế độ thời lượng: Thủ công / Hồ sơ D1-D6”) và trong CLI qua `--duration-preset`.

| Hồ sơ | Tổng thời lượng | Khởi động | Tăng dần | Ổn định | Hạ nhiệt | Mức tối đa không cần xác nhận | Mức bổ sung (xác nhận tăng cường) | Nhóm tương thích |
|---|---|---|---|---|---|---|---|---|
| D1 (quick) | 1 phút | 5 giây | 10 giây | 40 giây | 5 giây | Tối đa | — | Yêu cầu, Kết nối, Tải |
| D2 (short) | 5 phút | 15 giây | 30 giây | 4 phút | 15 giây | Tối đa | — | Yêu cầu, Kết nối, Tải |
| D3 (standard) | 15 phút | 30 giây | 1 phút 30 | 12 phút 30 | 30 giây | Dữ dội | — | Yêu cầu, Kết nối, Tải |
| D4 (resilience) | 30 phút | 1 phút | 3 phút | 25 phút | 1 phút | Hung hãn | Dữ dội | Yêu cầu, Kết nối, Tải |
| D5 (extended) | 60 phút | 2 phút | 5 phút | 51 phút | 2 phút | Mạnh | Hung hãn | Yêu cầu, Kết nối, Tải |
| D6 (soak) | 120 phút | 3 phút | 10 phút | 104 phút | 3 phút | Cao | Mạnh | Kết nối, Tải (không bao giờ Yêu cầu) |

- Mức “bổ sung” (D4-D6) chỉ dùng được khi gõ chính xác văn bản xác nhận tăng cường hiển thị trên màn hình — không bao giờ chỉ là một ô đánh dấu.
- D6 loại trừ Kiểm thử yêu cầu: một bài kiểm thử thông lượng bị giới hạn theo khối lượng, điều không bao giờ phù hợp với một hồ sơ 2 giờ nhằm theo dõi sự trôi dạt theo thời gian.
- Bảng này cũng có trong ứng dụng (Trợ giúp → Hồ sơ thời lượng D1-D6).

## Chế độ an toàn

Một ô đánh dấu có trên mỗi màn hình khởi chạy (đánh dấu mặc định), chỉ bật/tắt **duy nhất** các giới hạn bảo vệ chiếc máy đang chạy Omega-Stress (CPU/bộ nhớ của bộ tạo tải cục bộ):

- **Luôn bật, bất kể thiết lập này**: các ngưỡng bảo vệ **mục tiêu được kiểm thử** (tỉ lệ lỗi, độ trễ) — tắt chúng không bao giờ có ý nghĩa với sản phẩm; ô này không phụ trách chúng.
- **Chế độ an toàn bật (mặc định)**: bài kiểm thử tự động dừng nếu chính máy chạy công cụ có vẻ quá tải (CPU của bộ tạo tải VÀ CPU tổng của máy cùng cao một lúc, không phải chỉ một trong hai — việc một nhân bão hòa bình thường không bao giờ tự nó là đủ).
- **Chế độ an toàn tắt**: giới hạn cục bộ này được gỡ bỏ. Khi đó sẽ hiện lời nhắc so sánh mức đã chọn với lần hiệu chuẩn gần nhất đã biết của máy này (xem [Hiệu chuẩn cục bộ](#hiệu-chuẩn-cục-bộ)) — vẫn có thể vượt ngưỡng an toàn đó, nhưng độ tin cậy của kết quả và sự ổn định của máy trở thành trách nhiệm của người dùng.

Cũng có trong CLI qua `--unsafe` (mặc định không có = chế độ an toàn bật).

## Hiệu chuẩn cục bộ

Đo năng lực thực của **máy này** (không bao giờ là của mục tiêu được kiểm thử): một máy chủ vòng lặp cục bộ tích hợp trong Omega-Stress nhận tải tăng dần theo bậc, do cùng động cơ `httpx`/asyncio như các bài kiểm thử thật tạo ra.

- 7 bậc, từ nghỉ (nhiễu nền của hệ thống) tới 2000 kết nối / 12.000 yc/giây, mỗi bậc được đánh giá theo ngưỡng sức khỏe (CPU của bộ tạo tải VÀ tổng, bộ nhớ còn trống, tỉ lệ lỗi, thông lượng đạt được) — 2 bậc cuối có điều kiện, bị bỏ qua nếu bậc trước không ổn.
- Tạo ra một ngưỡng an toàn (`VU_safe` / `RPS_safe`) từ bậc ổn cuối cùng, kèm biên an toàn (~30 % dự phòng) và mức độ tin cậy tăng theo độ sâu đạt được.
- **V1 chỉ đo**: kết quả không được tự động áp dụng để giới hạn một bài kiểm thử thật — nó là mốc tham khảo, nhất là khi [Chế độ an toàn](#chế-độ-an-toàn) đã tắt.
- Được lưu theo từng máy (dấu vân tay không xâm phạm: hệ điều hành/kiến trúc/số nhân/RAM, không bao giờ là địa chỉ phần cứng), xem được bất cứ lúc nào mà không cần đo lại.

Truy cập từ màn hình **Hiệu chuẩn** của TUI (nút “Bắt đầu hiệu chuẩn”, tiến trình hiển thị từng giây), hoặc trong CLI:

```bash
omega-stress calibrate run     # chạy một lần hiệu chuẩn mới
omega-stress calibrate show    # hiện lần hiệu chuẩn gần nhất đã biết, không chạy lại
```

## Cấu hình

Mọi thứ được chỉnh từ màn hình **Thiết lập** của TUI (không có tệp cấu hình nào phải sửa tay):

- **Giao diện màu**: một trong 10 giao diện Omega, áp dụng ngay và được lưu.
- **Hồ sơ hiển thị**: Tự động (nhận diện khi khởi động) hoặc ép thủ công (Đầy đủ/Tiêu chuẩn/Giản lược/Đơn sắc).
- **Thư mục xuất mặc định**: điền sẵn trường “đích” của màn hình Xuất.
- **Thư mục chụp màn hình mặc định**: được lệnh “Chụp màn hình” của bảng lệnh dùng (`Ctrl+P`).
- **Dọn dẹp**: mục tiêu gần đây (không bao giờ là mục tiêu đã ghim), mọi mục tiêu (kể cả đã ghim và quyền cấp phép của chúng) hoặc toàn bộ lịch sử — mỗi thao tác được bảo vệ bởi một xác nhận riêng.

Thiết lập được lưu trong `var/settings.json`. Bản thân thư mục gốc `var/` có thể được chuyển hướng bằng biến môi trường `OMEGA_STRESS_VAR_DIR` (hữu ích để tách biệt nhiều phiên bản chạy song song, hoặc cho kiểm thử).

## Kiểm thử và chất lượng

```bash
pytest
ruff check .
mypy src
lint-imports   # kiểm tra Dependency Rule (xem pyproject.toml [tool.importlinter])
```

Bộ kiểm thử có hơn 570 bài (đơn vị, tích hợp, TUI, CLI). `lint-imports` làm CI thất bại nếu Dependency Rule hoặc việc cô lập công nghệ bên thứ ba bị vi phạm — xem [Kiến trúc](#kiến-trúc).

## Gỡ cài đặt

Omega-Stress không đụng tới thứ gì ngoài thư mục riêng của nó và một dòng bí danh tùy chọn:

```bash
rm -rf ~/omega-stress
sed -i '/alias stress=/d' ~/.bashrc ~/.zshrc
```

`install.sh` không tạo gói hệ thống, dịch vụ hay tệp nào bên ngoài `~/omega-stress/` — không cần gỡ cài đặt gì thêm.

## Giới hạn đã biết

- Tạo tải **ngay trong tiến trình**, trên một máy (`httpx`/asyncio): đây không phải công cụ phân tán — các mức trần thực tế (xem [Giá trị kiểm thử](#giá-trị-kiểm-thử)) thấp hơn rõ rệt so với một dịch vụ kiểm thử tải SaaS (loader.io, v.v.), một cách có chủ ý, theo định vị sản phẩm có kiểm soát. Trên phần cứng khiêm tốn, các mức Hung hãn/Dữ dội/Tối đa của Kiểm thử kết nối có thể mất nhiều thời gian thực hơn hẳn thời lượng đã chọn để phát đủ toàn bộ tải nhắm tới — khi đó năng lực của **máy này**, chứ không phải của mục tiêu, mới giới hạn thông lượng thực; hãy dùng [Hiệu chuẩn cục bộ](#hiệu-chuẩn-cục-bộ) để biết các giá trị hợp lý cho phần cứng của bạn.
- Việc tự động nhận diện loại terminal dựa vào biến môi trường: xfce4-terminal tới nay chưa có dấu hiệu đáng tin cậy nào được biết (xem [Terminal được hỗ trợ](#terminal-được-hỗ-trợ)).
- `plugins/` là điểm mở rộng mà kiến trúc dự liệu (nạp plugin tích hợp/bên ngoài), chưa triển khai ở V1: khung đã có, chưa có plugin nào được phát hành.
- `var/` tương đối với thư mục dự án (không theo XDG): được thiết kế cho một người dùng dùng cục bộ, không cho nhiều người dùng chia sẻ trên cùng một máy.
- Kiểm thử tải (tăng dần) ở **chế độ thủ công** không có bậc hạ tải (“cooldown”) sau giai đoạn ổn định — chỉ có qua một [hồ sơ thời lượng D1-D6](#hồ-sơ-thời-lượng-d1-d6-chế-độ-hồ-sơ), vốn đã gồm đủ 4 giai đoạn.
- Một lần kiểm tra trước đã qua không gắn với một mục tiêu cụ thể: nó có hiệu lực 24 giờ cho mọi lần chạy Dữ dội/Tối đa tiếp theo, không chỉ trên mục tiêu đã được kiểm tra.
- [Hiệu chuẩn cục bộ](#hiệu-chuẩn-cục-bộ) có đo, nhưng chưa tự động áp dụng ngưỡng an toàn của nó để giới hạn một bài kiểm thử thật — một hạng mục được chủ ý tách riêng, chưa bắt đầu.

## Giấy phép

MIT — xem `LICENSE`.
