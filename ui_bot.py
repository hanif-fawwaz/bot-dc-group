import discord

# Import fungsi loop dari bot
from typing import Callable

class PlayerUI(discord.ui.View):
    def __init__(self, guild, get_loop_mode: Callable, set_loop_mode: Callable):
        super().__init__(timeout=None)
        self.guild = guild
        self.get_loop_mode = get_loop_mode
        self.set_loop_mode = set_loop_mode

    # ▶️ Resume
    @discord.ui.button(label="Play", style=discord.ButtonStyle.green)
    async def resume_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Resumed", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Tidak paused", ephemeral=True)

    # ⏸ Pause
    @discord.ui.button(label="Pause", style=discord.ButtonStyle.gray)
    async def pause_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Paused", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Tidak playing", ephemeral=True)

    # ⏭ Skip
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.blurple)
    async def skip_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc:
            vc.stop()
            await interaction.response.send_message("⏭️ Skipped", ephemeral=True)

    # 🔁 Loop
    @discord.ui.button(label="Loop", style=discord.ButtonStyle.red)
    async def loop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        mode = self.get_loop_mode(interaction.guild.id)

        if mode == "off":
            self.set_loop_mode(interaction.guild.id, "song")
        elif mode == "song":
            self.set_loop_mode(interaction.guild.id, "queue")
        else:
            self.set_loop_mode(interaction.guild.id, "off")

        await interaction.response.send_message(
            f"🔁 Loop Mode → {self.get_loop_mode(interaction.guild.id)}",
            ephemeral=True
        )

    # ⏹ Stop
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("⏹ Stopped", ephemeral=True)
