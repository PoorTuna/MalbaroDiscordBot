import os
import logging
import discord
from discord import app_commands
from discord.ext import commands
from scheduler import setup_scheduler
from config import PropagandaConfig
from image_generation import generate_poster_image, generate_poster_text
import pytz
import json

logger = logging.getLogger(__name__)


class PropagandaBot(commands.Bot):
    """Discord bot for generating and posting propaganda posters."""

    def __init__(self):
        """Initialize the bot with required intents and configuration."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True

        from music import MusicPlayer
        self.music_player = MusicPlayer()

        super().__init__(command_prefix=None, intents=intents)

        # Store bot configuration
        self.propaganda_config = PropagandaConfig()

        # Load tokens from config file
        tokens_config_dir = os.environ.get("TOKEN_CONFIG_DIR", '')
        self.tokens_config_path = os.path.join(tokens_config_dir,
                                               'tokens_config.json')

        try:
            with open(self.tokens_config_path, 'r') as f:
                self.tokens_config = json.load(f)
        except FileNotFoundError:
            self.tokens_config = {}

        # Add event listeners for logging
        self.add_listeners()

    async def setup_hook(self):
        """Called when the bot is starting up."""
        await self.setup_commands()

    async def setup_commands(self):

        @self.tree.command(name="play", description="Play a YouTube URL in your voice channel")
        async def play(interaction: discord.Interaction, url: str):
            await interaction.response.defer()
            await self.music_player.join_and_play(interaction, url)

        @self.tree.command(name="leave", description="Leave the voice channel")
        async def leave(interaction: discord.Interaction):
            if interaction.guild_id in self.music_player.voice_clients:
                voice_client = self.music_player.voice_clients[interaction.guild_id]
                await voice_client.disconnect()
                del self.music_player.voice_clients[interaction.guild_id]
                await interaction.response.send_message("Left the voice channel!")
            else:
                await interaction.response.send_message("I'm not in a voice channel!")

        @self.tree.command(
            name="generate",
            description="Generate a propaganda poster immediately")
        async def generate(interaction: discord.Interaction):
            await interaction.response.send_message(
                "Generating your propaganda poster...")
            await self.generate_and_post_poster(interaction.channel)

        @self.tree.command(
            name="set_channel",
            description="Set the current channel for propaganda posters")
        async def set_channel(interaction: discord.Interaction):
            self.propaganda_config.set_channel_id(interaction.channel_id)
            await interaction.response.send_message(
                "Channel set for propaganda posters.")

        @self.tree.command(name="set_time",
                           description="Set the time for daily posts (HH:MM)")
        async def set_time(interaction: discord.Interaction, time: str):
            try:
                hour, minute = map(int, time.split(':'))
                if 0 <= hour < 24 and 0 <= minute < 60:
                    self.propaganda_config.set_post_time(hour, minute)
                    await interaction.response.send_message(
                        f"Post time set to {time}")
                else:
                    await interaction.response.send_message(
                        "Invalid time format. Use HH:MM (24-hour format)")
            except ValueError:
                await interaction.response.send_message(
                    "Invalid time format. Use HH:MM (e.g., 15:30)")

        @self.tree.command(name="set_timezone", description="Set the timezone")
        async def set_timezone(interaction: discord.Interaction,
                               timezone: str):
            try:
                pytz.timezone(timezone)
                self.propaganda_config.timezone = timezone
                self.propaganda_config.save_config()
                setup_scheduler(self)
                await interaction.response.send_message(
                    f"Timezone set to: {timezone}")
            except Exception:
                await interaction.response.send_message(
                    "Invalid timezone. Example: US/Eastern, Europe/London")

        @self.tree.command(name="set_prompt",
                           description="Set the text generation prompt")
        async def set_prompt(interaction: discord.Interaction, prompt: str):
            self.propaganda_config.set_text_prompt(prompt)
            await interaction.response.send_message(
                "Text generation prompt updated.")

        @self.tree.command(name="show_config",
                           description="Show current configuration")
        async def show_config(interaction: discord.Interaction):
            config = self.propaganda_config
            channel_mention = f"<#{config.channel_id}>" if config.channel_id else "Not set"

            # Truncate text prompt if too long
            text_prompt = config.text_prompt
            if len(text_prompt) > 900:
                text_prompt = text_prompt[:897] + "..."

            embed = discord.Embed(title="Propaganda Poster Configuration",
                                  color=discord.Color.blue())
            embed.add_field(name="Channel", value=channel_mention, inline=True)
            embed.add_field(
                name="Post Time",
                value=
                f"{config.hour:02d}:{config.minute:02d} {config.timezone}",
                inline=True)
            embed.add_field(name="Text Prompt",
                            value=text_prompt,
                            inline=False)

            await interaction.response.send_message(embed=embed)

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

        async def on_message(self, message):
            pass

        @self.tree.error
        async def on_app_command_error(interaction: discord.Interaction,
                                       error: app_commands.AppCommandError):
            """Log errors when processing slash commands."""
            logger.error(f"Error executing slash command: {error}",
                         exc_info=True)

            # Create detailed user-friendly error messages
            user_message = "An error occurred while processing your command."

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

    async def on_app_command(self, interaction: discord.Interaction):
        """Log when slash commands are used."""
        command_name = interaction.command.name if interaction.command else "unknown"
        logger.info(
            f"Slash command '{command_name}' used by {interaction.user} in {interaction.channel}"
        )

    async def on_command(self, ctx):
        """Log when regular commands are used."""
        logger.info(
            f"Regular command '{ctx.command}' used by {ctx.author} in {ctx.channel}"
        )

        # Log the command arguments if any
        if ctx.args and len(ctx.args) > 1:  # First arg is the bot itself
            args = ' '.join([str(a) for a in ctx.args[1:]])
            logger.info(f"Arguments: {args}")

        if ctx.kwargs:
            kwargs = ' '.join([f"{k}='{v}'" for k, v in ctx.kwargs.items()])
            logger.info(f"Keyword arguments: {kwargs}")

    async def add_commands(self):
        """This method is deprecated - commands are now registered in setup_hook"""
        pass

    async def _handle_generate(self, channel, response_handler):
        """Shared handler for generating propaganda poster."""
        await response_handler(
            "A True Piece is in the Making... Smoke a true cigarette in the meanwhile 🚬."
        )
        await self.generate_and_post_poster(channel)

    async def _handle_set_time(self, time_str, response_handler):
        """Shared handler for setting poster time."""
        try:
            hour, minute = map(int, time_str.split(':'))
            if 0 <= hour < 24 and 0 <= minute < 60:
                self.propaganda_config.set_post_time(hour, minute)
                await response_handler(
                    f"Daily propaganda posters will be posted at {time_str} {self.propaganda_config.timezone}."
                )
            else:
                await response_handler(
                    "Invalid time format. Please use HH:MM in 24-hour format.")
        except ValueError:
            await response_handler(
                "Invalid time format. Please use HH:MM (e.g., 15:30 for 3:30 PM UTC)."
            )

    async def generate_and_post_poster(self, channel=None):
        """Generate a propaganda poster and post it to the specified channel."""
        if channel is None and self.propaganda_config.channel_id:
            channel = self.get_channel(self.propaganda_config.channel_id)

        if not channel:
            logger.error("No channel set for posting propaganda poster")
            return

        try:
            async with channel.typing():
                # Get text and configuration from propaganda_config
                text_prompt = self.propaganda_config.text_prompt

                # Generate the poster text
                poster_text = await generate_poster_text(text_prompt)
                if not poster_text:
                    raise ValueError("Failed to generate poster text")

                # Generate the poster image using the text and configuration
                image_url = await generate_poster_image(
                    poster_text,
                    max_retries=self.propaganda_config.max_retries)
                if not image_url:
                    raise ValueError("Failed to generate poster image")

                # Create message with the poster
                with open(image_url, 'rb') as f:
                    file = discord.File(f, filename='propaganda_poster.png')
                    await channel.send(
                        file=file,
                        content=f"**{self.propaganda_config.poster_caption}**")

                # Clean up the temporary file
                import os
                try:
                    os.remove(image_url)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file: {e}")
                logger.info(
                    f"Posted propaganda poster to channel {channel.name}")

        except Exception as e:
            error_msg = f"Error generating propaganda poster: {str(e)}"
            logger.error(error_msg, exc_info=True)

            # Create detailed error messages for poster generation
            error_str = str(e).lower()
            if "rate limit" in error_str or "429" in error_str:
                user_message = "⌛ Rate limit reached. The bot will try again in a few minutes."
            elif "api key" in error_str or "authentication" in error_str:
                user_message = "🔑 API Key Error: Please check your WaveSpeed API token."
            elif "timeout" in error_str:
                user_message = "⏱️ Request timed out. The bot will try again shortly."
            else:
                # Log the unexpected error for debugging
                logger.error(f"Unexpected error: {e}", exc_info=True)
                user_message = f"❌ Error: {str(e)}\nPlease report this if the issue persists."

            await channel.send(user_message)