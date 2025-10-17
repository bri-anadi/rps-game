# Rock Paper Scissors Game

Game Rock Paper Scissors modern dengan fitur lengkap yang dibangun menggunakan Python dan Tkinter, menampilkan level kesulitan AI, timer bergaya catur, tantangan harian, dan pelacakan statistik komprehensif.

## Fitur

### Gameplay Inti
- **Mekanik RPS Klasik**: Bermain Rock, Paper, Scissors melawan lawan AI yang cerdas
- **Shortcut Keyboard**: Bermain cepat menggunakan R (Rock), P (Paper), S (Scissors), ESC (Reset)
- **Hasil Animasi**: Animasi hitung mundur dan perayaan pemenang
- **Statistik Real-time**: Tingkat kemenangan, streak saat ini, dan pelacakan streak terbaik

### Sistem Timer Bergaya Catur
- **Timer Ganda**: Pool waktu terpisah untuk pemain dan komputer
- **Berbasis Giliran**: Waktu hanya berjalan selama giliran Anda
- **Batas Waktu Beragam**: Game 1, 3, 5, 10, atau 15 menit
- **Kemenangan Timeout**: Menang otomatis jika lawan kehabisan waktu
- **Peringatan Visual**: Timer berkedip merah ketika di bawah 10 detik

### Level Kesulitan AI
- **Easy**: Gerakan acak dengan kesalahan sesekali
- **Normal**: Pemilihan acak murni
- **Hard**: Menganalisis 5 gerakan terakhir dan melawan pola (80% akurasi)
- **Expert**: Pengenalan pola lanjutan pada 10 gerakan terakhir dengan deteksi anti-cycling (90% akurasi)

### Sistem Tantangan Harian
- **Tantangan Harian Acak**: 3 tantangan baru dibuat setiap hari
- **Berbagai Jenis Tantangan**:
  - **Wins**: Menangkan X game
  - **Streak**: Menangkan X game berturut-turut
  - **Games**: Mainkan X game
  - **Specific Choice**: Menangkan X game menggunakan Rock/Paper/Scissors
  - **Difficulty**: Menangkan X game pada mode Hard/Expert
  - **Speed**: Menangkan X game dengan cepat
- **Sistem Poin**: Dapatkan poin untuk menyelesaikan tantangan
- **Pelacakan Progress**: Progress bar visual dengan update real-time
- **Auto-Reset**: Tantangan disegarkan setiap hari pada tengah malam

### Statistik & Riwayat
- **Statistik Persisten**: Data game disimpan ke file JSON
- **Pelacakan Skor**: Kemenangan pemain, kemenangan komputer, dan seri
- **Kalkulasi Tingkat Kemenangan**: Kalkulasi persentase otomatis
- **Sistem Streak**: Lacak streak saat ini dan streak terbaik
- **Riwayat Game**: 10 game terakhir dengan timestamp dan hasil

