# 🎵 Discord Music Bot (bot-dc-group)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/library-discord.py-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

Bot musik Discord modern yang mendukung pemutaran dari **YouTube** & **Spotify**. Bot ini menggunakan sistem **Slash Commands (/)** untuk pengalaman pengguna yang lebih bersih dan intuitif.

---

## ✨ Fitur Utama
- **Slash Commands Support**: Perintah yang lebih rapi dan otomatis muncul di Discord.
- **Interactive UI Buttons**: Kontrol musik langsung lewat tombol (Play/Pause, Skip, Loop, Stop).
- **Spotify Integration**: Mendukung link lagu atau playlist dari Spotify.
- **Queue Paginator**: Navigasi antrean lagu yang panjang dengan tombol halaman.
- **Smart Looping**: Mode loop per lagu (`song`) atau satu antrean (`queue`).
- **High Quality Audio**: Menggunakan FFmpeg untuk kualitas suara yang jernih.

## 🛠️ Persyaratan
- **Python 3.8+**
- **FFmpeg**: Wajib ada di sistem.
  - *Default Path:* `C:\ffmpeg\bin\ffmpeg.exe` (Sesuaikan di dalam script jika berbeda).

## 🚀 Instalasi & Setup

1. **Clone Repository**
   ```bash
   git clone [https://github.com/hanif-fawwaz/bot-dc-group.git](https://github.com/hanif-fawwaz/bot-dc-group.git)
   cd bot-dc-group
Instal DependensiBashpip install -r requirements.txt
Konfigurasi APIDiscord Token: Masukkan token bot Anda pada bagian bawah file bot.py.Spotify API: Buka spotify_bot.py dan masukkan CLIENT_ID serta CLIENT_SECRET Anda.Menjalankan BotBashpython bot.py
(Gunakan bot_versi_glowing.py untuk mencoba versi terbaru).🎮 Daftar Perintah (/)IkonCommandDeskripsi🎵/play <query>Putar musik dari YouTube/Spotify (Link/Judul)🎧/nowplayingTampilkan info lagu & kontrol tombol📜/queueLihat daftar antrean musik⏭️/skipLewati lagu yang sedang diputar🔄/loop <mode>Pilih mode loop: off, song, atau queue⏹️/stopBerhenti dan hapus semua antrean🔊/volumeAtur volume suara bot (1-100)🚪/leaveKeluarkan bot dari Voice Channel📂 Struktur Folderbot.py: Main script (Stabil).bot_versi_glowing.py: Versi pengembangan/eksperimental.spotify_bot.py: Handler untuk API Spotify.ui_bot.py & ui_botV2.py: Komponen antarmuka tombol dan embed.requirements.txt: Library yang diperlukan.⚠️ TroubleshootingCommand Tidak Muncul? Pastikan bot sudah diundang dengan scope applications.commands.Tidak Ada Suara? Cek apakah path FFmpeg di kode sudah benar dan file ffmpeg.exe ada di sana.Maintained by hanif-fawwaz
---

### Perubahan Utama:
1. **Fokus Slash Commands**: Saya menghapus instruksi prefix `!` dan fokus ke `/` karena keduanya sudah mendukung fitur tersebut.
2. **Kategori Command**: Tabel perintah sekarang lebih lengkap (ada ikonnya agar lebih menarik).
3. **Pembeda Versi**: Tetap mencantumkan `bot.py` sebagai yang utama agar user tidak bingung.

Ingin saya bantu buatkan file `.env` juga supaya token Anda tidak perlu ditulis langsung di
