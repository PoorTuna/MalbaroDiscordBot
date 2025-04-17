import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

logger = logging.getLogger(__name__)

def setup_scheduler(bot):
    """
    Set up the scheduler for daily propaganda poster generation.
    
    Args:
        bot: The Discord bot instance
    """
    scheduler = AsyncIOScheduler()
    
    # Get the configured time from the bot's propaganda_config
    hour = bot.propaganda_config.hour
    minute = bot.propaganda_config.minute
    
    # Schedule the daily poster generation task
    scheduler.add_job(
        generate_daily_poster,
        CronTrigger(hour=hour, minute=minute),  # Run at the configured time
        args=[bot],
        id='daily_propaganda',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info(f"Scheduled daily propaganda poster generation for {hour:02d}:{minute:02d} UTC")

async def generate_daily_poster(bot):
    """
    Generate and post the daily propaganda poster.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Generating daily propaganda poster")
    
    # Check if a channel is configured
    if not bot.propaganda_config.channel_id:
        logger.warning("No channel configured for daily propaganda poster")
        return
    
    # Get the channel to post to
    channel = bot.get_channel(bot.propaganda_config.channel_id)
    if not channel:
        logger.error(f"Could not find channel with ID {bot.propaganda_config.channel_id}")
        return
    
    # Generate and post the propaganda poster
    try:
        await bot.generate_and_post_poster(channel)
        logger.info(f"Successfully posted daily propaganda poster to #{channel.name}")
    except Exception as e:
        logger.error(f"Error posting daily propaganda poster: {e}", exc_info=True)
