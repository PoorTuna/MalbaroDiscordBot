import asyncio
import logging
from datetime import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from discord_bot.content_generation.generate_poster import generate_propaganda_poster
from discord_bot.models.scheduler_state import get_scheduler_state

logger = logging.getLogger(__name__)


def setup_scheduler(bot, api_tokens: list[str]):
    current_scheduler_state = get_scheduler_state()

    # Shutdown existing scheduler if it exists
    try:
        if current_scheduler_state.current_scheduler:
            current_scheduler_state.current_scheduler.shutdown(wait=False)
    except Exception as e:
        logger.error(f"Error shutting down existing scheduler: {e}")

    scheduler = AsyncIOScheduler()
    current_scheduler_state.current_scheduler = scheduler

    # Get the configured time and timezone from the bot's propaganda_config
    hour = bot.propaganda_config.propaganda_scheduler.time.hour
    minute = bot.propaganda_config.propaganda_scheduler.time.minute
    timezone = pytz.timezone(bot.propaganda_config.propaganda_scheduler.timezone)

    # Check if we missed today's run within last 5 minutes
    now = datetime.now(timezone)
    scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    time_diff = now - scheduled_time

    if 0 <= time_diff.total_seconds() <= 300:  # Within 5 minutes after scheduled time
        logger.info("Missed recent schedule - running now")
        asyncio.create_task(generate_daily_content(bot, api_tokens))

    # Schedule the daily content generation task
    scheduler.configure(timezone=timezone)  # Set scheduler default timezone
    scheduler.add_job(
        generate_daily_content,
        CronTrigger(hour=hour, minute=minute, timezone=timezone),
        args=[bot, api_tokens],
        id='daily_content',
        replace_existing=True,
        misfire_grace_time=600,  # Allow 10 minutes grace period
        coalesce=True,  # Only run once even if multiple executions are missed
        max_instances=1  # Ensure only one instance runs at a time
    )

    # Start the scheduler
    scheduler.start()
    logger.info(f"Scheduled daily propaganda poster generation for {hour:02d}:{minute:02d} {timezone}")


async def generate_daily_content(bot, api_tokens: list[str]):
    current_time = datetime.now(pytz.timezone(bot.propaganda_config.propaganda_scheduler.timezone))
    logger.info(f"Scheduler triggered at {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logger.info("Generating daily propaganda poster and playing music")

    channel_id = bot.propaganda_config.propaganda_scheduler.poster_output_channel_id
    if not channel_id:
        logger.warning("No channel configured for daily propaganda poster")
        return

    channel = bot.get_channel(channel_id)
    if not channel:
        logger.error(f"Could not find channel with ID {channel_id}")
        return

    try:
        # Generate and post the propaganda poster
        await generate_propaganda_poster(bot, api_tokens, channel)
        logger.info(f"Successfully posted daily propaganda poster to #{channel.name}")

        # Join and play a random propaganda speech
        voice_channel_id = bot.propaganda_config.propaganda_scheduler.voice_channel_id
        playlist_url = bot.propaganda_config.propaganda_scheduler.youtube_playlist_url
        await play_random_propaganda_speech(bot, voice_channel_id, playlist_url)

    except Exception as e:
        error_msg = f"Error in daily content generation: {e}"
        logger.error(error_msg, exc_info=True)
        await channel.send(f"⚠️ {error_msg}")


async def play_random_propaganda_speech(bot, voice_channel_id, playlist_url):
    voice_channel = bot.get_channel(voice_channel_id)
    if voice_channel and playlist_url:
        try:
            # Connect to voice channel and wait for it to be ready
            voice_client = await voice_channel.connect()
            await asyncio.sleep(2)  # Wait for voice client to stabilize
            bot.music_player.voice_clients[voice_channel.guild.id] = voice_client

            # Play random song from playlist
            await bot.music_player.join_and_play(None, playlist_url, force_voice_channel=True)
            logger.info(f"Successfully started playing music in voice channel {voice_channel.name}")

            # Disconnect after playing
            if voice_channel.guild.id in bot.music_player.voice_clients:
                await bot.music_player.voice_clients[voice_channel.guild.id].disconnect()
                del bot.music_player.voice_clients[voice_channel.guild.id]
        except Exception as e:
            logger.error(f"Error playing music: {e}")
    else:
        if not voice_channel:
            logger.error(f"Could not find voice channel with ID {voice_channel_id}")
        if not playlist_url:
            logger.error("No playlist URL configured")
