import os
from json import load
from logging import getLogger

from discord_bot.bot import PropagandaBot
from discord_bot.commands import register_commands
from discord_bot.models.bot_state import get_bot_state

logger = getLogger(__name__)

bot_state = get_bot_state()


def run_discord_bot(propaganda_bot: PropagandaBot) -> None:
    try:
        if not os.path.exists('tokens_config.json'):
            logger.error(
                "tokens_config.json not found."
            )
            bot_state.status = "Error: No tokens found"
            return

        with open('tokens_config.json', 'r') as f:
            tokens = load(f)

        if not tokens.get('discord_token'):
            logger.error("Discord token not found in config")
            bot_state.status = "Error: Discord token not found in config"
            return

        register_commands(propaganda_bot)
        logger.info("Starting Discord propaganda poster bot...")
        propaganda_bot.run(tokens['discord_token'])
        bot_state.status = "Running"

    except Exception as e:
        logger.error(f"Error running bot: {e}")
        bot_state.status = f"Error: {str(e)}"
