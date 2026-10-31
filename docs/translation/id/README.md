<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Lisensi MIT (lihat berkas LICENSE) -->
<div align="center">
  <img src="../../assets/omega-stress.png" alt="Omega-Stress" width="384">
</div>

# 🗲 OMEGA-STRESS

**Stasiun uji beban HTTP yang terkendali**

> Dibuat oleh [kraynux](https://github.com/kraynux) untuk [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Halaman resmi: [OMEGA-STRESS](https://kraynux.snake-mackarel.ts.net/omega-stress/) &nbsp; Pratinjau: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-stress/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Antarmuka dan laporan ekspor tersedia dalam **17 bahasa** — lihat [Bahasa antarmuka](#bahasa-antarmuka).  
**Bahasa:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)



**Omega-Stress** adalah aplikasi terminal lokal (TUI [Textual](https://github.com/Textualize/textual) + CLI untuk skrip) yang menjalankan uji beban HTTP secara terkendali dan dapat dipakai ulang: profil yang dibekukan, riwayat, menjalankan ulang, ekspor terperinci (JSON/CSV/HTML), batas keamanan yang tegas.

Proyek ini mengikuti prinsip **Clean Architecture**, dengan pemisahan jelas antara domain bisnis, orkestrasi, infrastruktur, dan antarmuka pengguna.
---

## Daftar isi

- [Gambaran umum](#gambaran-umum)
- [Fitur](#fitur)
- [Arsitektur](#arsitektur)
- [Prasyarat](#prasyarat)
- [Instalasi](#instalasi)
- [Penggunaan](#menjalankan)
- [Profil durasi D1-D6](#profil-durasi-d1-d6-mode-profil)
- [Mode keamanan](#mode-keamanan)
- [Kalibrasi lokal](#kalibrasi-lokal)
- [Konfigurasi](#konfigurasi)
- [Pengujian dan kualitas](#pengujian-dan-kualitas)
- [Penghapusan instalasi](#penghapusan-instalasi)
- [Keterbatasan yang diketahui](#keterbatasan-yang-diketahui)
- [Lisensi](#lisensi)

## Gambaran umum

### Tujuan

## Yang dilakukan Omega-Stress (target V1)

- Tiga keluarga uji yang terkendali: **Uji permintaan** (laju), **Uji koneksi** (keserentakan), **Uji beban** (kenaikan bertahap).
- **8 level intensitas** (Lemah/Rendah/Sedang/Tinggi/Kuat/Agresif/Brutal/Maksimum), dengan model pra-pemeriksaan 3 tingkat (tidak pernah diwajibkan / diwajibkan opsional / diwajibkan mutlak — lihat [Nilai pengujian](#nilai-pengujian)).
- **Dua mode durasi**: manual (1 hingga 5 menit, dibatasi per level) atau **profil bernama D1-D6** (durasi total tetap dengan pemanasan/kenaikan/dataran/pendinginan — lihat [Profil durasi D1-D6](#profil-durasi-d1-d6-mode-profil)).
- **Mode keamanan** (aktif secara bawaan, dapat dimatikan pada setiap peluncuran): pengaman CPU/memori lokal untuk mesin host, terpisah dari ambang yang melindungi target yang diuji — lihat [Mode keamanan](#mode-keamanan).
- **Kalibrasi lokal yang tersimpan**: mengukur kapasitas nyata mesin host (bukan target) melalui server loopback lokal, dalam tahap beban yang meningkat — lihat [Kalibrasi lokal](#kalibrasi-lokal).
- Profil yang dibekukan, dapat dipakai ulang, dan tercatat di riwayat — **opsional**: sebuah uji tetap berjalan baik dalam mode manual, tanpa profil sama sekali, dengan memilih atau mengetik target secara langsung.
- Konfirmasi otorisasi eksplisit wajib sebelum setiap eksekusi pada target yang belum disematkan.
- Ambang berhenti otomatis, tidak pernah beban tanpa batas.
- Ekspor JSON/CSV/HTML terperinci (tahap, metrik per interval, putusan, diagnosis).
- Mode CLI non-interaktif untuk otomasi (cron, CI), yang memanggil kasus penggunaan yang persis sama dengan TUI.
- Penyesuaian otomatis dengan terminal (tema + profil tampilan yang dapat disederhanakan).

## Yang tidak dilakukan proyek ini

- Tidak menggantikan alat pemindai jaringan — kosakata dan sikap produk sengaja “uji beban”, tidak pernah “pemindaian”.
- Tidak mengimplementasikan mesin beban eksternal apa pun (k6, dll.) — pembangkitan bawaan dengan `httpx`/asyncio.
- Tidak pernah memulai eksekusi tanpa batas dan tanpa konfirmasi otorisasi.
- Bukan alat beban terdistribusi: pembangkitan berjalan di satu mesin, dalam satu proses — lihat [Keterbatasan yang diketahui](#keterbatasan-yang-diketahui).

## Fitur

- **Tiga keluarga uji**, masing-masing dengan 8 level intensitas (Lemah/Rendah/Sedang/Tinggi/Kuat/Agresif/Brutal/Maksimum) — lihat tabel [Acuan beban](#nilai-pengujian) untuk nilai persis setiap level.
- **Profil uji yang dibekukan**: nama, target, keluarga, intensitas, durasi, ambang galat — dibuat sekali, dijalankan ulang secara identik dari TUI atau CLI.
- **Profil durasi bernama D1-D6** (mode “profil”), alternatif dari mode manual: durasi total tetap (1 hingga 120 menit) dengan pemanasan/kenaikan/dataran/pendinginan, yang juga membatasi level yang dapat diakses — lihat [Profil durasi D1-D6](#profil-durasi-d1-d6-mode-profil).
- **Mode keamanan**, tercentang secara bawaan di setiap layar peluncuran: menghentikan uji jika mesin host (bukan target) tampak dalam bahaya. Dapat dimatikan dengan sadar, disertai pengingat yang membandingkan level yang dipilih dengan kalibrasi terakhir — lihat [Mode keamanan](#mode-keamanan).
- **Kalibrasi lokal yang tersimpan**: mengukur seberapa besar yang benar-benar sanggup ditangani mesin (7 tahap beban yang meningkat terhadap server loopback lokal bawaan), dapat dilihat dari layar Kalibrasi — lihat [Kalibrasi lokal](#kalibrasi-lokal).
- **Target yang disematkan**: alamat yang disematkan tidak perlu dicentang ulang otorisasinya pada setiap peluncuran; target terbaru yang tidak disematkan tetap terlihat (paling banyak 10) tanpa otorisasi tersirat. Target yang disematkan dapat dipakai dengan dua cara yang saling independen: langsung, untuk meluncurkan uji dalam mode manual tanpa profil, atau sebagai target bawaan saat membuat profil yang dibekukan.
- **Riwayat lengkap**: setiap eksekusi dicatat (putusan, metrik, kronologi per interval, mode keamanan yang dipakai); eksekusi yang terkait dengan profil yang dibekukan dapat diulang secara identik.
- **Ekspor terperinci** dalam JSON (data mentah yang dapat diimpor ulang), CSV (analisis tabel) atau HTML (laporan yang mudah dibaca, dengan tema pilihan dari 10 palet proyek). Laporan HTML ditulis dalam bahasa yang dipilih di Pengaturan (“Bahasa ekspor”, bawaannya sama dengan antarmuka); JSON dan CSV tetap berupa data dan tidak diterjemahkan.
- **Pra-pemeriksaan** otomatis dan wajib sebelum setiap uji Brutal/Maksimum, opsional (tetapi membuka durasi tambahan) pada Kuat/Agresif, dengan jendela keberlakuan (24 jam).
- **Pemantauan langsung** uji yang sedang berjalan: indikator kemajuan dengan hitung mundur yang andal (sisa waktu dihitung langsung, tidak pernah diperkirakan), laju/galat/latensi p95 diperbarui setiap interval, penghentian manual dimungkinkan tanpa keluar dari aplikasi.
- **Pengaturan terpusat**: tema (10 palet Omega + semua tema bawaan Textual, total 31 lewat palet perintah), profil tampilan (otomatis atau dipaksakan), folder ekspor dan tangkapan layar, pembersihan target/riwayat.
- **Bantuan terpadu** (tombol `a`): pintasan keyboard, deskripsi setiap layar (termasuk Kalibrasi dan Mode keamanan), tabel acuan nilai beban, dan tabel profil durasi D1-D6.
- **CLI untuk skrip** (`omega-stress profile|run|history|export|calibrate ...`), kasus penggunaan yang persis sama dengan TUI, dengan keluaran `--json` untuk otomasi.
- **Penyesuaian otomatis dengan terminal**: keluarga dan ukuran dideteksi saat mulai, tema dan kekayaan tampilan disesuaikan (lihat [Terminal yang didukung](#terminal-yang-didukung)).

## Arsitektur

Clean Architecture + Ports & Adapters dalam 9 paket (`app/`, `core/`, `domain/`, `application/`, `ports/`, `infrastructure/`, `interfaces/`, `plugins/`, `shared/`).
Detail lengkap: `ARCHITECTURE.md`.

```text
src/omega_stress/
├── app/              Bootstrap dan kontainer injeksi dependensi (perakitan manual, tanpa framework DI)
├── core/             Kosakata lintas bagian: enumerasi, pengecualian akar, Result/Ok/Err, kapabilitas sistem
├── domain/           Logika bisnis murni: beban, profil, eksekusi, target, tema, terminal — tanpa I/O
├── application/      Orkestrasi: commands (aksi), queries (pembacaan), pipeline eksekusi (guards/hooks)
├── ports/            Kontrak Protocol/ABC yang diharapkan adaptor (repositori, pengekspor, pembangkit beban...)
├── infrastructure/   Implementasi konkret: SQLite, pengekspor JSON/CSV/HTML, pembangkit httpx/asyncio, deteksi terminal, probe sistem
├── interfaces/       Dua adaptor presentasi yang independen: TUI (Textual) dan CLI (argparse)
├── plugins/          Titik perluasan yang dicadangkan (pemuatan plugin) — kerangka sudah ada, belum diimplementasikan di V1
└── shared/           Utilitas lintas bagian tanpa dependensi bisnis (jam yang dapat diinjeksi, pembuatan pengenal)
```

### Prinsip desain

- `domain/` tidak berisi I/O maupun dependensi pada infrastruktur — logika bisnis murni, sepenuhnya dapat diuji tanpa mock.
- `application/` mengorkestrasi kasus penggunaan melalui domain dan port, tidak pernah langsung melalui kelas konkret dari `infrastructure/`.
- `infrastructure/` mengimplementasikan port tanpa pernah diimpor langsung oleh `application/` atau `domain/` — hanya `interfaces/` dan `app/` yang merujuknya.
- `interfaces/` tidak boleh memanggil `infrastructure/` atau `subprocess` secara langsung: hanya melalui `application/` (commands/queries) dan controller-nya sendiri.
- `ports/` mendefinisikan kontrak yang diharapkan adaptor (Protocol), tidak pernah implementasi.
- `core/` menghimpun kosakata yang dipakai bersama semua lapisan, tanpa pernah memasukkan aturan bisnis bernilai angka (ambang, durasi, preset — selalu di `domain/*/policies.py`).

Dependency Rule (hanya dari lapisan luar ke lapisan dalam) dan isolasi teknologi pihak ketiga (`textual`, `sqlite3`, `httpx`, `jinja2`, masing-masing terbatas pada titik masuk yang ditentukan) diperiksa secara otomatis setiap kali `lint-imports` dijalankan (lihat [Pengujian dan kualitas](#pengujian-dan-kualitas)).

## Prasyarat

- Python ≥ 3.10
- [`uv`](https://github.com/astral-sh/uv) disarankan untuk mengelola dependensi (jika tidak, `pip` standar)

### Sistem

- Linux, terutama Arch Linux dan distribusi yang kompatibel.
- Python 3.10 atau lebih baru.
- Tidak perlu hak root: Omega-Stress hanya melakukan panggilan HTTP keluar sebagai pengguna biasa.

## Instalasi

Arsip resmi disediakan dalam format `.tar.gz`. Periksa integritasnya sebelum memasang:

```bash
sha256sum omega-stress.tar.gz
```

### Metode 1 — skrip instalasi

```bash
[ -d omega-stress ] && echo "ℹ️ Sudah diekstrak di sini, langkah dilewati." || tar -xzf omega-stress.tar.gz
[ -d ~/omega-stress ] && echo "ℹ️ ~/omega-stress sudah ada, pemindahan dilewati." || mv omega-stress ~/
cd ~/omega-stress/
chmod +x install.sh
./install.sh
```

### Metode 2 — instalasi lengkap yang tangguh

Perintah ini dapat disalin dan ditempel apa adanya serta dijalankan ulang tanpa galat: setiap langkah melewati apa yang sudah dilakukan.

```bash
( [ -d omega-stress ] || tar -xzf omega-stress.tar.gz ) && \
( [ -d ~/omega-stress ] || mv omega-stress ~/ ) && \
cd ~/omega-stress && chmod +x install.sh && ./install.sh
```
`install.sh`:

1. Membuat lingkungan virtual `.venv` jika belum ada.
2. Memasang dependensi (`pip install -e .`; `pyproject.toml` tetap menjadi satu-satunya sumber kebenaran).
3. Menjadikan `omega-stress.sh` dan `install.sh` dapat dieksekusi.
4. Menambahkan alias `stress` ke `~/.bashrc` dan `~/.zshrc` (tanpa duplikat jika sudah ada).

## Instalasi (pengembangan)

```bash
uv sync --all-extras
# atau, tanpa uv:
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```


### Menjalankan

```bash
cd ~/omega-stress
./omega-stress.sh

# atau cukup ketik "stress" di terminal baru jika alias sudah dibuat
```

Peluncur:

1. Mendeteksi `.venv`, `venv`, atau Python sistem.
2. Mengatur `PYTHONPATH` ke `src/`.
3. Menjalankan `python -m omega_stress` — tanpa argumen membuka TUI; dengan argumen diteruskan ke CLI.

### Bahasa antarmuka

Antarmuka tersedia dalam 17 bahasa: Prancis, Inggris, Spanyol, Portugis (Brasil), Italia, Jerman, Belanda, Polandia, Rusia, Tionghoa Sederhana, Vietnam, Thai, Indonesia, Jepang, Korea, Hindi, dan Arab. Pilihan dibuat di Pengaturan (“Langue / Language”) dan berlaku setelah antarmuka dimulai ulang; variabel `OMEGA_STRESS_LANG` (misalnya `OMEGA_STRESS_LANG=id ./omega-stress.sh`) memaksakan bahasa untuk satu sesi. Jika dijalankan dari omega-suite, omega-stress memakai bahasa rangkaian. Di konsol teks Linux (TTY), bahasa beraksara non-Latin ditampilkan dalam bahasa Inggris selama sesi itu. Baris perintah tetap berbahasa Prancis.

### Penggunaan CLI

```bash
omega-stress profile list                                     # menampilkan daftar profil
omega-stress profile create --name "Survei API" --target-id t-1 \
    --family request --level bas --duration-minutes 1 --max-error-rate 0.05
omega-stress profile freeze <profile-id>                       # membekukan profil

# Pra-pemeriksaan wajib sebelum setiap peluncuran Brutal/Maksimum (opsional pada Kuat/Agresif)
omega-stress run precheck --target-id t-1 --target-url https://exemple.org --confirm

omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level bas --duration-minutes 1 --max-error-rate 0.05 --confirm
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level moyen --duration-minutes 3 --max-error-rate 0.05 --confirm
omega-stress run ramp --target-id t-1 --target-url https://exemple.org \
    --level puissant --duration-minutes 3 --max-error-rate 0.05 --confirm --precheck-validated

# Mode profil D1-D6, sebagai ganti --duration-minutes (saling eksklusif)
# D4 (resilience) mengizinkan Agresif tanpa syarat, Brutal dengan konfirmasi diperkuat
omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-preset d4 --max-error-rate 0.05 --confirm \
    --precheck-validated --confirmation-text JE_CONFIRME_LA_CIBLE_AUTORISEE

# --unsafe mematikan mode keamanan (pengaman CPU/memori lokal); tidak ada secara bawaan
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-minutes 1 --max-error-rate 0.05 --confirm \
    --precheck-validated --unsafe

omega-stress run replay <run-id> --confirm                     # mengulang eksekusi yang terkait dengan profil yang dibekukan

omega-stress history list                                      # riwayat eksekusi
omega-stress history show <run-id>                              # detail sebuah eksekusi

omega-stress export <run-id> --format html --destination var/exports --theme omega-base

omega-stress calibrate run                                      # menjalankan kalibrasi mesin ini
omega-stress calibrate show                                     # menampilkan kalibrasi terakhir yang diketahui
```

Nilai `--level` (`faible`, `bas`, `moyen`, `haut`, `puissant`, `agressif`, `violent`, `maximum`) dan teks konfirmasi tetap dalam bahasa Prancis, seperti bagian lain baris perintah.

`--confirm` adalah padanan baris perintah untuk kotak otorisasi di TUI: wajib untuk setiap target yang belum disematkan sebagai terotorisasi. `--target-id`/`--target-url` yang identik menandakan target manual (tidak disematkan); gunakan pengenal target yang sudah disematkan agar tidak perlu `--confirm` setiap kali meluncurkan.

Tambahkan `--json` pada `history`/`export`/`calibrate` untuk keluaran yang dapat dibaca mesin, berguna di cron/CI.

### Alur umum

1. Pada peluncuran pertama, layar utama menawarkan: Profil, Uji permintaan, Uji koneksi, Uji beban, Riwayat, Target, Kalibrasi, Pengaturan, Bantuan.
2. Dari layar uji, profil yang dibekukan (opsional) tetap dapat dipilih di bagian atas: dua cara mengisi target dan kriteria, tidak pernah digabung dalam satu peluncuran —
   - **dengan profil**: memilihnya mengisi target/intensitas/durasi/ambang galat, dan kolom target manual menghilang (tidak relevan lagi); nilai yang terisi tetap dapat diubah sebelum meluncurkan;
   - **tanpa profil (mode manual)**: memilih target yang disematkan/terbaru dari daftar atau mengetik yang baru, mencentang otorisasi jika belum disematkan sebagai terotorisasi, mengatur sendiri intensitas/durasi (manual atau profil durasi D1-D6)/ambang galat.

   Dalam kedua kasus: biarkan mode keamanan aktif atau matikan dengan sadar, jalankan pra-pemeriksaan jika level mewajibkannya, lalu luncurkan uji.
3. Hasil langsung ditampilkan (putusan, metrik, kronologi), tanpa melalui Riwayat — ekspor ditawarkan langsung dari layar ini.
4. Profil dapat dibekukan untuk menjalankan ulang uji yang sama secara identik di kemudian hari, dari layar Profil atau dengan mengulangnya dari Riwayat.

### Nilai pengujian

8 level intensitas, identik di tiga keluarga uji (hanya dimensi yang dikendalikan yang berbeda) — tabel lengkap:

| Jenis uji | Level | Dimensi yang dikendalikan | Nilai sasaran | Pra-pemeriksaan | Durasi yang tersedia (mode manual) |
|---|---|---|---|---|---|
| Uji permintaan | Lemah | Laju | 250 perm/mnt (≈4,2 perm/dtk) | Tidak | 1 hingga 5 menit |
| Uji permintaan | Rendah | Laju | 500 perm/mnt (≈8,3 perm/dtk) | Tidak | 1 hingga 5 menit |
| Uji permintaan | Sedang | Laju | 1000 perm/mnt (≈16,7 perm/dtk) | Tidak | 1 hingga 5 menit |
| Uji permintaan | Tinggi | Laju | 2000 perm/mnt (≈33,3 perm/dtk) | Tidak | 1 hingga 5 menit |
| Uji permintaan | Kuat | Laju | 6000 perm/mnt (≈100 perm/dtk) | Opsional | 1 hingga 3 menit (5 jika lolos pra-pemeriksaan) |
| Uji permintaan | Agresif | Laju | 10.000 perm/mnt (≈167 perm/dtk) | Opsional | 1 hingga 3 menit (5 jika lolos pra-pemeriksaan) |
| Uji permintaan | Brutal | Laju | 15.000 perm/mnt (≈250 perm/dtk) | **Wajib** | Hanya 1 hingga 3 menit |
| Uji permintaan | Maksimum | Laju | 20.000 perm/mnt (≈333 perm/dtk) | **Wajib** | Hanya 1 hingga 3 menit |
| Uji koneksi | Lemah | Koneksi serentak | 25 koneksi | Tidak | 1 hingga 5 menit |
| Uji koneksi | Rendah | Koneksi serentak | 50 koneksi | Tidak | 1 hingga 5 menit |
| Uji koneksi | Sedang | Koneksi serentak | 100 koneksi | Tidak | 1 hingga 5 menit |
| Uji koneksi | Tinggi | Koneksi serentak | 200 koneksi | Tidak | 1 hingga 5 menit |
| Uji koneksi | Kuat | Koneksi serentak | 1000 koneksi | Opsional | 1 hingga 3 menit (5 jika lolos pra-pemeriksaan) |
| Uji koneksi | Agresif | Koneksi serentak | 2000 koneksi | Opsional | 1 hingga 3 menit (5 jika lolos pra-pemeriksaan) |
| Uji koneksi | Brutal | Koneksi serentak | 3500 koneksi | **Wajib** | Hanya 1 hingga 3 menit |
| Uji koneksi | Maksimum | Koneksi serentak | 5000 koneksi | **Wajib** | Hanya 1 hingga 3 menit |
| Uji beban (kenaikan bertahap) | Lemah | Laju, bertahap naik | puncak 250 perm/mnt | Tidak | 1 hingga 5 menit |
| Uji beban (kenaikan bertahap) | Rendah | Laju, bertahap naik | puncak 500 perm/mnt | Tidak | 1 hingga 5 menit |
| Uji beban (kenaikan bertahap) | Sedang | Laju, bertahap naik | puncak 1000 perm/mnt | Tidak | 1 hingga 5 menit |
| Uji beban (kenaikan bertahap) | Tinggi | Laju, bertahap naik | puncak 2000 perm/mnt | Tidak | 1 hingga 5 menit |
| Uji beban (kenaikan bertahap) | Kuat | Laju, bertahap naik | puncak 6000 perm/mnt | Opsional | 1 hingga 3 menit (5 jika lolos pra-pemeriksaan) |
| Uji beban (kenaikan bertahap) | Agresif | Laju, bertahap naik | puncak 10.000 perm/mnt | Opsional | 1 hingga 3 menit (5 jika lolos pra-pemeriksaan) |
| Uji beban (kenaikan bertahap) | Brutal | Laju, bertahap naik | puncak 15.000 perm/mnt | **Wajib** | Hanya 1 hingga 3 menit |
| Uji beban (kenaikan bertahap) | Maksimum | Laju, bertahap naik | puncak 20.000 perm/mnt | **Wajib** | Hanya 1 hingga 3 menit |

- **Pra-pemeriksaan Tidak**: uji langsung dimulai, tanpa syarat durasi.
- **Pra-pemeriksaan Opsional** (Kuat/Agresif): uji dimulai tanpa pra-pemeriksaan (durasi 1-3 menit), tetapi pra-pemeriksaan yang lolos juga membuka durasi 4-5 menit.
- **Pra-pemeriksaan Wajib** (Brutal/Maksimum): uji tidak akan dimulai tanpa pra-pemeriksaan yang sudah lolos; durasinya tetap dibatasi 3 menit meskipun dengan pra-pemeriksaan (di sini pra-pemeriksaan menentukan akses ke level, bukan perpanjangan durasi).

Kolom “Durasi yang tersedia” di atas hanya mencakup **mode manual** (paling lama 5 menit). Lebih dari itu, hanya [mode profil D1-D6](#profil-durasi-d1-d6-mode-profil) yang memungkinkan uji lebih lama (hingga 120 menit) — setiap profil D1-D6 sendiri yang menentukan level mana yang tetap dapat diakses pada durasi tersebut (`free_max_level`/`reinforced_level`, lihat tabelnya sendiri):

| Level | Durasi maks. dalam mode manual | Durasi maks. melalui profil D1-D6 |
|---|---|---|
| Lemah / Rendah / Sedang / Tinggi | 5 menit | 120 menit (D6, hanya Koneksi/Beban); 60 menit untuk Permintaan (D5, D6 tidak kompatibel dengan keluarga ini) |
| Kuat | 5 menit (3 menit tanpa pra-pemeriksaan) | 120 menit dengan konfirmasi diperkuat (D6, Koneksi/Beban) atau 60 menit tanpanya (D5) |
| Agresif | 5 menit (3 menit tanpa pra-pemeriksaan) | 60 menit dengan konfirmasi diperkuat (D5) atau 30 menit tanpanya (D4) |
| Brutal | 3 menit (pra-pemeriksaan wajib) | 30 menit dengan konfirmasi diperkuat (D4) atau 15 menit tanpanya (D3) |
| Maksimum | 3 menit (pra-pemeriksaan wajib) | paling lama 5 menit (hanya D1/D2 — tidak ada profil D3-D6 yang menawarkan Maksimum, bahkan dengan konfirmasi) |

Tabel yang sama tersedia langsung di aplikasi (Bantuan → Acuan beban), selalu dihasilkan dari nilai acuan yang sama (`domain/load/presets.py`, `domain/load/policies.py`) — tidak pernah disalin dengan tangan.

> Pada Uji beban dalam **mode manual**, kenaikan dan dataran otomatis diskalakan ke durasi yang dipilih (dengan mempertahankan proporsi preset): uji 1 menit menjelajahi seluruh kurva, dari 0 hingga puncak, bukan hanya awalnya. Dalam **mode profil D1-D6**, jaminan yang sama diberikan secara bawaan oleh pembagian pemanasan/kenaikan/dataran/pendinginan setiap profil — lihat [Profil durasi D1-D6](#profil-durasi-d1-d6-mode-profil).

### Navigasi

- Panah atas/bawah: menggerakkan kursor.
- `Tab` / `Shift+Tab`: berpindah antarkolom formulir.
- `Esc`: kembali (konfirmasi keluar dari layar utama).
- `a`: menampilkan bantuan.
- `t`: mengganti tema.
- `q`: keluar (dengan konfirmasi).
- `r`: menyegarkan tampilan, berguna setelah mengubah ukuran terminal.
- `Ctrl+P`: palet perintah (ganti tema, tangkapan layar, bantuan pintasan).

Beralih antartema dengan `t`: Omega-Stress otomatis menyesuaikan warna dan kekayaan tampilan dengan kemampuan terminal yang terdeteksi, dari layar mana pun. Dari palet perintah (`Ctrl+P` → Tema), ke-31 tema yang tersedia ditawarkan (10 tema Omega + 21 tema bawaan Textual).

### Terminal yang didukung

Empat profil tampilan, dari yang paling kaya hingga yang paling disederhanakan: **Lengkap**, **Standar**, **Ringkas**, **Mono**. Profil yang dipakai adalah yang lebih ketat antara keluarga terminal yang terdeteksi dan ukuran jendela yang sebenarnya (tidak pernah lebih kaya daripada salah satu dari kedua batas atas itu).

| Terminal | Profil bawaan |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | Lengkap |
| Konsole, GNOME Terminal, Terminator, xfce4-terminal | Standar |
| urxvt, xterm | Ringkas |
| TTY Linux | Mono |
| SSH (true color/256 warna terdeteksi) | Ringkas |
| SSH (sinyal minimal) | Mono |
| Terminal tidak dikenal | Ringkas (cadangan yang hati-hati) |

Di bawah 80 kolom × 24 baris, layar peringatan muncul sebelum layar utama (tidak pernah memblokir: aplikasi tetap dapat dipakai dalam mode yang disederhanakan). Konsole, GNOME Terminal, dan Terminator dikenali lewat variabel lingkungan khas masing-masing (`KONSOLE_VERSION`, `GNOME_TERMINAL_SCREEN`/`GNOME_TERMINAL_SERVICE`, `TERMINATOR_UUID`) alih-alih `TERM`, yang dibiarkan pada nilai kompatibilitas umumnya — xfce4-terminal sejauh ini tidak memasang penanda setara yang diketahui, sehingga hanya jatuh ke profil Standar yang sama jika menampilkan nilai `TERM`/`TERM_PROGRAM` yang dapat dikenali, selain itu Ringkas.

### Jalur internal dan jalur sistem

Secara bawaan, Omega-Stress bekerja di folder `var/` miliknya sendiri, relatif terhadap direktori tempat ia dijalankan (atau `$OMEGA_STRESS_VAR_DIR` jika ditetapkan):

```text
var/db/app.db           # basis data SQLite (profil, target, riwayat)
var/settings.json       # pengaturan tersimpan (tema, profil tampilan, folder bawaan)
var/exports/            # ekspor JSON/CSV/HTML bawaan
var/screenshots/        # tangkapan layar SVG bawaan (palet perintah)
var/audit.jsonl         # log audit (satu baris per eksekusi)
var/app.log             # log aplikasi
```

Jalur sistem absolut (mis. `/var/exports/`) tidak pernah dipakai secara bawaan — jadi `/` di awal itu bermakna: hanya ekspor eksplisit ke folder yang dipilih pengguna (Pengaturan atau layar Ekspor) yang keluar dari folder ini.

## Profil durasi D1-D6 (mode profil)

Alternatif dari mode manual (durasi 1-5 menit, dibatasi per level): **profil durasi bernama**, dengan durasi total tetap dan pembagian internal menjadi 4 fase (pemanasan, kenaikan, dataran, pendinginan). Dapat dipilih di setiap layar peluncuran (sakelar “Mode durasi: Manual / Profil D1-D6”) dan di CLI lewat `--duration-preset`.

| Profil | Durasi total | Pemanasan | Kenaikan | Dataran | Pendinginan | Level maks. tanpa konfirmasi | Level tambahan (konfirmasi diperkuat) | Keluarga yang kompatibel |
|---|---|---|---|---|---|---|---|---|
| D1 (quick) | 1 menit | 5 dtk | 10 dtk | 40 dtk | 5 dtk | Maksimum | — | Permintaan, Koneksi, Beban |
| D2 (short) | 5 menit | 15 dtk | 30 dtk | 4 menit | 15 dtk | Maksimum | — | Permintaan, Koneksi, Beban |
| D3 (standard) | 15 menit | 30 dtk | 1 menit 30 | 12 menit 30 | 30 dtk | Brutal | — | Permintaan, Koneksi, Beban |
| D4 (resilience) | 30 menit | 1 menit | 3 menit | 25 menit | 1 menit | Agresif | Brutal | Permintaan, Koneksi, Beban |
| D5 (extended) | 60 menit | 2 menit | 5 menit | 51 menit | 2 menit | Kuat | Agresif | Permintaan, Koneksi, Beban |
| D6 (soak) | 120 menit | 3 menit | 10 menit | 104 menit | 3 menit | Tinggi | Kuat | Koneksi, Beban (tidak pernah Permintaan) |

- Level “tambahan” (D4-D6) hanya dapat diakses dengan mengetik persis teks konfirmasi diperkuat yang ditampilkan di layar — tidak pernah dengan kotak centang biasa.
- D6 tidak mencakup Uji permintaan: uji laju dibatasi oleh volume, yang tidak pernah relevan untuk profil 2 jam yang berfokus pada penyimpangan seiring waktu.
- Tabel yang sama tersedia di aplikasi (Bantuan → Profil durasi D1-D6).

## Mode keamanan

Kotak centang di setiap layar peluncuran (tercentang secara bawaan) yang **hanya** mengubah pengaman yang melindungi mesin tempat Omega-Stress berjalan (CPU/memori pembangkit lokal):

- **Selalu aktif, apa pun pengaturan ini**: ambang yang melindungi **target yang diuji** (tingkat galat, latensi) — mematikannya tidak pernah masuk akal bagi produk; bukan itu yang dicakup kotak ini.
- **Mode keamanan aktif (bawaan)**: uji berhenti otomatis jika mesin host sendiri tampak tertekan (CPU pembangkit DAN CPU keseluruhan mesin tinggi bersamaan, bukan salah satu saja — saturasi normal satu inti saja tidak pernah cukup dengan sendirinya).
- **Mode keamanan mati**: pengaman lokal ini dilepas. Lalu muncul pengingat yang membandingkan level yang dipilih dengan kalibrasi terakhir yang diketahui untuk mesin ini (lihat [Kalibrasi lokal](#kalibrasi-lokal)) — melampaui batas aman itu tetap mungkin, tetapi keandalan hasil dan kestabilan mesin menjadi tanggung jawab pengguna.

Tersedia juga di CLI lewat `--unsafe` (tidak ada secara bawaan = mode keamanan aktif).

## Kalibrasi lokal

Mengukur kapasitas nyata **mesin ini** (bukan target yang diuji): server loopback lokal yang tertanam dalam Omega-Stress menerima beban yang meningkat bertahap, dibangkitkan oleh mesin `httpx`/asyncio yang sama dengan uji sungguhan.

- 7 tahap, dari diam (derau latar sistem) hingga 2000 koneksi / 12.000 perm/dtk, masing-masing dinilai terhadap ambang kesehatan (CPU pembangkit DAN keseluruhan, memori tersedia, tingkat galat, laju yang dicapai) — 2 tahap terakhir bersyarat, dilewati jika tahap sebelumnya tidak sehat.
- Menghasilkan batas aman (`VU_safe` / `RPS_safe`) dari tahap sehat terakhir, dengan margin keamanan (~30 % cadangan) dan tingkat keyakinan yang naik seiring kedalaman yang dicapai.
- **Hanya pengukuran di V1**: hasilnya tidak diterapkan otomatis untuk membatasi uji sungguhan — hasilnya menjadi acuan informatif, terutama saat [Mode keamanan](#mode-keamanan) dimatikan.
- Disimpan per mesin (sidik jari non-invasif: OS/arsitektur/jumlah inti/RAM, tidak pernah alamat perangkat keras), dapat dilihat kapan saja tanpa mengukur ulang.

Dapat diakses dari layar **Kalibrasi** di TUI (tombol “Mulai kalibrasi”, kemajuan ditampilkan detik demi detik), atau di CLI:

```bash
omega-stress calibrate run     # menjalankan kalibrasi baru
omega-stress calibrate show    # menampilkan kalibrasi terakhir yang diketahui, tanpa menjalankan yang baru
```

## Konfigurasi

Semuanya diatur dari layar **Pengaturan** di TUI (tanpa berkas konfigurasi yang perlu disunting dengan tangan):

- **Tema**: salah satu dari 10 tema Omega, langsung diterapkan dan disimpan.
- **Profil tampilan**: Otomatis (deteksi saat mulai) atau dipaksakan secara manual (Lengkap/Standar/Ringkas/Mono).
- **Folder ekspor bawaan**: mengisi kolom “tujuan” di layar Ekspor.
- **Folder tangkapan layar bawaan**: dipakai oleh perintah “Tangkapan layar” di palet (`Ctrl+P`).
- **Pembersihan**: target terbaru (tidak pernah yang disematkan), semua target (termasuk yang disematkan beserta otorisasinya), atau seluruh riwayat — masing-masing dilindungi konfirmasi tersendiri.

Pengaturan disimpan di `var/settings.json`. Akar `var/` itu sendiri dapat dialihkan lewat variabel lingkungan `OMEGA_STRESS_VAR_DIR` (berguna untuk memisahkan beberapa instans, atau untuk pengujian).

## Pengujian dan kualitas

```bash
pytest
ruff check .
mypy src
lint-imports   # memeriksa Dependency Rule (lihat pyproject.toml [tool.importlinter])
```

Rangkaian ini mencakup lebih dari 570 pengujian (unit, integrasi, TUI, CLI). `lint-imports` menggagalkan CI jika Dependency Rule atau isolasi teknologi pihak ketiga dilanggar — lihat [Arsitektur](#arsitektur).

## Penghapusan instalasi

Omega-Stress tidak menyentuh apa pun di luar foldernya sendiri dan satu baris alias opsional:

```bash
rm -rf ~/omega-stress
sed -i '/alias stress=/d' ~/.bashrc ~/.zshrc
```

`install.sh` tidak membuat paket sistem, layanan, maupun berkas di luar `~/omega-stress/` — tidak perlu penghapusan tambahan.

## Keterbatasan yang diketahui

- Pembangkitan beban **di dalam proses itu sendiri**, di satu mesin (`httpx`/asyncio): ini bukan alat terdistribusi — batas atas yang nyata (lihat [Nilai pengujian](#nilai-pengujian)) jauh lebih sederhana daripada layanan uji beban SaaS (loader.io, dll.), dengan sengaja, sebagai sikap produk yang terkendali. Pada perangkat keras sederhana, level Agresif/Brutal/Maksimum pada Uji koneksi dapat memerlukan waktu nyata yang jauh lebih lama daripada durasi yang dipilih untuk mengirim seluruh beban yang ditargetkan — saat itu kapasitas **mesin ini**, bukan target, yang membatasi laju nyata; gunakan [Kalibrasi lokal](#kalibrasi-lokal) untuk mengetahui nilai yang wajar bagi perangkat keras Anda.
- Deteksi otomatis keluarga terminal bergantung pada variabel lingkungan: xfce4-terminal sejauh ini belum memiliki penanda andal yang diketahui (lihat [Terminal yang didukung](#terminal-yang-didukung)).
- `plugins/` adalah titik perluasan yang direncanakan arsitektur (pemuatan plugin bawaan/eksternal), belum diimplementasikan di V1: kerangkanya ada, belum ada plugin yang disertakan.
- `var/` relatif terhadap folder proyek (bukan XDG): dirancang untuk penggunaan lokal oleh satu pengguna, bukan untuk dibagi oleh banyak pengguna di mesin yang sama.
- Uji beban (kenaikan bertahap) dalam **mode manual** tidak memiliki tahap penurunan (“cooldown”) setelah dataran — hanya tersedia melalui [profil durasi D1-D6](#profil-durasi-d1-d6-mode-profil), yang sudah mencakup 4 fase.
- Pra-pemeriksaan yang lolos tidak terikat pada target tertentu: berlaku 24 jam untuk setiap peluncuran Brutal/Maksimum berikutnya, bukan hanya pada target yang diperiksa.
- [Kalibrasi lokal](#kalibrasi-lokal) mengukur, tetapi belum otomatis menerapkan batas amannya untuk membatasi uji sungguhan — sebuah pekerjaan yang sengaja dipisahkan, belum dimulai.

## Lisensi

MIT — lihat `LICENSE`.
