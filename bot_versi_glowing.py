import discord
from discord.ext import commands
import yt_dlp
import asyncio
import time
import os
from spotify_bot import get_track_query, get_playlist_queries
from ui_botV2 import PlayerUI, create_now_playing_embed, create_queue_embed, QueuePaginator

# ⚠️ GANTI TOKEN BOT KAMU DI BARIS PALING BAWAH!

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

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
    """Memutar lagu berikutnya di queue dengan loop support"""
    data = get_guild_data(guild.id)
    mode = get_loop_mode(guild.id)

    # Cek apakah voice client masih connected
    if not voice_client or not voice_client.is_connected():
        print("❌ Voice client not connected")
        embed = discord.Embed(
            title="❌ Error",
            description="Bot tidak terhubung ke voice channel",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)
        return

    # LOOP SONG
    if mode == "song" and data["now_playing"]:
        query = data["now_playing"]["webpage_url"]
    else:
        if data["queue"].empty():
            if mode == "queue" and data["now_playing"]:
                # Re-add last song untuk loop queue
                await data["queue"].put(data["now_playing"]["webpage_url"])
            else:
                data["now_playing"] = None
                embed = discord.Embed(
                    title="✅ Queue Selesai",
                    description="Semua lagu telah diputar!",
                    color=discord.Color.green()
                )
                await channel.send(embed=embed)
                return

        query = await data["queue"].get()

        # LOOP QUEUE -> masukkan kembali
        if mode == "queue":
            await data["queue"].put(query)

    try:
        print(f"🔍 Searching: {query}")
        
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]

        print(f"✅ Found: {info['title']}")
        
        data["now_playing"] = info
        data["start_time"] = time.time()
        data["duration"] = info.get("duration", 0)

        # Cek lagi sebelum play
        if not voice_client.is_connected():
            print("❌ Lost voice connection before playing")
            embed = discord.Embed(
                title="❌ Error",
                description="Koneksi voice terputus",
                color=discord.Color.red()
            )
            await channel.send(embed=embed)
            return

        # Gunakan FFmpeg path yang ditemukan
        if FFMPEG_PATH:
            source = discord.FFmpegPCMAudio(
                info['url'],
                executable=FFMPEG_PATH,
                **FFMPEG_OPTIONS
            )
        else:
            source = discord.FFmpegPCMAudio(
                info['url'],
                **FFMPEG_OPTIONS
            )

        def after_playing(error):
            if error:
                print(f"❌ Player error: {error}")
            bot.loop.create_task(play_next(guild, voice_client, channel))

        voice_client.play(source, after=after_playing)

        # Buat embed Now Playing dengan UI controls
        loop_mode = get_loop_mode(guild.id)
        embed = create_now_playing_embed(info, 0, data["duration"], loop_mode)
        view = PlayerUI(guild, get_loop_mode, set_loop_mode)
        
        await channel.send(embed=embed, view=view)
        print(f"🎵 Playing: {info['title']}")
    
    except Exception as e:
        print(f"❌ Error playing: {e}")
        embed = discord.Embed(
            title="❌ Error",
            description=f"Gagal memutar lagu: {str(e)}",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)
        
        # Coba lagu berikutnya
        if not data["queue"].empty():
            await play_next(guild, voice_client, channel)

