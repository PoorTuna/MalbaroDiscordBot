import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

def setup_scheduler(bot):
    """
    Set up the scheduler for daily propaganda poster generation and music.

    Args:
        bot: The Discord bot instance
    """
    global current_scheduler

    # Shutdown existing scheduler if it exists
    try:
        if hasattr(setup_scheduler, 'current_scheduler'):
            setup_scheduler.current_scheduler.shutdown(wait=False)
    except Exception as e:
        logger.error(f"Error shutting down existing scheduler: {e}")

    scheduler = AsyncIOScheduler()
    setup_scheduler.current_scheduler = scheduler

    # Get the configured time and timezone from the bot's propaganda_config
    hour = bot.propaganda_config.hour
    minute = bot.propaganda_config.minute
    timezone = pytz.timezone(bot.propaganda_config.timezone)

    # Check if we missed today's run within last 5 minutes
    now = datetime.now(timezone)
    scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    time_diff = now - scheduled_time
    
    if 0 <= time_diff.total_seconds() <= 300:  # Within 5 minutes after scheduled time
        logger.info("Missed recent schedule - running now")
        asyncio.create_task(generate_daily_content(bot))

    # Schedule the daily content generation task
    scheduler.configure(timezone=timezone)  # Set scheduler default timezone
    scheduler.add_job(
        generate_daily_content,
        CronTrigger(hour=hour, minute=minute, timezone=timezone),
        args=[bot],
        id='daily_content',
        replace_existing=True,
        misfire_grace_time=60,  # Allow 60 seconds grace period
        coalesce=True,  # Only run once even if multiple executions are missed
        max_instances=1  # Ensure only one instance runs at a time
    )

    # Start the scheduler
    scheduler.start()
    logger.info(f"Scheduled daily propaganda poster generation for {hour:02d}:{minute:02d} {timezone}")

async def generate_daily_content(bot):
    """
    Generate and post the daily propaganda poster and play music.

    Args:
        bot: The Discord bot instance
    """
    current_time = datetime.now(pytz.timezone(bot.propaganda_config.timezone))
    logger.info(f"Scheduler triggered at {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logger.info("Generating daily propaganda poster and playing music")

    if not bot.propaganda_config.channel_id:
        logger.warning("No channel configured for daily propaganda poster")
        return

    channel = bot.get_channel(bot.propaganda_config.channel_id)
    if not channel:
        logger.error(f"Could not find channel with ID {bot.propaganda_config.channel_id}")
        return

    try:
        # Generate and post the propaganda poster
        await bot.generate_and_post_poster(channel)
        logger.info(f"Successfully posted daily propaganda poster to #{channel.name}")

        # Get voice channel and playlist URL from config
        voice_channel = bot.get_channel(bot.propaganda_config.voice_channel_id)
        playlist_url = bot.propaganda_config.youtube_playlist_url
        
        if voice_channel and playlist_url:
            try:
                # Connect to voice channel directly
                voice_client = await voice_channel.connect()
                bot.music_player.voice_clients[voice_channel.guild.id] = voice_client
                
                # Play random song from playlist
                await bot.music_player.join_and_play(None, playlist_url, force_voice_channel=True)
                logger.info(f"Successfully started playing music in voice channel {voice_channel.name}")
            except Exception as e:
                logger.error(f"Error playing music: {e}")
        else:
            if not voice_channel:
                logger.error(f"Could not find voice channel with ID {voice_channel_id}")
            if not playlist_url:
                logger.error("No playlist URL configured")

    except Exception as e:
        error_msg = f"Error in daily content generation: {e}"
        logger.error(error_msg, exc_info=True)
        try:
            await channel.send(f"⚠️ {error_msg}")
        except:
            pass

class MockInteraction:
    def __init__(self, text_channel, voice_channel):
        self.channel = text_channel
        self.guild = text_channel.guild
        self.user = text_channel.guild.me
        self.followup = text_channel
        self._voice_channel = voice_channel

    @property
    def voice(self):
        class VoiceState:
            def __init__(self, channel):
                self.channel = channel
        return VoiceState(self._voice_channel)

    async def response(self):
        return self

    async def send(self, *args, **kwargs):
        await self.channel.send(*args, **kwargs)

    async def defer(self):
        pass