from logging import getLogger

logger = getLogger(__name__)

async def handle_cs2_start(steam_monitor):
    """Handle when a user starts playing CS2."""
    try:
        voice_channel_id = steam_monitor.propaganda_bot.propaganda_config.propaganda_scheduler[
            "voice_channel_id"]
        video_url = steam_monitor.propaganda_bot.propaganda_config.propaganda_scheduler[
            "cs2_alert_video_url"]

        if voice_channel_id and video_url:
            if voice_channel := steam_monitor.propaganda_bot.get_channel(voice_channel_id):
                logger.info(
                    f"Playing CS2 alert video in channel {voice_channel.name}"
                )
                # Connect to voice channel first
                voice_client = await voice_channel.connect()
                steam_monitor.propaganda_bot.music_player.voice_clients[
                    voice_channel.guild.id] = voice_client

                # Play the alert
                await steam_monitor.propaganda_bot.music_player.join_and_play(
                    None, video_url, force_voice_channel=True)

                # Cleanup after playing
                if voice_channel.guild.id in steam_monitor.propaganda_bot.music_player.voice_clients:
                    await steam_monitor.propaganda_bot.music_player.voice_clients[
                        voice_channel.guild.id].disconnect()
                    del steam_monitor.propaganda_bot.music_player.voice_clients[
                        voice_channel.guild.id]
            else:
                logger.warning(
                    f"Could not find voice channel with ID {voice_channel_id}"
                )
        else:
            logger.warning(
                "Voice channel or CS2 alert video URL not configured")
    except Exception as e:
        logger.error(f"Error playing CS2 alert: {e}")
        # Ensure cleanup on error
        try:
            if voice_channel and voice_channel.guild.id in steam_monitor.propaganda_bot.music_player.voice_clients:
                await steam_monitor.propaganda_bot.music_player.voice_clients[
                    voice_channel.guild.id].disconnect()
                del steam_monitor.propaganda_bot.music_player.voice_clients[
                    voice_channel.guild.id]
        except Exception as e:
            logger.error(f"Error deleting voice client: {e}")
