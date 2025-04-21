import os
from functools import cache
from logging import getLogger

import discord
from discord import app_commands
from discord.ext import commands

from config import PropagandaConfig
from discord_bot.scheduler import setup_scheduler

logger = getLogger(__name__)


class PropagandaBot(commands.Bot):
    """Discord bot for generating and posting propaganda posters."""

    def __init__(self, *args, **kwargs):
        """Initialize the bot with required intents and configuration."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True

        from discord_bot.music_player.music import MusicPlayer
        self.music_player = MusicPlayer()

        super().__init__(*args, command_prefix="/", intents=intents, **kwargs)

        self.tree.clear_commands(guild=None)
        logger.info("Cleared all existing commands")
        # Store bot configuration
        self.propaganda_config = PropagandaConfig()

        # Load tokens from config file
        tokens_config_dir = os.environ.get("TOKEN_CONFIG_DIR", '')
        self.tokens_config_path = os.path.join(tokens_config_dir,
                                               'tokens_config.json')

        # Add event listeners for logging
        self.add_listeners()

    async def setup_hook(self):
        """Called when the bot is starting up."""
        synced_commands = await self.tree.sync()
        logger.info(
            f"{len(synced_commands)} Commands synced with Discord {synced_commands=}"
        )

    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info('------')
        # Set up the scheduled task for daily poster generation
        setup_scheduler(self)

    async def on_error(self, event, *args, **kwargs):
        """Handle any uncaught exceptions in the bot."""
        logger.error(f'Error in event {event}', exc_info=True)

    def add_listeners(self):
        """Add event listeners for logging command usage."""

        @self.tree.error
        async def on_app_command_error(interaction: discord.Interaction,
                                       error: app_commands.AppCommandError):
            """Log errors when processing slash commands."""
            logger.error(f"Error executing slash command: {error}",
                         exc_info=True)

            error_str = str(error).lower()
            if "invalid_request_error" in error_str or "openai.badrequest" in error_str:
                user_message = "⚠️ Content Policy Alert: The content couldn't be generated. Please try:\n- Using less controversial themes\n- Avoiding sensitive topics\n- Rewording your prompt"
            elif "rate limit" in error_str or "429" in error_str:
                user_message = "⌛ Rate limit reached. Please wait a few minutes before trying again."
            elif "api key" in error_str or "authentication" in error_str:
                user_message = "🔑 API Key Error: Please check your OpenAI API key using the /set_openai_key command."
            elif "timeout" in error_str:
                user_message = "⏱️ Request timed out. Please try again."
            else:
                # Log the unexpected error for debugging
                logger.error(f"Unexpected error: {error}", exc_info=True)
                user_message = f"❌ Error: {str(error)}\nPlease report this if the issue persists."

            await interaction.response.send_message(user_message,
                                                    ephemeral=True)

        # Set the error handler
        self.tree.on_error = on_app_command_error


@cache
def get_propganda_bot(*args, **kwargs):
    return PropagandaBot(*args, **kwargs)
