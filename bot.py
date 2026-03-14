import discord
from discord.ext import commands
import yt_dlp
import asyncio
import time
import os
import shutil
from spotify_bot import get_track_query, get_playlist_queries
from ui_bot import PlayerUI

# ⚠️ GANTI TOKEN BOT KAMU DI BARIS PALING BAWAH!

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Set FFmpeg path manual
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"

# Verify FFmpeg exists
if os.path.exists(FFMPEG_PATH):
    print(f"✅ FFmpeg found at: {FFMPEG_PATH}")
else:
    print(f"❌ FFmpeg not found at: {FFMPEG_PATH}")
    print("   Please check the path!")
    FFMPEG_PATH = None

# YouTube download options
YDL_OPTIONS = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'default_search': 'ytsearch',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'noplaylist': True,
    'force_ipv4': True
}
FFMPEG_OPTIONS = {
    'before_options':
        '-reconnect 1 '
        '-reconnect_streamed 1 '
        '-reconnect_delay_max 10 '
        '-reconnect_on_network_error 1 '
        '-reconnect_on_http_error 4xx,5xx '
        '-loglevel panic',

    'options':
        '-vn '
        '-bufsize 512k'
}

# Queue data per server
guild_data = {}
loop_modes = {}

def get_loop_mode(guild_id):
    return loop_modes.get(guild_id, "off")

def set_loop_mode(guild_id, mode):
    loop_modes[guild_id] = mode

def get_guild_data(guild_id):
    """Mendapatkan data guild (queue, now playing, dll)"""
    if guild_id not in guild_data:
        guild_data[guild_id] = {
            "queue": asyncio.Queue(),
            "now_playing": None,
            "start_time": None,
            "duration": None
        }
    return guild_data[guild_id]

async def play_next(guild, voice_client, channel):
    """Memutar lagu berikutnya di queue"""
    data = get_guild_data(guild.id)
    mode = get_loop_mode(guild.id)

    if not voice_client or not voice_client.is_connected():
        return

    # Logika Loop & Queue
    if mode == "song" and data["now_playing"]:
        query = data["now_playing"]["webpage_url"]
    else:
        if data["queue"].empty():
            data["now_playing"] = None
            return await channel.send("✅ Queue habis!")
        query = await data["queue"].get()
        if mode == "queue":
            await data["queue"].put(query)

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]

        data["now_playing"] = info
        
        # PASTIKAN EXECUTABLE SELALU ADA
        source = discord.FFmpegPCMAudio(
            info['url'], 
            executable=FFMPEG_PATH, # Ini penting agar tidak error di Windows
            **FFMPEG_OPTIONS
        )

        def after_playing(error):
            if error: print(f"Player Error: {error}")
            bot.loop.create_task(play_next(guild, voice_client, channel))

        voice_client.play(source, after=after_playing)
        
        view = PlayerUI(guild, get_loop_mode, set_loop_mode)
        await channel.send(f"🎵 **Now Playing:** {info['title']}", view=view)

    except Exception as e:
        print(f"Error: {e}")
        await channel.send(f"❌ Gagal memutar lagu: {e}")
        bot.loop.create_task(play_next(guild, voice_client, channel))

@bot.event
async def on_ready():
    """Event ketika bot online"""
    try:
        synced = await bot.tree.sync()
        print(f"✅ Bot online: {bot.user}")
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    """Disconnect bot jika sendiri di channel"""
    if member.id == bot.user.id:
        return
    
    voice_client = member.guild.voice_client
    if voice_client and len(voice_client.channel.members) == 1:
        await voice_client.disconnect()
        print(f"👋 Left empty channel in {member.guild.name}")

