import os
import logging
from dotenv import load_dotenv
from bot import PropagandaBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the Discord propaganda poster bot."""
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ['DISCORD_TOKEN', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set them in your .env file or environment")
        return
    
    # Initialize and run the bot
    bot = PropagandaBot()
    try:
        logger.info("Starting Discord propaganda poster bot...")
        bot.run(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        logger.error(f"Error running bot: {e}")

if __name__ == "__main__":
    main()
