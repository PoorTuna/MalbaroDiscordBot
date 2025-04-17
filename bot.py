import os
import logging
import discord
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
        
        super().__init__(command_prefix='!', intents=intents)
        
        # Store bot configuration
        self.propaganda_config = PropagandaConfig()
        
        # Register commands
        self.add_commands()
    
    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info('------')
        
        # Set up the scheduled task for daily poster generation
        setup_scheduler(self)
    
    async def on_error(self, event, *args, **kwargs):
        """Handle any uncaught exceptions in the bot."""
        logger.error(f'Error in event {event}', exc_info=True)
    
    def add_commands(self):
        """Register all bot commands."""
        
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
    
    async def generate_and_post_poster(self, channel=None):
        """Generate a propaganda poster and post it to the specified channel."""
        if channel is None and self.propaganda_config.channel_id:
            channel = self.get_channel(self.propaganda_config.channel_id)
        
        if not channel:
            logger.error("No channel set for posting propaganda poster")
            return
        
        try:
            async with channel.typing():
                # Generate poster text based on the configured prompt
                poster_text = await generate_poster_text(self.propaganda_config.text_prompt)
                
                # Generate the poster image using the text and configuration
                image_url = await generate_poster_image(
                    poster_text,
                    theme=self.propaganda_config.theme,
                    style=self.propaganda_config.style
                )
                
                # Create an embed with the poster
                embed = discord.Embed(
                    title="Daily Propaganda Poster",
                    description=poster_text,
                    color=discord.Color.red()
                )
                embed.set_image(url=image_url)
                
                # Send the propaganda poster to the channel
                await channel.send(embed=embed)
                logger.info(f"Posted propaganda poster to channel {channel.name}")
        
        except Exception as e:
            logger.error(f"Error generating propaganda poster: {e}", exc_info=True)
            await channel.send(f"⚠️ Failed to generate propaganda poster: {e}")
