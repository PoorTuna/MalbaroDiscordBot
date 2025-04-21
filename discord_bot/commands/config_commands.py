import logging

import pytz
from discord import Interaction, Embed, Color

from discord_bot.bot import PropagandaBot
from discord_bot.scheduler import setup_scheduler

logger = logging.getLogger(__name__)


def register_config_commands(bot: PropagandaBot):
    config = bot.propaganda_config

    @bot.tree.command(
        name="set_channel",
        description="Set the current channel for propaganda posters")
    async def set_channel(interaction: Interaction):
        config.propaganda_scheduler[
            "poster_output_channel_id"] = interaction.channel_id
        await interaction.response.send_message(
            "Channel set for propaganda posters.")

    @bot.tree.command(
        name="set_voice_channel",
        description="Set the voice channel for music playback")
    async def set_voice_channel(interaction: Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message(
                "You must be in a voice channel to set it!")
            return
        voice_channel_id = interaction.user.voice.channel.id
        config.voice_channel_id = voice_channel_id
        config.save_config()
        await interaction.response.send_message(
            f"Voice channel set to: {interaction.user.voice.channel.name}")

    @bot.tree.command(name="set_time",
                      description="Set the time for daily posts (HH:MM)")
    async def set_time(interaction: Interaction, time: str):
        try:
            hour, minute = map(int, time.split(':'))
            if 0 <= hour < 24 and 0 <= minute < 60:
                config.propaganda_scheduler["time"][
                    "hour"] = hour
                config.propaganda_scheduler["time"][
                    "minute"] = minute
                bot.propaganda_config.save_config()
                await interaction.response.send_message(
                    f"Post time set to {time}")
            else:
                await interaction.response.send_message(
                    "Invalid time format. Use HH:MM (24-hour format)")
        except ValueError:
            await interaction.response.send_message(
                "Invalid time format. Use HH:MM (e.g., 15:30)")

    @bot.tree.command(name="set_timezone", description="Set the timezone")
    async def set_timezone(interaction: Interaction,
                           timezone: str):
        try:
            pytz.timezone(timezone)
            config.timezone = timezone
            config.save_config()
            setup_scheduler(bot)
            await interaction.response.send_message(
                f"Timezone set to: {timezone}")
        except Exception:
            await interaction.response.send_message(
                "Invalid timezone. Example: US/Eastern, Europe/London")

    @bot.tree.command(name="show_config",
                      description="Show current configuration")
    async def show_config(interaction: Interaction):
        channel_mention = f"<#{config.propaganda_scheduler['poster_output_channel_id']}>" if config.propaganda_scheduler.get(
            'poster_output_channel_id') else "Not set"

        # Truncate text prompt if too long
        text_prompt = config.text_prompt
        if len(text_prompt) > 900:
            text_prompt = text_prompt[:897] + "..."

        embed = Embed(title="Propaganda Poster Configuration",
                      color=Color.orange())
        embed.add_field(name="Channel", value=channel_mention, inline=True)
        embed.add_field(
            name="Post Time",
            value=
            f"{config.propaganda_scheduler['time']['hour']:02d}:{config.propaganda_scheduler['time']['minute']:02d} {config.propaganda_scheduler['timezone']}",
            inline=True)
        embed.add_field(name="Text Prompt",
                        value=text_prompt,
                        inline=False)

        await interaction.response.send_message(embed=embed)
