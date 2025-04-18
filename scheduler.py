
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

def setup_scheduler(bot):
    """
    Set up the scheduler for daily propaganda poster generation.
    
    Args:
        bot: The Discord bot instance
    """
    scheduler = AsyncIOScheduler()
    
    # Get the configured time and timezone from the bot's propaganda_config
    hour = bot.propaganda_config.hour
    minute = bot.propaganda_config.minute
    timezone = pytz.timezone(bot.propaganda_config.timezone)
    
    # Schedule the poster generation task every 30 seconds
    scheduler.add_job(
        generate_daily_poster,
        'interval',
        seconds=30,
        args=[bot],
        id='propaganda_generator',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Scheduled propaganda poster generation to run every 30 seconds")

async def generate_daily_poster(bot):
    """
    Generate and post the daily propaganda poster.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Generating daily propaganda poster")
    
    if not bot.propaganda_config.channel_id:
        logger.warning("No channel configured for daily propaganda poster")
        return
    
    channel = bot.get_channel(bot.propaganda_config.channel_id)
    if not channel:
        logger.error(f"Could not find channel with ID {bot.propaganda_config.channel_id}")
        return
    
    try:
        await bot.generate_and_post_poster(channel)
        logger.info(f"Successfully posted daily propaganda poster to #{channel.name}")
    except Exception as e:
        logger.error(f"Error posting daily propaganda poster: {e}", exc_info=True)