# 🎵 COMMAND: PLAY
@bot.tree.command(name="play", description="Play music from YouTube or Spotify")
async def play(interaction: discord.Interaction, query: str):
    """Command untuk memutar musik"""
    await interaction.response.defer()
    
    guild = interaction.guild

    # Cek user di voice channel
    if not interaction.user.voice:
        return await interaction.followup.send("❌ Kamu harus join voice channel dulu!")

    print(f"📝 Play request from {interaction.user}: {query}")

    # Connect ke voice channel
    vc = guild.voice_client
    if not vc or not vc.is_connected():
        try:
            channel = interaction.user.voice.channel
            if vc:
                await vc.disconnect()
            vc = await channel.connect()
            print(f"✅ Connected to {channel.name}")
            await asyncio.sleep(1)  # Tunggu sebentar untuk koneksi stabil
        except Exception as e:
            print(f"❌ Error connecting: {e}")
            return await interaction.followup.send(f"❌ Error joining channel: {e}")

    data = get_guild_data(guild.id)

    # Handle Spotify Track
    if "open.spotify.com/track" in query:
        spotify_query = get_track_query(query)
        if not spotify_query:
            return await interaction.followup.send("❌ Error mengambil info dari Spotify")
        query = spotify_query
        print(f"🎵 Spotify track converted: {query}")

    # Handle Spotify Playlist
    elif "open.spotify.com/playlist" in query:
        tracks = get_playlist_queries(query)
        if not tracks:
            return await interaction.followup.send("❌ Error mengambil playlist dari Spotify")
        
        for q in tracks:
            await data["queue"].put(q)
        
        await interaction.followup.send(f"📀 Playlist ditambahkan: **{len(tracks)} lagu**")
        print(f"📀 Added {len(tracks)} tracks from Spotify playlist")
        
        if not vc.is_playing() and vc.is_connected():
            await play_next(guild, vc, interaction.channel)
        return

    # Tambahkan ke queue
    await data["queue"].put(query)
    await interaction.followup.send(f"➕ Ditambahkan ke queue: **{query}**")

    # Play jika sedang tidak playing dan sudah connected
    if not vc.is_playing() and vc.is_connected():
        await play_next(guild, vc, interaction.channel)
    elif not vc.is_connected():
        await interaction.followup.send("❌ Bot tidak terhubung ke voice channel")

# ⏭️ COMMAND: SKIP
@bot.tree.command(name="skip", description="Skip current song")
async def skip(interaction: discord.Interaction):
    """Skip lagu yang sedang diputar"""
    vc = interaction.guild.voice_client
    
    if not vc:
        return await interaction.response.send_message("❌ Bot tidak sedang di voice channel")
    
    if vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏭️ Skipped!")
    else:
        await interaction.response.send_message("❌ Tidak ada lagu yang sedang diputar")

# ⏸️ COMMAND: PAUSE
@bot.tree.command(name="pause", description="Pause current song")
async def pause(interaction: discord.Interaction):
    """Pause lagu"""
    vc = interaction.guild.voice_client
    
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("⏸️ Paused")
    else:
        await interaction.response.send_message("❌ Tidak ada lagu yang sedang diputar")

# ▶️ COMMAND: RESUME
@bot.tree.command(name="resume", description="Resume paused song")
async def resume(interaction: discord.Interaction):
    """Resume lagu yang di-pause"""
    vc = interaction.guild.voice_client
    
    if vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message("▶️ Resumed")
    else:
        await interaction.response.send_message("❌ Tidak ada lagu yang di-pause")

# ⏹️ COMMAND: STOP
@bot.tree.command(name="stop", description="Stop music and clear queue")
async def stop(interaction: discord.Interaction):
    """Stop musik dan clear queue"""
    vc = interaction.guild.voice_client
    
    if not vc:
        return await interaction.response.send_message("❌ Bot tidak sedang di voice channel")
    
    data = get_guild_data(interaction.guild.id)
    
    # Clear queue
    while not data["queue"].empty():
        await data["queue"].get()
    
    data["now_playing"] = None
    
    if vc.is_playing():
        vc.stop()
    
    await vc.disconnect()
    await interaction.response.send_message("⏹️ Stopped and disconnected")

# 📜 COMMAND: QUEUE
@bot.tree.command(name="queue", description="Show current queue")
async def show_queue(interaction: discord.Interaction):
    """Menampilkan daftar queue"""
    data = get_guild_data(interaction.guild.id)
    
    if data["queue"].empty():
        return await interaction.response.send_message("📜 Queue kosong")

    items = list(data["queue"]._queue)
    text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(items[:10])])
    
    total = len(items)
    if total > 10:
        text += f"\n\n... dan {total - 10} lagu lainnya"
    
    await interaction.response.send_message(f"📜 **Queue ({total} lagu):**\n{text}")

# 🎧 COMMAND: NOW PLAYING
@bot.tree.command(name="nowplaying", description="Show currently playing song")
async def nowplaying(interaction: discord.Interaction):
    """Menampilkan lagu yang sedang diputar dengan progress bar"""
    data = get_guild_data(interaction.guild.id)

    if not data["now_playing"]:
        return await interaction.response.send_message("❌ Tidak ada lagu yang sedang diputar")

    elapsed = int(time.time() - data["start_time"])
    duration = data["duration"]

    # Progress bar
    bar_length = 20
    if duration > 0:
        filled = int(bar_length * elapsed / duration)
        filled = min(filled, bar_length)
    else:
        filled = 0
    
    bar = "█" * filled + "─" * (bar_length - filled)

    # Format waktu
    elapsed_str = f"{elapsed // 60}:{elapsed % 60:02d}"
    duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "Live"

    await interaction.response.send_message(
        f"🎵 **Now Playing:**\n"
        f"**{data['now_playing']['title']}**\n"
        f"`{bar}` {elapsed_str} / {duration_str}"
    )

