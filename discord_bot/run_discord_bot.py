from logging import getLogger

from discord_bot.propaganda_bot import PropagandaBot
from discord_bot.commands import register_commands
from discord_bot.models.bot_state import get_bot_state
from discord_bot.models.token_config import TokenConfig

logger = getLogger(__name__)

bot_state = get_bot_state()


def run_discord_bot(propaganda_bot: PropagandaBot, token_config: TokenConfig) -> None:
    try:
        register_commands(propaganda_bot, token_config.wavespeed_tokens)
        logger.info("Starting Discord propaganda poster bot...")
        propaganda_bot.run(token_config.discord_token)
        bot_state.status = "Running"

    except Exception as e:
        logger.error(f"Error running bot: {e}")
        bot_state.status = f"Error: {str(e)}"
