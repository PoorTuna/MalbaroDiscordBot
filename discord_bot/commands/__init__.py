from discord_bot.propaganda_bot import PropagandaBot


def register_commands(bot: PropagandaBot, api_tokens: list[str]):
    from discord_bot.commands.config_commands import register_config_commands
    from discord_bot.commands.music_player_commands import register_music_player_commands
    from discord_bot.commands.poster_generation_commands import register_poster_generation_commands
    from logging import getLogger

    logger = getLogger(__name__)
    register_config_commands(bot, api_tokens)
    register_music_player_commands(bot)
    register_poster_generation_commands(bot, api_tokens)
    logger.info("Registered bot commands successfully")
