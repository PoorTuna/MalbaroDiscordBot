from discord import Interaction

from discord_bot.bot import PropagandaBot
from discord_bot.commands.config_commands import logger


def register_music_player_commands(bot: PropagandaBot):
    music_player = bot.music_player

    @bot.tree.command(
        name="play",
        description="Play a YouTube URL in your voice channel")
    async def play(interaction: Interaction, url: str):
        if not interaction.user or not interaction.user.voice:
            await interaction.response.send_message(
                "You must be in a voice channel to use this command!")
            return

        try:
            await interaction.response.defer()
            await music_player.join_and_play(interaction, url)
        except Exception as e:
            await interaction.followup.send(
                f"Error playing music: {str(e)}")
            logger.error(f"Error in play command: {e}", exc_info=True)

    @bot.tree.command(name="leave", description="Leave the voice channel")
    async def leave(interaction: Interaction):
        if interaction.guild_id not in music_player.voice_clients:
            await interaction.response.send_message(
                "I'm not in a voice channel!")
            return

        voice_client = music_player.voice_clients[
            interaction.guild_id]
        await voice_client.disconnect()
        music_player.voice_clients.pop(interaction.guild_id)

        await interaction.response.send_message(
            "Left the voice channel!")