### Desain UI Modern
- **Tema Gelap**: Palet warna ramah mata dengan aksen cerah
- **Desain Flat**: Antarmuka modern dan bersih tanpa efek 3D
- **Layout Tetap**: Window 1000x800, dioptimalkan tanpa scrolling
- **Elemen Berkode Warna**:
  - Hijau (#00ff87): Elemen pemain
  - Merah (#ff4757): Elemen komputer
  - Oranye (#ffa502): Elemen seri/netral
  - Cyan (#00d4ff): Aksen dan highlight
- **Efek Hover Responsif**: Feedback tombol interaktif
- **Tipografi Profesional**: Font Courier New di seluruh aplikasi

## Instalasi

### Prasyarat
- Python 3.6 atau lebih tinggi
- Tkinter (biasanya sudah termasuk dengan Python)

### Instalasi Tkinter Spesifik Platform

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**macOS:**
Tkinter sudah termasuk dengan instalasi Python

**Windows:**
Tkinter sudah termasuk dengan instalasi Python

### Menjalankan Game
```bash
python3 app.py
```

## Dependensi

Game ini hanya menggunakan modul pustaka standar Python:
- `tkinter` - Framework GUI
- `random` - Pengambilan keputusan AI
- `datetime` - Timestamp dan reset tantangan harian
- `json` - Simpan/muat statistik
- `os` - Operasi file
- `urllib.request` - Diimpor tapi tidak aktif digunakan
- `tempfile` - Diimpor tapi tidak aktif digunakan

**Tidak memerlukan paket pip eksternal!**

## Cara Bermain

### Kontrol Dasar
1. **Mulai Game**: Klik tombol "START GAME" atau buat gerakan pertama Anda
2. **Buat Gerakan**: Klik tombol Rock/Paper/Scissors atau tekan tombol R/P/S
3. **Reset Game**: Klik tombol "[ESC] Reset" atau tekan tombol ESC

### Sistem Timer
1. Klik "START GAME" untuk memulai timer
2. Waktu Anda berkurang ketika giliran Anda
3. Waktu komputer berkurang selama gilirannya
4. Buat gerakan Anda sebelum waktu habis
5. Gunakan "RESET TIMER" untuk restart timer
6. Klik "5 MIN" untuk mengubah batas waktu

### Tantangan
1. Klik tombol "Challenges" untuk melihat tantangan harian
2. Selesaikan tantangan dengan memenuhi persyaratannya
3. Dapatkan poin untuk setiap tantangan yang diselesaikan
4. Tantangan otomatis direset setiap hari
5. Klik "REFRESH CHALLENGES" untuk update tampilan progress

### Pengaturan Kesulitan
1. Klik tombol "Difficulty" untuk mengubah level
2. Setiap kesulitan mengubah perilaku AI:
   - **Easy**: Bagus untuk pemula
   - **Normal**: Permainan acak standar
   - **Hard**: AI mempelajari pola Anda
   - **Expert**: AI lanjutan - sangat menantang!

## Struktur File

```
RPS/
├── app.py              # File aplikasi utama
├── requirements.txt    # Informasi dependensi
├── README.md          # File ini
└── rps_stats.json     # File statistik yang dibuat otomatis
```

## Mekanik Game

### Kondisi Menang
- Rock menghancurkan Scissors
- Paper menutupi Rock
- Scissors memotong Paper
- Pilihan identik menghasilkan seri

### Sistem Skor
- Menang: +1 poin
- Seri: Tidak ada poin
- Kalah: Tidak ada poin
- Menang Timeout: +3 poin

### Sistem Streak
- Meningkat 1 untuk setiap kemenangan berturut-turut
- Reset ke 0 pada kekalahan apa pun
- Seri tidak mereset streak
- Streak terbaik disimpan secara permanen

## Persistensi Data

Statistik game otomatis disimpan ke `rps_stats.json` setelah setiap game:
- Skor Pemain/Komputer
- Total game yang dimainkan
- Streak menang/kalah
- Riwayat 10 game terakhir
- Progress tantangan
- Poin tantangan yang diperoleh
- Tanggal pembuatan tantangan terakhir

## Detail Teknis

### Arsitektur
- **Desain Berbasis Kelas**: Satu kelas `RockPaperScissorsGame` mengelola semua fungsionalitas
- **Sistem Tantangan**: Kelas `Challenge` terpisah dengan pelacakan progress
- **Event-driven**: Loop event Tkinter menangani interaksi pengguna
- **Timer Stateful**: Timer bergaya catur dengan pergantian giliran
- **Penyimpanan Persisten**: Serialisasi JSON untuk data game

### Implementasi AI
AI komputer menggunakan strategi berbeda berdasarkan kesulitan:

**Mode Easy:**
```python
# 50% peluang untuk memilih gerakan yang kalah dari pilihan terakhir pemain
# 50% peluang untuk memilih secara acak
```

**Mode Hard:**
```python
# Menganalisis 5 gerakan terakhir
# Menemukan pilihan paling umum
# Melawannya 80% dari waktu
```

**Mode Expert:**
```python
# Menganalisis 10 gerakan terakhir
# Mendeteksi pola cycling
# Strategi counter lanjutan dengan tingkat keberhasilan 90%
```

### Palet Warna
```python
'bg_primary': '#0f0f23',      # Biru-hitam gelap pekat
'bg_secondary': '#1a1d29',    # Abu-biru gelap
'bg_card': '#252838',         # Background kartu
'accent_primary': '#00ff87',   # Hijau cerah
'accent_secondary': '#00d4ff', # Cyan
'player_color': '#00ff87',     # Hijau pemain
'cpu_color': '#ff4757',        # Merah komputer
'draw_color': '#ffa502',       # Oranye
'text_primary': '#ffffff',     # Putih
'text_secondary': '#8b92a8',   # Abu-abu muda
'text_dim': '#5a5f73'          # Abu-abu redup
```

## Shortcut Keyboard

| Tombol | Aksi |
|--------|------|
| `R` atau `r` | Pilih Rock |
| `P` atau `p` | Pilih Paper |
| `S` atau `s` | Pilih Scissors |
| `ESC` | Reset game (dengan konfirmasi) |

## Spesifikasi Window

- **Ukuran**: 1000x800 piksel
- **Resizable**: Tidak (layout tetap)
- **Bagian** (dari atas ke bawah):
  1. Header dengan judul dan shortcut
  2. Tampilan timer bergaya catur
  3. Kartu statistik (tingkat kemenangan, streak, terbaik)
  4. Tampilan skor (pemain, seri, komputer)
  5. Tampilan pilihan dengan indikator VS
  6. Pesan hasil
  7. Tombol game (Rock, Paper, Scissors)
  8. Tombol kontrol (Reset, History, Difficulty, Challenges)

## Kontribusi

Ini adalah proyek pribadi, tetapi saran dan perbaikan diterima!

## Lisensi

Bebas digunakan dan dimodifikasi untuk keperluan pribadi dan edukasi.

## Riwayat Versi

- **v2.0**: Redesain UI modern dengan desain flat
- **v1.9**: Menghapus sistem custom font, standarisasi pada Courier New
- **v1.8**: Menambahkan mode kesulitan Expert
- **v1.7**: Mengimplementasikan sistem tantangan harian
- **v1.6**: Menambahkan timer bergaya catur
- **v1.5**: Meningkatkan AI dengan pengenalan pola
- **v1.0**: Rilis awal

## Kredit

Dikembangkan menggunakan Python dan Tkinter
Ikon: Karakter emoji Unicode
Font: Courier New (system font)

---

**Selamat bermain! Semoga strategis terbaik yang menang!**
