# 🎵 Discord Music Bot (Glowing Version)

Bot Discord musik premium dengan antarmuka tombol (UI), mendukung pemutaran dari **YouTube** dan **Spotify**. Proyek ini menggunakan `discord.py` dan `yt-dlp` untuk pengalaman mendengarkan musik yang lancar.

---

## ✨ Fitur Utama

* **Antarmuka Interaktif:** Kontrol musik menggunakan tombol (Play/Pause, Skip, Loop, Stop) dan embed yang dinamis.
* **Dukungan Spotify:** Putar lagu atau playlist langsung dari link Spotify.
* **Sistem Queue:** Kelola daftar antrean lagu dengan fitur paginasi.
* **Mode Loop:** Tersedia mode `off`, `song` (ulang satu lagu), dan `queue` (ulang seluruh antrean).
* **High Quality Audio:** Menggunakan FFmpeg untuk pemrosesan audio yang jernih.

---

## 🛠️ Persyaratan Sistem

Sebelum menjalankan bot, pastikan perangkat Anda sudah terinstal:
* **Python 3.8+**
* **FFmpeg:** Wajib terinstal di sistem dan path-nya sudah benar di dalam `bot.py` (Default: `C:\ffmpeg\bin\ffmpeg.exe`).
* **Spotify Credentials:** Client ID dan Client Secret dari [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

---

## 🚀 Instalasi

### 1. Kloning Repositori
```bash
git clone [https://github.com/hanif-fawwaz/bot-dc-group.git](https://github.com/hanif-fawwaz/bot-dc-group.git)
cd bot-dc-group
2. Instal DependensiBashpip install -r requirements.txt
3. KonfigurasiBuka file bot_versi_glowing.py atau bot.py dan spotify_bot.py untuk mengisi token Anda:Discord Token: Masukkan di bagian bawah file bot.Spotify API: Masukkan CLIENT_ID dan CLIENT_SECRET di spotify_bot.py.4. Jalankan BotBashpython bot_versi_glowing.py
🎮 Perintah (Commands)Bot ini mendukung Slash Commands (/) untuk kemudahan penggunaan:CommandDeskripsi/play <query/url>Putar musik dari YouTube/Spotify/nowplayingMenampilkan lagu yang sedang diputar/queueMelihat daftar antrean lagu/skipMelewati lagu saat ini/pause / /resumeMenghentikan/melanjutkan musik/loop <mode>Mengatur mode pengulangan/leaveMengeluarkan bot dari voice channel📂 Struktur Filebot_versi_glowing.py: Script utama dengan fitur UI terbaru dan Slash Commands.bot.py: Script utama versi standar (Prefix !).spotify_bot.py: Modul untuk menangani integrasi API Spotify.ui_botV2.py: Logika antarmuka tombol dan embed premium.requirements.txt: Daftar library Python yang dibutuhkan.🤝 KontribusiTarik Pull Request atau buka Issue jika Anda menemukan bug atau ingin menambahkan fitur baru.Developed by Hanif Fawwaz
**Catatan Tambahan:**
Karena di file `bot.py` dan `bot_versi_glowing.py` kamu melakukan *hardcode* path FFmpeg ke `C:\ffmpeg\bin\ffmpeg.exe`, pastikan pengguna lain tahu bahwa mereka mungkin perlu mengubah path tersebut jika menggunakan Linux atau lokasi folder yang berbeda.

Ada bagian lain yang ingin kamu tambahkan?
