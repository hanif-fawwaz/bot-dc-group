import discord
from discord.ui import Button, View
import time


class PlayerUI(View):
    """UI untuk kontrol player musik dengan tombol interaktif"""
    
    def __init__(self, guild, get_loop_mode, set_loop_mode):
        super().__init__(timeout=None)  # UI tidak expire
        self.guild = guild
        self.get_loop_mode = get_loop_mode
        self.set_loop_mode = set_loop_mode
        
        # Update button loop sesuai mode saat ini
        self.update_loop_button()
    
    def update_loop_button(self):
        """Update emoji loop button sesuai mode"""
        mode = self.get_loop_mode(self.guild.id)
        loop_emojis = {
            "off": "🔁",
            "song": "🔂",
            "queue": "🔁"
        }
        
        # Update button loop
        for item in self.children:
            if item.custom_id == "loop":
                item.emoji = loop_emojis.get(mode, "🔁")
                item.style = discord.ButtonStyle.green if mode != "off" else discord.ButtonStyle.secondary
    
    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.primary, custom_id="playpause")
    async def play_pause_button(self, interaction: discord.Interaction, button: Button):
        """Tombol Play/Pause"""
        vc = self.guild.voice_client
        
        if not vc:
            return await interaction.response.send_message("❌ Bot tidak di voice channel", ephemeral=True)
        
        if vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ **Paused**", ephemeral=True)
        elif vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ **Resumed**", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Tidak ada lagu", ephemeral=True)
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.primary, custom_id="skip")
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        """Tombol Skip"""
        vc = self.guild.voice_client
        
        if not vc or not vc.is_playing():
            return await interaction.response.send_message("❌ Tidak ada lagu yang sedang diputar", ephemeral=True)
        
        vc.stop()
        await interaction.response.send_message("⏭️ **Skipped!**", ephemeral=True)
    
    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger, custom_id="stop")
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        """Tombol Stop"""
        vc = self.guild.voice_client
        
        if not vc:
            return await interaction.response.send_message("❌ Bot tidak di voice channel", ephemeral=True)
        
        # Import guild_data from main bot
        from __main__ import guild_data
        
        if self.guild.id in guild_data:
            data = guild_data[self.guild.id]
            # Clear queue
            while not data["queue"].empty():
                await data["queue"].get()
            data["now_playing"] = None
        
        if vc.is_playing():
            vc.stop()
        
        await vc.disconnect()
        await interaction.response.send_message("⏹️ **Stopped and disconnected**", ephemeral=True)
    
    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.secondary, custom_id="loop")
    async def loop_button(self, interaction: discord.Interaction, button: Button):
        """Tombol Loop - cycle through modes"""
        current_mode = self.get_loop_mode(self.guild.id)
        
        # Cycle: off -> song -> queue -> off
        modes = ["off", "song", "queue"]
        next_mode = modes[(modes.index(current_mode) + 1) % len(modes)]
        
        self.set_loop_mode(self.guild.id, next_mode)
        
        mode_text = {
            "off": "🔁 Loop: **OFF**",
            "song": "🔂 Loop: **CURRENT SONG**",
            "queue": "🔁 Loop: **ENTIRE QUEUE**"
        }
        
        # Update button appearance
        self.update_loop_button()
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(mode_text[next_mode], ephemeral=True)
    
    @discord.ui.button(emoji="📜", style=discord.ButtonStyle.secondary, custom_id="queue")
    async def queue_button(self, interaction: discord.Interaction, button: Button):
        """Tombol Queue - tampilkan daftar queue"""
        from __main__ import guild_data
        
        if self.guild.id not in guild_data:
            return await interaction.response.send_message("📜 Queue kosong", ephemeral=True)
        
        data = guild_data[self.guild.id]
        
        if data["queue"].empty():
            return await interaction.response.send_message("📜 Queue kosong", ephemeral=True)
        
        items = list(data["queue"]._queue)
        
        # Create embed untuk queue
        embed = discord.Embed(
            title="📜 Current Queue",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        # Show now playing
        if data["now_playing"]:
            embed.add_field(
                name="🎵 Now Playing",
                value=f"**{data['now_playing']['title']}**",
                inline=False
            )
        
        # Show next songs
        if items:
            queue_text = "\n".join([f"`{i+1}.` {self._format_title(q)}" for i, q in enumerate(items[:10])])
            
            if len(items) > 10:
                queue_text += f"\n\n*... and {len(items) - 10} more songs*"
            
            embed.add_field(
                name=f"🎶 Up Next ({len(items)} songs)",
                value=queue_text,
                inline=False
            )
        
        loop_mode = self.get_loop_mode(self.guild.id)
        loop_icons = {"off": "🔁 Off", "song": "🔂 Song", "queue": "🔁 Queue"}
        embed.set_footer(text=f"Loop: {loop_icons.get(loop_mode, 'Off')}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _format_title(self, query):
        """Format title untuk tampilan yang lebih rapi"""
        if "http" in query:
            # Jika URL, coba ambil bagian akhir
            parts = query.split("/")[-1].split("?")[0]
            return parts[:50] + "..." if len(parts) > 50 else parts
        return query[:50] + "..." if len(query) > 50 else query


def create_now_playing_embed(info, elapsed, duration, loop_mode="off"):
    """Membuat embed untuk Now Playing dengan progress bar"""
    
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
    
    # Buat embed
    embed = discord.Embed(
        title="🎵 Now Playing",
        description=f"**{info['title']}**",
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    
    # Thumbnail dari YouTube
    if 'thumbnail' in info:
        embed.set_thumbnail(url=info['thumbnail'])
    
    # Progress bar
    embed.add_field(
        name="⏱️ Progress",
        value=f"`{bar}` {elapsed_str} / {duration_str}",
        inline=False
    )
    
    # Info tambahan
    if 'uploader' in info:
        embed.add_field(name="👤 Uploader", value=info['uploader'], inline=True)
    
    if 'view_count' in info:
        views = f"{info['view_count']:,}"
        embed.add_field(name="👁️ Views", value=views, inline=True)
    
    # Loop mode indicator
    loop_icons = {
        "off": "🔁 Off",
        "song": "🔂 Song",
        "queue": "🔁 Queue"
    }
    embed.set_footer(text=f"Loop: {loop_icons.get(loop_mode, 'Off')}")
    
    return embed


def create_queue_embed(data, loop_mode="off"):
    """Membuat embed untuk daftar queue"""
    
    embed = discord.Embed(
        title="📜 Music Queue",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    
    # Now playing
    if data["now_playing"]:
        elapsed = int(time.time() - data["start_time"])
        duration = data["duration"]
        
        elapsed_str = f"{elapsed // 60}:{elapsed % 60:02d}"
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "Live"
        
        embed.add_field(
            name="🎵 Now Playing",
            value=f"**{data['now_playing']['title']}**\n`{elapsed_str} / {duration_str}`",
            inline=False
        )
    
    # Queue list
    if not data["queue"].empty():
        items = list(data["queue"]._queue)
        
        # Ambil 10 lagu pertama
        queue_text = ""
        for i, item in enumerate(items[:10], 1):
            # Format judul
            if isinstance(item, dict):
                title = item.get('title', 'Unknown')
            else:
                title = str(item)[:50]
            
            queue_text += f"`{i}.` {title}\n"
        
        if len(items) > 10:
            queue_text += f"\n*... and {len(items) - 10} more songs*"
        
        embed.add_field(
            name=f"🎶 Up Next ({len(items)} songs)",
            value=queue_text,
            inline=False
        )
    else:
        embed.add_field(
            name="🎶 Up Next",
            value="*Queue is empty*",
            inline=False
        )
    
    # Loop mode
    loop_icons = {
        "off": "🔁 Off",
        "song": "🔂 Song",
        "queue": "🔁 Queue"
    }
    embed.set_footer(text=f"Loop: {loop_icons.get(loop_mode, 'Off')}")
    
    return embed


class QueuePaginator(View):
    """Paginator untuk queue yang panjang"""
    
    def __init__(self, items, per_page=10):
        super().__init__(timeout=60)
        self.items = items
        self.per_page = per_page
        self.current_page = 0
        self.max_page = (len(items) - 1) // per_page
        
        # Disable buttons jika hanya 1 halaman
        if self.max_page == 0:
            self.previous_button.disabled = True
            self.next_button.disabled = True
    
    def get_page_content(self):
        """Mendapatkan konten halaman saat ini"""
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_items = self.items[start:end]
        
        embed = discord.Embed(
            title=f"📜 Queue - Page {self.current_page + 1}/{self.max_page + 1}",
            color=discord.Color.blue()
        )
        
        queue_text = "\n".join([
            f"`{start + i + 1}.` {item[:50]}"
            for i, item in enumerate(page_items)
        ])
        
        embed.description = queue_text
        embed.set_footer(text=f"Total: {len(self.items)} songs")
        
        return embed
    
    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.primary, custom_id="previous")
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        """Halaman sebelumnya"""
        if self.current_page > 0:
            self.current_page -= 1
            
            # Update button states
            self.next_button.disabled = False
            if self.current_page == 0:
                self.previous_button.disabled = True
            
            embed = self.get_page_content()
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.primary, custom_id="next")
    async def next_button(self, interaction: discord.Interaction, button: Button):
        """Halaman berikutnya"""
        if self.current_page < self.max_page:
            self.current_page += 1
            
            # Update button states
            self.previous_button.disabled = False
            if self.current_page == self.max_page:
                self.next_button.disabled = True
            
            embed = self.get_page_content()
            await interaction.response.edit_message(embed=embed, view=self)