@bot.event
async def on_ready():
    """Event ketika bot online"""
    try:
        synced = await bot.tree.sync()
        print(f"✅ Bot online: {bot.user}")
        print(f"✅ Synced {len(synced)} slash commands")
        
        # Set bot activity
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="🎵 /play"
            )
        )
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
@bot.tree.command(name="play", description="🎵 Play music from YouTube or Spotify")
async def play(interaction: discord.Interaction, query: str):
    """Command untuk memutar musik dengan UI yang menarik"""
    await interaction.response.defer()
    
    guild = interaction.guild

    # Cek user di voice channel
    if not interaction.user.voice:
        embed = discord.Embed(
            title="❌ Error",
            description="Kamu harus join voice channel terlebih dahulu!",
            color=discord.Color.red()
        )
        return await interaction.followup.send(embed=embed)

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
            
            await asyncio.sleep(1)  # Tunggu koneksi stabil
        except Exception as e:
            print(f"❌ Error connecting: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description=f"Gagal join channel: {str(e)}",
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed)

    data = get_guild_data(guild.id)

    # Handle Spotify Track
    if "open.spotify.com/track" in query:
        spotify_query = get_track_query(query)
        if not spotify_query:
            embed = discord.Embed(
                title="❌ Error",
                description="Gagal mengambil info dari Spotify",
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed)
        query = spotify_query
        print(f"🎵 Spotify track converted: {query}")

    # Handle Spotify Playlist
    elif "open.spotify.com/playlist" in query:
        embed = discord.Embed(
            title="⏳ Loading Playlist",
            description="Mengambil lagu dari Spotify...",
            color=discord.Color.blue()
        )
        msg = await interaction.followup.send(embed=embed)
        
        tracks = get_playlist_queries(query)
        if not tracks:
            embed = discord.Embed(
                title="❌ Error",
                description="Gagal mengambil playlist dari Spotify",
                color=discord.Color.red()
            )
            return await msg.edit(embed=embed)
        
        for q in tracks:
            await data["queue"].put(q)
        
        embed = discord.Embed(
            title="✅ Playlist Added",
            description=f"**{len(tracks)} lagu** ditambahkan ke queue",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", 
                         icon_url=interaction.user.display_avatar.url)
        await msg.edit(embed=embed)
        
        print(f"📀 Added {len(tracks)} tracks from Spotify playlist")
        
        if not vc.is_playing() and vc.is_connected():
            await play_next(guild, vc, interaction.channel)
        return

    # Tambahkan ke queue
    await data["queue"].put(query)
    
    embed = discord.Embed(
        title="✅ Added to Queue",
        description=f"**{query}**",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Requested by {interaction.user.display_name}",
                     icon_url=interaction.user.display_avatar.url)
    await interaction.followup.send(embed=embed)

    # Play jika sedang tidak playing dan sudah connected
    if not vc.is_playing() and vc.is_connected():
        await play_next(guild, vc, interaction.channel)
    elif not vc.is_connected():
        embed = discord.Embed(
            title="❌ Error",
            description="Bot tidak terhubung ke voice channel",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

# ⏭️ COMMAND: SKIP
@bot.tree.command(name="skip", description="⏭️ Skip current song")
async def skip(interaction: discord.Interaction):
    """Skip lagu yang sedang diputar"""
    vc = interaction.guild.voice_client
    
    if not vc:
        embed = discord.Embed(
            title="❌ Error",
            description="Bot tidak sedang di voice channel",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)
    
    if vc.is_playing():
        vc.stop()
        embed = discord.Embed(
            title="⏭️ Skipped",
            description="Lagu di-skip!",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Error",
            description="Tidak ada lagu yang sedang diputar",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

# ⏸️ COMMAND: PAUSE
@bot.tree.command(name="pause", description="⏸️ Pause current song")
async def pause(interaction: discord.Interaction):
    """Pause lagu"""
    vc = interaction.guild.voice_client
    
    if vc and vc.is_playing():
        vc.pause()
        embed = discord.Embed(
            title="⏸️ Paused",
            description="Musik di-pause",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Error",
            description="Tidak ada lagu yang sedang diputar",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

# ▶️ COMMAND: RESUME
@bot.tree.command(name="resume", description="▶️ Resume paused song")
async def resume(interaction: discord.Interaction):
    """Resume lagu yang di-pause"""
    vc = interaction.guild.voice_client
    
    if vc and vc.is_paused():
        vc.resume()
        embed = discord.Embed(
            title="▶️ Resumed",
            description="Musik dilanjutkan",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Error",
            description="Tidak ada lagu yang di-pause",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

# ⏹️ COMMAND: STOP
@bot.tree.command(name="stop", description="⏹️ Stop music and clear queue")
async def stop(interaction: discord.Interaction):
    """Stop musik dan clear queue"""
    vc = interaction.guild.voice_client
    
    if not vc:
        embed = discord.Embed(
            title="❌ Error",
            description="Bot tidak sedang di voice channel",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)
    
    data = get_guild_data(interaction.guild.id)
    
    # Clear queue
    while not data["queue"].empty():
        await data["queue"].get()
    
    data["now_playing"] = None
    
    if vc.is_playing():
        vc.stop()
    
    await vc.disconnect()
    
    embed = discord.Embed(
        title="⏹️ Stopped",
        description="Musik dihentikan dan bot disconnect",
        color=discord.Color.dark_gray()
    )
    await interaction.response.send_message(embed=embed)

# 📜 COMMAND: QUEUE
@bot.tree.command(name="queue", description="📜 Show current queue")
async def show_queue(interaction: discord.Interaction):
    """Menampilkan daftar queue dengan embed"""
    data = get_guild_data(interaction.guild.id)
    
    if data["queue"].empty() and not data["now_playing"]:
        embed = discord.Embed(
            title="📜 Queue",
            description="Queue kosong",
            color=discord.Color.blue()
        )
        return await interaction.response.send_message(embed=embed)

    loop_mode = get_loop_mode(interaction.guild.id)
    embed = create_queue_embed(data, loop_mode)
    
    # Jika queue panjang, gunakan paginator
    items = list(data["queue"]._queue)
    if len(items) > 10:
        paginator = QueuePaginator(items)
        await interaction.response.send_message(embed=paginator.get_page_content(), view=paginator)
    else:
        await interaction.response.send_message(embed=embed)

# 🎧 COMMAND: NOW PLAYING
@bot.tree.command(name="nowplaying", description="🎧 Show currently playing song")
async def nowplaying(interaction: discord.Interaction):
    """Menampilkan lagu yang sedang diputar dengan embed menarik"""
    data = get_guild_data(interaction.guild.id)

    if not data["now_playing"]:
        embed = discord.Embed(
            title="❌ Error",
            description="Tidak ada lagu yang sedang diputar",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    elapsed = int(time.time() - data["start_time"])
    loop_mode = get_loop_mode(interaction.guild.id)
    
    embed = create_now_playing_embed(data["now_playing"], elapsed, data["duration"], loop_mode)
    view = PlayerUI(interaction.guild, get_loop_mode, set_loop_mode)
    
    await interaction.response.send_message(embed=embed, view=view)

# 🔗 COMMAND: JOIN
@bot.tree.command(name="join", description="🔗 Join your voice channel")
async def join(interaction: discord.Interaction):
    """Join voice channel user"""
    if not interaction.user.voice:
        embed = discord.Embed(
            title="❌ Error",
            description="Kamu belum di voice channel!",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)
    
    vc = interaction.guild.voice_client
    
    if vc:
        await vc.move_to(interaction.user.voice.channel)
        embed = discord.Embed(
            title="✅ Moved",
            description=f"Pindah ke **{interaction.user.voice.channel.name}**",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    else:
        try:
            await interaction.user.voice.channel.connect()
            embed = discord.Embed(
                title="✅ Joined",
                description=f"Bergabung ke **{interaction.user.voice.channel.name}**",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Gagal join: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

# 🚪 COMMAND: LEAVE
@bot.tree.command(name="leave", description="🚪 Leave voice channel")
async def leave(interaction: discord.Interaction):
    """Leave voice channel"""
    vc = interaction.guild.voice_client
    
    if vc:
        await vc.disconnect()
        embed = discord.Embed(
            title="👋 Left",
            description="Bot keluar dari voice channel",
            color=discord.Color.dark_gray()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Error",
            description="Bot tidak sedang di voice channel",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

# 🔄 COMMAND: LOOP
@bot.tree.command(name="loop", description="🔄 Set loop mode (off/song/queue)")
async def loop(interaction: discord.Interaction, mode: str):
    """Set loop mode"""
    mode = mode.lower()

    if mode not in ["off", "song", "queue"]:
        embed = discord.Embed(
            title="❌ Error",
            description="Pilih mode: **off** | **song** | **queue**",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    set_loop_mode(interaction.guild.id, mode)
    
    mode_text = {
        "off": ("🔁 Loop: OFF", "Loop dinonaktifkan"),
        "song": ("🔂 Loop: SONG", "Loop lagu saat ini"),
        "queue": ("🔁 Loop: QUEUE", "Loop seluruh queue")
    }
    
    title, desc = mode_text[mode]
    embed = discord.Embed(
        title=title,
        description=desc,
        color=discord.Color.blue()
    )
    
    await interaction.response.send_message(embed=embed)

# 🗑️ COMMAND: REMOVE
@bot.tree.command(name="remove", description="🗑️ Remove song from queue")
async def remove(interaction: discord.Interaction, index: int):
    """Remove lagu dari queue"""
    data = get_guild_data(interaction.guild.id)
    q = list(data["queue"]._queue)

    if index < 1 or index > len(q):
        embed = discord.Embed(
            title="❌ Error",
            description=f"Index tidak valid! (1-{len(q)})",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    removed = q.pop(index - 1)
    data["queue"] = asyncio.Queue()
    for item in q:
        await data["queue"].put(item)

    embed = discord.Embed(
        title="🗑️ Removed",
        description=f"**{removed}**",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)

# 🔊 COMMAND: VOLUME
@bot.tree.command(name="volume", description="🔊 Set volume (1-100)")
async def volume(interaction: discord.Interaction, level: int):
    """Set volume"""
    vc = interaction.guild.voice_client
    
    if not vc or not vc.source:
        embed = discord.Embed(
            title="❌ Error",
            description="Tidak ada lagu yang sedang diputar",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)
    
    if level < 1 or level > 100:
        embed = discord.Embed(
            title="❌ Error",
            description="Volume harus antara 1-100",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    vc.source.volume = level / 100
    
    # Volume emoji based on level
    if level <= 30:
        emoji = "🔈"
    elif level <= 70:
        emoji = "🔉"
    else:
        emoji = "🔊"
    
    embed = discord.Embed(
        title=f"{emoji} Volume Set",
        description=f"Volume diatur ke **{level}%**",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

# 🔧 COMMAND: DEBUG
@bot.tree.command(name="debug", description="🔧 Show debug info")
async def debug(interaction: discord.Interaction):
    """Menampilkan info debug dengan embed"""
    vc = interaction.guild.voice_client
    data = get_guild_data(interaction.guild.id)
    
    embed = discord.Embed(
        title="🔧 Debug Info",
        color=discord.Color.blue()
    )
    
    # FFmpeg status
    ffmpeg_status = "✅ Found" if FFMPEG_PATH else "❌ Not found"
    embed.add_field(name="FFmpeg", value=ffmpeg_status, inline=True)
    
    # Voice status
    voice_status = "✅ Connected" if vc else "❌ Not connected"
    embed.add_field(name="Voice Client", value=voice_status, inline=True)
    
    # Playing status
    playing_status = "✅ Yes" if vc and vc.is_playing() else "❌ No"
    embed.add_field(name="Is Playing", value=playing_status, inline=True)
    
    # Paused status
    paused_status = "✅ Yes" if vc and vc.is_paused() else "❌ No"
    embed.add_field(name="Is Paused", value=paused_status, inline=True)
    
    # Queue size
    queue_size = data["queue"].qsize()
    embed.add_field(name="Queue Size", value=f"{queue_size} songs", inline=True)
    
    # Loop mode
    loop_mode = get_loop_mode(interaction.guild.id)
    embed.add_field(name="Loop Mode", value=loop_mode.upper(), inline=True)
    
    if FFMPEG_PATH:
        embed.set_footer(text=f"FFmpeg: {FFMPEG_PATH}")
    
    await interaction.response.send_message(embed=embed)

# 📝 COMMAND: HELP
@bot.tree.command(name="help", description="📝 Show all commands")
async def help_command(interaction: discord.Interaction):
    """Menampilkan daftar semua command"""
    embed = discord.Embed(
        title="🎵 Music Bot Commands",
        description="Daftar semua command yang tersedia",
        color=discord.Color.blue()
    )
    
    commands_list = [
        ("🎵 /play `<query>`", "Putar musik dari YouTube/Spotify"),
        ("⏸️ /pause", "Pause lagu saat ini"),
        ("▶️ /resume", "Resume lagu yang di-pause"),
        ("⏭️ /skip", "Skip lagu saat ini"),
        ("⏹️ /stop", "Stop musik dan clear queue"),
        ("📜 /queue", "Tampilkan daftar queue"),
        ("🎧 /nowplaying", "Info lagu yang sedang diputar"),
        ("🔄 /loop `<mode>`", "Set loop (off/song/queue)"),
        ("🗑️ /remove `<index>`", "Hapus lagu dari queue"),
        ("🔊 /volume `<1-100>`", "Atur volume"),
        ("🔗 /join", "Join voice channel kamu"),
        ("🚪 /leave", "Keluar dari voice channel"),
        ("🔧 /debug", "Info debugging"),
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="Created with ❤️ | Use buttons for easy control!")
    
    await interaction.response.send_message(embed=embed)

# 🚀 JALANKAN BOT
if __name__ == "__main__":
    TOKEN = "YOUR_BOT_TOKEN_HERE"  # ⚠️ GANTI INI DENGAN TOKEN BOT KAMU!
    
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ GANTI TOKEN BOT DI BARIS PALING BAWAH!")
    else:
        bot.run(TOKEN)