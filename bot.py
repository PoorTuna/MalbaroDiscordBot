import os
import logging
import discord
from discord import app_commands
from discord.ext import commands
from scheduler import setup_scheduler
from config import PropagandaConfig
from image_generation import generate_poster_image, generate_poster_text

logger = logging.getLogger(__name__)

class PropagandaBot(commands.Bot):
    """Discord bot for generating and posting propaganda posters."""

    def __init__(self):
        """Initialize the bot with required intents and configuration."""
        intents = discord.Intents.default()
        intents.message_content = True

        # Keep the prefix commands for backward compatibility
        super().__init__(command_prefix='!', intents=intents)

        # Store bot configuration
        self.propaganda_config = PropagandaConfig()

        # Register traditional commands for backward compatibility
        self.add_commands()

        # Add event listeners for logging
        self.add_listeners()

    async def setup_hook(self):
        """Called when the bot is starting up."""
        # Register slash commands
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

        @self.event
        async def on_message(message):
            """Log all messages that could be commands."""
            # Don't respond to our own messages
            if message.author == self.user:
                return

            # Log potential command messages
            if message.content.startswith('!'):
                logger.info(f"Command message received from {message.author} in {message.channel}: {message.content}")

            # Process commands as usual
            await self.process_commands(message)

        @self.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
            """Log errors when processing slash commands."""
            logger.error(f"Error executing slash command: {error}", exc_info=True)

            # Create a more user-friendly error message
            user_message = "Something went wrong with that command."

            # Check for specific error types to provide better messages
            if "invalid_request_error" in str(error).lower() or "openai.badrequest" in str(error).lower():
                user_message = "The image couldn't be generated. This might be due to content policies. Try a different theme or wording."

            await interaction.response.send_message(f"⚠️ {user_message}", ephemeral=True)

        # Add listener for slash command invocation
        self.tree.on_error = self.on_app_command_error

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handle errors in slash commands."""
        logger.error(f"Error in slash command {interaction.command.name if interaction.command else 'unknown'}: {error}", exc_info=True)

        # Provide useful error message - already handled by the tree.error decorator above

    async def on_app_command(self, interaction: discord.Interaction):
        """Log when slash commands are used."""
        command_name = interaction.command.name if interaction.command else "unknown"
        user = interaction.user
        channel = interaction.channel

        # Log the interaction
        logger.info(f"Slash command '{command_name}' used by {user} in {channel}")

        # Log the parameters if available
        try:
            if interaction.namespace:
                params = ' '.join([f"{k}='{v}'" for k, v in interaction.namespace.__dict__.items()])
                logger.info(f"Parameters: {params}")
        except Exception as e:
            logger.error(f"Error logging slash command parameters: {e}")

    async def on_command(self, ctx):
        """Log when regular commands are used."""
        logger.info(f"Regular command '{ctx.command}' used by {ctx.author} in {ctx.channel}")

        # Log the command arguments if any
        if ctx.args and len(ctx.args) > 1:  # First arg is the bot itself
            args = ' '.join([str(a) for a in ctx.args[1:]])
            logger.info(f"Arguments: {args}")

        if ctx.kwargs:
            kwargs = ' '.join([f"{k}='{v}'" for k, v in ctx.kwargs.items()])
            logger.info(f"Keyword arguments: {kwargs}")

    def add_commands(self):
        """Register traditional prefix commands for backward compatibility."""

        @self.command(name="generate", help="Generate a propaganda poster immediately")
        async def generate(ctx):
            """Generate and post a propaganda poster immediately."""
            await ctx.send("Generating propaganda poster... This may take a moment.")
            await self.generate_and_post_poster(ctx.channel)

        @self.command(name="set_channel", help="Set the channel for daily propaganda posters")
        async def set_channel(ctx):
            """Set the current channel as the destination for daily posters."""
            self.propaganda_config.set_channel_id(ctx.channel.id)
            await ctx.send(f"This channel has been set for daily propaganda posters.")

        @self.command(name="set_time", help="Set the time for daily propaganda posts (format: HH:MM in UTC)")
        async def set_time(ctx, time_str):
            """Set the time for daily propaganda poster generation."""
            try:
                hour, minute = map(int, time_str.split(':'))
                if 0 <= hour < 24 and 0 <= minute < 60:
                    self.propaganda_config.set_post_time(hour, minute)
                    await ctx.send(f"Daily propaganda posters will be posted at {time_str} UTC.")
                else:
                    await ctx.send("Invalid time format. Please use HH:MM in 24-hour format.")
            except ValueError:
                await ctx.send("Invalid time format. Please use HH:MM (e.g., 15:30 for 3:30 PM UTC).")

        @self.command(name="set_theme", help="Set the theme for propaganda posters")
        async def set_theme(ctx, *, theme):
            """Set the theme for propaganda posters."""
            self.propaganda_config.set_theme(theme)
            await ctx.send(f"Propaganda poster theme set to: {theme}")

        @self.command(name="set_style", help="Set the art style for propaganda posters")
        async def set_style(ctx, *, style):
            """Set the art style for propaganda posters."""
            self.propaganda_config.set_style(style)
            await ctx.send(f"Propaganda poster style set to: {style}")

        @self.command(name="set_text_prompt", help="Set the text prompt for generating poster text")
        async def set_text_prompt(ctx, *, prompt):
            """Set the text prompt for generating poster text."""
            self.propaganda_config.set_text_prompt(prompt)
            await ctx.send(f"Text generation prompt set to: {prompt}")

        @self.command(name="show_config", help="Show current propaganda poster configuration")
        async def show_config(ctx):
            """Display the current configuration."""
            config = self.propaganda_config
            channel_mention = f"<#{config.channel_id}>" if config.channel_id else "Not set"

            embed = discord.Embed(
                title="Propaganda Poster Configuration",
                color=discord.Color.red()
            )
            embed.add_field(name="Channel", value=channel_mention, inline=False)
            embed.add_field(name="Post Time (UTC)", value=f"{config.hour:02d}:{config.minute:02d}", inline=True)
            embed.add_field(name="Theme", value=config.theme, inline=True)
            embed.add_field(name="Art Style", value=config.style, inline=True)
            embed.add_field(name="Text Prompt", value=config.text_prompt, inline=False)

            await ctx.send(embed=embed)

    async def register_commands(self):
        """Register all bot slash commands."""
        # Create a command tree
        self.tree.clear_commands(guild=None)

        # Register the generate command
        @self.tree.command(
            name="generate",
            description="Generate a propaganda poster immediately"
        )
        async def generate(interaction: discord.Interaction):
            """Generate and post a propaganda poster immediately."""
            await interaction.response.send_message("Generating propaganda poster... This may take a moment.")
            await self.generate_and_post_poster(interaction.channel)

        # Register the set_channel command
        @self.tree.command(
            name="set_channel",
            description="Set the current channel for daily propaganda posters"
        )
        async def set_channel(interaction: discord.Interaction):
            """Set the current channel as the destination for daily posters."""
            self.propaganda_config.set_channel_id(interaction.channel_id)
            await interaction.response.send_message(f"This channel has been set for daily propaganda posters.")

        # Register the set_time command
        @self.tree.command(
            name="set_time",
            description="Set the time for daily propaganda posts (format: HH:MM in UTC)"
        )
        @app_commands.describe(time_str="Time in HH:MM format (24-hour, UTC)")
        async def set_time(interaction: discord.Interaction, time_str: str):
            """Set the time for daily propaganda poster generation."""
            try:
                hour, minute = map(int, time_str.split(':'))
                if 0 <= hour < 24 and 0 <= minute < 60:
                    self.propaganda_config.set_post_time(hour, minute)
                    await interaction.response.send_message(f"Daily propaganda posters will be posted at {time_str} UTC.")
                else:
                    await interaction.response.send_message("Invalid time format. Please use HH:MM in 24-hour format.")
            except ValueError:
                await interaction.response.send_message("Invalid time format. Please use HH:MM (e.g., 15:30 for 3:30 PM UTC).")

        # Register the set_theme command
        @self.tree.command(
            name="set_theme",
            description="Set the theme for propaganda posters"
        )
        @app_commands.describe(theme="The theme or subject of the propaganda")
        async def set_theme(interaction: discord.Interaction, theme: str):
            """Set the theme for propaganda posters."""
            self.propaganda_config.set_theme(theme)
            await interaction.response.send_message(f"Propaganda poster theme set to: {theme}")

        # Register the set_style command
        @self.tree.command(
            name="set_style",
            description="Set the art style for propaganda posters"
        )
        @app_commands.describe(style="The art style for the propaganda poster")
        async def set_style(interaction: discord.Interaction, style: str):
            """Set the art style for propaganda posters."""
            self.propaganda_config.set_style(style)
            await interaction.response.send_message(f"Propaganda poster style set to: {style}")

        # Register the set_text_prompt command
        @self.tree.command(
            name="set_text_prompt",
            description="Set the text prompt for generating poster text"
        )
        @app_commands.describe(prompt="The prompt to guide text generation")
        async def set_text_prompt(interaction: discord.Interaction, prompt: str):
            """Set the text prompt for generating poster text."""
            self.propaganda_config.set_text_prompt(prompt)
            await interaction.response.send_message(f"Text generation prompt set to: {prompt}")

        @self.tree.command(
            name="show_config",
            description="Show current propaganda poster configuration"
        )
        async def show_config(interaction: discord.Interaction):
            """Display the current configuration."""
            config = self.propaganda_config
            channel_mention = f"<#{config.channel_id}>" if config.channel_id else "Not set"

        @self.tree.command(
            name="set_openai_key",
            description="Set the OpenAI API key (use in DM only for security)"
        )
        async def set_openai_key(interaction: discord.Interaction, api_key: str):
            """Set the OpenAI API key."""
            # Only allow this command in DMs
            if not isinstance(interaction.channel, discord.DMChannel):
                await interaction.response.send_message("⚠️ For security, please use this command in a DM with the bot.", ephemeral=True)
                return

            import openai
            # Test the key
            try:
                temp_client = openai.OpenAI(api_key=api_key)
                temp_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                # If no error, key is valid
                os.environ['OPENAI_API_KEY'] = api_key
                global client
                client = openai.OpenAI(api_key=api_key)
                await interaction.response.send_message("✅ OpenAI API key has been updated successfully!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ Error testing API key: {str(e)}", ephemeral=True)

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
                        await self.tree.sync(guild=guild)
                        logger.info(f"Slash commands synced to guild: {guild.name} (ID: {guild.id})")
                    except Exception as e:
                        logger.error(f"Error syncing commands to guild {guild.name}: {e}")

            # Also sync globally (this can take up to an hour to propagate)
            synced = await self.tree.sync()
            logger.info(f"Slash commands registered and synced globally: {len(synced)} commands")

            # Print invite URL with proper permissions
            app_id = self.user.id
            permissions = discord.Permissions(
                send_messages=True, 
                embed_links=True, 
                attach_files=True,
                manage_webhooks=True
            )
            invite_url = discord.utils.oauth_url(
                app_id, 
                permissions=permissions, 
                scopes=("bot", "applications.commands")
            )
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
                theme = self.propaganda_config.theme
                style = self.propaganda_config.style

                # Generate the poster text
                poster_text = await generate_poster_text(text_prompt)
                if not poster_text:
                    raise ValueError("Failed to generate poster text")

                # Generate the poster image using the text and configuration
                image_url = await generate_poster_image(
                    poster_text,
                    theme=theme,
                    style=style
                )
                if not image_url:
                    raise ValueError("Failed to generate poster image")

                # Create an embed with the poster
                embed = discord.Embed(
                    title="Propaganda Poster",
                    description=poster_text,
                    color=discord.Color.red()
                )
                embed.set_image(url=image_url)

                # Send the propaganda poster to the channel
                await channel.send(embed=embed)
                logger.info(f"Posted propaganda poster to channel {channel.name}")

        except Exception as e:
            error_msg = f"Error generating propaganda poster: {str(e)}"
            logger.error(error_msg, exc_info=True)

            # Create a more user-friendly error message
            user_message = "Something went wrong generating the poster."

            # Check for specific error types to provide better messages
            if "invalid_request_error" in str(e).lower() or "openai.badrequest" in str(e).lower():
                user_message = "The image couldn't be generated. This might be due to content policies. Try a different theme or wording."

            await channel.send(f"⚠️ {user_message}")