# 🎵 Discord Music Bot

<p align="center">

Bot musik Discord modern dengan **YouTube + Spotify support**, **Slash Commands**, dan **Interactive UI Controls**.

</p>

<p align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge\&logo=python\&logoColor=white)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/Discord.py-Library-5865F2?style=for-the-badge\&logo=discord\&logoColor=white)](https://discordpy.readthedocs.io/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Audio%20Engine-green?style=for-the-badge\&logo=ffmpeg\&logoColor=white)](https://ffmpeg.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</p>

---

# 📌 Overview

**bot-dc-group** adalah bot musik Discord yang dibuat menggunakan **Python** dan **discord.py**.
Bot ini dirancang untuk memberikan pengalaman memutar musik yang **mudah, modern, dan interaktif** menggunakan **Slash Commands** dan **UI Buttons**.

Bot mendukung pemutaran musik dari:

* 🎥 **YouTube**
* 🎧 **Spotify (Track & Playlist)**

---

# ✨ Features

### 🎛 Modern Slash Commands

Semua perintah menggunakan **/** sehingga lebih rapi dan mudah digunakan.

### 🎮 Interactive Music Controls

Kontrol musik langsung menggunakan tombol:

* ⏯ Play / Pause
* ⏭ Skip
* 🔁 Loop
* ⏹ Stop

### 🎧 Spotify Integration

Bot dapat membaca:

* Spotify Track
* Spotify Playlist

Lalu otomatis mencari versi YouTube untuk diputar.

### 📜 Smart Queue System

Sistem antrean musik yang mendukung:

* Multi lagu
* Pagination queue
* Navigasi halaman

### 🔁 Loop System

Mode loop fleksibel:

* `off` → tidak ada loop
* `song` → ulangi lagu
* `queue` → ulangi seluruh antrean

### 🔊 High Quality Audio

Audio diproses menggunakan **FFmpeg** untuk kualitas suara optimal.

---

# 🧠 How It Works

```
User Command (/play)
        │
        ▼
Discord Slash Command Handler
        │
        ▼
Spotify / YouTube Parser
        │
        ▼
Queue Manager
        │
        ▼
FFmpeg Audio Stream
        │
        ▼
Discord Voice Channel
```

---

# 🛠 Tech Stack

| Technology  | Function                   |
| ----------- | -------------------------- |
| Python      | Programming language       |
| discord.py  | Discord API wrapper        |
| yt-dlp      | Extract audio dari YouTube |
| FFmpeg      | Audio streaming            |
| Spotify API | Fetch track & playlist     |

---

# 📦 Requirements

Pastikan sistem memiliki:

* Python **3.8 atau lebih baru**
* **FFmpeg**
* Internet connection

### Contoh lokasi FFmpeg di Windows

```
C:\ffmpeg\bin\ffmpeg.exe
```

Jika berbeda, ubah path di dalam script.

---

# 🚀 Installation

## 1️⃣ Clone Repository

```
git clone https://github.com/hanif-fawwaz/bot-dc-group.git
cd bot-dc-group
```

---

## 2️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

# ⚙️ Configuration

## Discord Bot Token

Masukkan token pada file:

```
bot.py
```

Contoh:

```python
bot.run("YOUR_DISCORD_TOKEN")
```

Token dapat diperoleh dari:

**Discord Developer Portal**

---

## Spotify API Setup

Buka file:

```
spotify_bot.py
```

Isi:

```
CLIENT_ID
CLIENT_SECRET
```

Dapatkan dari:

**Spotify Developer Dashboard**

---

# ▶️ Running the Bot

Menjalankan bot:

```
python bot.py
```

Menjalankan versi pengembangan:

```
python bot_versi_glowing.py
```

---

# 🎮 Commands List

| Command           | Description                            |
| ----------------- | -------------------------------------- |
| `/play <query>`   | Memutar lagu dari YouTube atau Spotify |
| `/nowplaying`     | Menampilkan lagu yang sedang diputar   |
| `/queue`          | Menampilkan antrean lagu               |
| `/skip`           | Lewati lagu saat ini                   |
| `/loop <mode>`    | Loop mode: off / song / queue          |
| `/stop`           | Menghentikan musik dan menghapus queue |
| `/volume <1-100>` | Mengatur volume bot                    |
| `/leave`          | Mengeluarkan bot dari voice channel    |

---

# 📂 Project Structure

```
bot-dc-group
│
├── bot.py
│
├── bot_versi_glowing.py
│
├── spotify_bot.py
│
├── ui_bot.py
│
├── ui_botV2.py
│
├── requirements.txt
│
└── README.md
```

### File Explanation

| File                 | Function          |
| -------------------- | ----------------- |
| bot.py               | Script utama bot  |
| bot_versi_glowing.py | Versi eksperimen  |
| spotify_bot.py       | Integrasi Spotify |
| ui_bot.py            | UI kontrol musik  |
| ui_botV2.py          | Versi UI terbaru  |

---

# ⚠️ Troubleshooting

## Slash Command Tidak Muncul

Pastikan bot diundang dengan permission:

```
applications.commands
```

---

## Bot Tidak Mengeluarkan Suara

Periksa:

* FFmpeg sudah terinstall
* Path FFmpeg benar
* Bot berada di voice channel

---

## Bot Tidak Join Voice Channel

Pastikan:

* Bot memiliki permission **Connect**
* Bot memiliki permission **Speak**

---

# 🗺 Roadmap

Fitur yang akan ditambahkan:

* [ ] Autoplay system
* [ ] Playlist save system
* [ ] Music recommendation
* [ ] Web dashboard
* [ ] Lavalink support
* [ ] Multi-server music sync

---

# 🤝 Contributing

Kontribusi sangat terbuka!

Langkah kontribusi:

```
1. Fork repository
2. Buat branch baru
3. Commit perubahan
4. Push ke branch
5. Buat Pull Request
```

---

# 📜 License

Project ini menggunakan **MIT License**.

---

# 👨‍💻 Author

**Hanif Fawwaz**

GitHub
https://github.com/hanif-fawwaz

---

⭐ Jika project ini membantu, jangan lupa **berikan star pada repository ini!**