# 🔗 COMMAND: JOIN
@bot.tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    """Join voice channel user"""
    if not interaction.user.voice:
        return await interaction.response.send_message("❌ Kamu belum di voice channel!")
    
    vc = interaction.guild.voice_client
    
    if vc:
        await vc.move_to(interaction.user.voice.channel)
        await interaction.response.send_message(f"✅ Moved to **{interaction.user.voice.channel.name}**")
    else:
        try:
            await interaction.user.voice.channel.connect()
            await interaction.response.send_message(f"✅ Joined **{interaction.user.voice.channel.name}**")
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}")

# 🚪 COMMAND: LEAVE
@bot.tree.command(name="leave", description="Leave voice channel")
async def leave(interaction: discord.Interaction):
    """Leave voice channel"""
    vc = interaction.guild.voice_client
    
    if vc:
        await vc.disconnect()
        await interaction.response.send_message("👋 Left voice channel")
    else:
        await interaction.response.send_message("❌ Bot tidak sedang di voice channel")

# 🔧 COMMAND: DEBUG (untuk troubleshooting)
@bot.tree.command(name="debug", description="Show debug info")
async def debug(interaction: discord.Interaction):
    """Menampilkan info debug"""
    vc = interaction.guild.voice_client
    
    info = f"""
**🔧 Debug Info:**
• FFmpeg: {'✅ Found' if FFMPEG_PATH else '❌ Not found'}
• Voice Client: {'✅ Connected' if vc else '❌ Not connected'}
• Is Playing: {'✅ Yes' if vc and vc.is_playing() else '❌ No'}
• Is Paused: {'✅ Yes' if vc and vc.is_paused() else '❌ No'}
    """
    
    if FFMPEG_PATH:
        info += f"\n• FFmpeg Path: `{FFMPEG_PATH}`"
    
    await interaction.response.send_message(info)

# Remove lagu tertentu
@bot.tree.command(name="remove", description="Remove song from queue")
async def remove(interaction: discord.Interaction, index: int):
    data = get_guild_data(interaction.guild.id)
    q = list(data["queue"]._queue)

    if index < 1 or index > len(q):
        return await interaction.response.send_message("❌ Index tidak valid")

    removed = q.pop(index - 1)
    data["queue"] = asyncio.Queue()
    for item in q:
        await data["queue"].put(item)

    await interaction.response.send_message(f"🗑️ Dihapus: **{removed}**")

# Set volume
@bot.tree.command(name="volume", description="Set volume (1-100)")
async def volume(interaction: discord.Interaction, level: int):
    vc = interaction.guild.voice_client
    if not vc or not vc.source:
        return await interaction.response.send_message("❌ Tidak ada lagu")

    vc.source.volume = level / 100
    await interaction.response.send_message(f"🔊 Volume: {level}%")

@bot.tree.command(name="loop", description="Set loop mode")
async def loop(interaction: discord.Interaction, mode: str):
    """
    mode:
    off   -> tidak loop
    song  -> loop lagu sekarang
    queue -> loop seluruh queue
    """

    mode = mode.lower()

    if mode not in ["off", "song", "queue"]:
        return await interaction.response.send_message(
            "❌ Pilih: off | song | queue"
        )

    set_loop_mode(interaction.guild.id, mode)

    await interaction.response.send_message(
        f"🔁 Loop mode diset ke: **{mode.upper()}**"
    )
old_play_next = play_next

async def play_next(guild, voice_client, channel):
    data = get_guild_data(guild.id)
    mode = get_loop_mode(guild.id)

    # LOOP SONG
    if mode == "song" and data["now_playing"]:
        query = data["now_playing"]["webpage_url"]

    else:
        if data["queue"].empty():
            if mode == "queue" and data["now_playing"]:
                # Re-add last song
                await data["queue"].put(data["now_playing"]["webpage_url"])
            else:
                data["now_playing"] = None
                return await channel.send("✅ Queue habis!")

        query = await data["queue"].get()

        # LOOP QUEUE -> masukkan kembali
        if mode == "queue":
            await data["queue"].put(query)

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]

        data["now_playing"] = info
        data["start_time"] = time.time()
        data["duration"] = info.get("duration", 0)

        source = discord.FFmpegPCMAudio(info['url'], **FFMPEG_OPTIONS)

        voice_client.play(
            source,
            after=lambda e: bot.loop.create_task(
                play_next(guild, voice_client, channel)
            )
        )

        view = PlayerUI(guild, get_loop_mode, set_loop_mode)

        await channel.send(
            f"🎵 **Now Playing:** {info['title']}",
            view=view
)


    except Exception as e:
        await channel.send(f"❌ Error playing: {e}")

# ⚠️ GANTI TOKEN BOT KAMU DI SINI!
bot.run("YOUR_BOT_TOKEN_HERE")