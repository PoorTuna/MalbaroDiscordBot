import os
import logging
import discord
from discord import app_commands
from discord.ext import commands
from scheduler import setup_scheduler
from config import PropagandaConfig
from discord.interactions import Interaction
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
        # Register slash commands
        logger.info('hello world')
        await self.register_commands()

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

    async def on_app_command(self, interaction: Interaction):
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

    async def register_commands(self):
        """Register all bot slash commands."""
        # Create a command tree
        self.tree.clear_commands(guild=None)

        @self.tree.command(
            name="generate",
            description="Generate a propaganda poster immediately")
        async def generate(self, interaction: Interaction):
            await self._handle_generate(interaction.channel,
                                        interaction.response.send_message)

        @self.tree.command(
            name="set_channel",
            description="Set the current channel for daily propaganda posters")
        async def set_channel(self, interaction: Interaction):
            """Set the current channel as the destination for daily posters."""
            self.propaganda_config.set_channel_id(interaction.channel_id)
            await interaction.response.send_message(
                f"This channel has been set for daily propaganda posters.")

        @self.tree.command(
            name="set_time",
            description=
            "Set the time for daily propaganda posts (format: HH:MM in UTC)")
        @app_commands.describe(time_str="Time in HH:MM format (24-hour, UTC)")
        async def set_time(self, interaction: Interaction, time_str: str):
            await self._handle_set_time(time_str,
                                        interaction.response.send_message)

        @self.tree.command(
            name="set_text_prompt",
            description="Set the text prompt for generating poster text")
        @app_commands.describe(prompt="The prompt to guide text generation")
        async def set_text_prompt(self, interaction: Interaction, prompt: str):
            """Set the text prompt for generating poster text."""
            self.propaganda_config.set_text_prompt(prompt)
            await interaction.response.send_message(
                f"Text generation prompt set to: {prompt}")

        @self.tree.command(
            name="set_timezone",
            description="Set the timezone for propaganda poster scheduling")
        async def set_timezone(self, interaction: Interaction, timezone: str):
            """Set the timezone for scheduling."""
            try:
                pytz.timezone(timezone)  # Validate timezone
                self.propaganda_config.timezone = timezone
                self.propaganda_config.save_config()

                # Reschedule with new timezone
                setup_scheduler(self)

                await interaction.response.send_message(
                    f"✅ Timezone set to: {timezone}")
            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Invalid timezone. Example valid timezones: Asia/Jerusalem, Europe/London, US/Eastern"
                )

        @self.tree.command(
            name="show_config",
            description="Show current propaganda poster configuration")
        async def show_config(self, interaction: Interaction):
            """Display the current configuration."""
            config = self.propaganda_config
            channel_mention = f"<#{config.channel_id}>" if config.channel_id else "Not set"

            # Create main configuration embed
            embed = discord.Embed(title="Propaganda Poster Configuration",
                                  color=discord.Color.blue())
            embed.add_field(name="Channel", value=channel_mention, inline=True)
            embed.add_field(
                name="Post Time",
                value=
                f"{config.hour:02d}:{config.minute:02d} {config.timezone}",
                inline=True)

            # Truncate text prompt if too long
            text_prompt = config.text_prompt
            if len(text_prompt) > 1000:
                text_prompt = text_prompt[:997] + "..."

            embed.add_field(name="Text Prompt",
                            value=text_prompt,
                            inline=False)

            try:
                await interaction.response.send_message(embed=embed)
            except discord.HTTPException as e:
                logger.error(f"Error sending config embed: {e}")
                await interaction.response.send_message(
                    "⚠️ Error displaying configuration. Please check the logs.",
                    ephemeral=True)

        @self.tree.command(
            name="set_discord_token",
            description=
            "Set the Discord bot token (use in DM only for security)")
        async def set_discord_token(self, interaction: Interaction,
                                    token: str):
            """Set the Discord bot token."""
            if not isinstance(interaction.channel, discord.DMChannel):
                await interaction.response.send_message(
                    "⚠️ For security, please use this command in a DM with the bot.",
                    ephemeral=True)
                return

            try:
                config = {}
                if os.path.exists(self.tokens_config_path):
                    with open(self.tokens_config_path, 'r') as f:
                        config = json.load(f)

                config['discord_token'] = token
                with open(self.tokens_config_path, 'w') as f:
                    json.dump(config, f, indent=4)

                await interaction.response.send_message(
                    "✅ Discord token has been updated!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Error setting Discord token: {str(e)}", ephemeral=True)

        @self.tree.command(
            name="help",
            description="Get information about available commands")
        async def help(self, interaction: Interaction):
            """Display help information about the bot."""
            embed = discord.Embed(
                title="Propaganda Poster Bot - Help",
                description=
                "I am a bot that generates propaganda-style posters using AI. Here are my commands:",
                color=discord.Color.blue())

            commands = {
                "generate": "Generate a propaganda poster immediately",
                "set_channel": "Set the current channel for daily posters",
                "set_time":
                "Set the daily posting time (format: HH:MM in UTC)",
                "set_text_prompt":
                "Set the text prompt for generating poster text",
                "set_discord_token": "Set the Discord bot token (DM only)",
                "set_timezone":
                "Set the timezone for propaganda poster scheduling",
                "show_config": "Show the current bot configuration",
                "help": "Display this help message"
            }

            for cmd, desc in commands.items():
                embed.add_field(name=f"/{cmd}", value=desc, inline=False)

            await interaction.response.send_message(embed=embed)

        @self.tree.command(
            name="play",
            description="Play a random song from the configured playlist")
        async def play(self, interaction: Interaction):
            """Play a random song from the playlist."""
            await interaction.response.send_message(
                "🎵 Playing a random song from the playlist...")
            await self.music_player.join_and_play(interaction)

        @self.tree.command(name="play_url",
                           description="Play a specific YouTube URL")
        @app_commands.describe(url="YouTube URL to play")
        async def play_url(self, interaction: Interaction, url: str):
            """Play a specific YouTube URL."""
            await interaction.response.send_message(f"🎵 Playing: {url}")
            await self.music_player.join_and_play(interaction, url)

        @self.tree.command(name="add_to_playlist",
                           description="Add a YouTube URL to the playlist")
        @app_commands.describe(url="YouTube URL to add")
        async def add_to_playlist(self, interaction: Interaction, url: str):
            """Add a URL to the playlist."""
            self.music_player.add_to_playlist(url)
            await interaction.response.send_message(
                f"✅ Added to playlist: {url}")

        # Try to sync the commands with Discord
        try:
            # Try to find a guild to sync commands to
            guilds = self.guilds
            if guilds:
                # Log information about the guilds
                logger.info(f"Bot is in {len(guilds)} guilds")
                for guild in guilds:
                    logger.info(f"Guild: {guild.name} (ID: {guild.id})")

                # Try syncing to each guild individually for faster update
                for guild in guilds:
                    try:
                        commands = await self.tree.sync(guild=guild)
                        logger.info(
                            f"Slash commands synced to guild: {guild.name} (ID: {guild.id}), {len(commands)} commands"
                        )
                    except Exception as e:
                        logger.error(
                            f"Error syncing commands to guild {guild.name}: {e}"
                        )

            # Also sync globally (this can take up to an hour to propagate)
            global_commands = await self.tree.sync()
            logger.info(
                f"Slash commands registered and synced globally: {len(global_commands)} commands"
            )

            # Print invite URL with proper permissions
            app_id = self.user.id
            permissions = discord.Permissions(send_messages=True,
                                              embed_links=True,
                                              attach_files=True,
                                              manage_webhooks=True)
            invite_url = discord.utils.oauth_url(
                app_id,
                permissions=permissions,
                scopes=("bot", "applications.commands"))
            logger.info(f"Invite URL with proper permissions: {invite_url}")

        except Exception as e:
            logger.error(f"Error syncing slash commands: {e}")
            # Continue with regular commands if slash commands fail

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

        @self.tree.command(
            name="set_poster_caption",
            description="Set the caption text for generated posters")
        @app_commands.describe(
            caption="The caption text that accompanies each poster")
        async def set_poster_caption(self, interaction: Interaction,
                                     caption: str):
            """Set the poster caption text."""
            self.propaganda_config.poster_caption = caption
            self.propaganda_config.save_config()
            await interaction.response.send_message(
                f"Poster caption set to: {caption}")
