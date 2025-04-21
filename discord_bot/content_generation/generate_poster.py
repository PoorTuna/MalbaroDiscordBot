from logging import getLogger

from discord import File

from discord_bot.content_generation.generate_image import generate_poster_image, generate_poster_text

logger = getLogger(__name__)


async def generate_and_post_poster(bot, channel: str=None):
    """Generate a propaganda poster and post it to the specified channel."""
    channel_id = bot.propaganda_config.propaganda_scheduler.get(
        "poster_output_channel_id")
    if channel is None and channel_id:
        channel = bot.get_channel(channel_id)

    if not channel:
        logger.error("No channel set for posting propaganda poster")
        return

    try:
        async with channel.typing():
            # Get text and configuration from propaganda_config
            text_prompt = bot.propaganda_config.text_prompt

            # Generate the poster text
            poster_text = await generate_poster_text(text_prompt)
            if not poster_text:
                raise ValueError("Failed to generate poster text")

            # Generate the poster image using the text and configuration
            image_url = await generate_poster_image(
                poster_text,
                max_retries=bot.propaganda_config.max_retries)
            if not image_url:
                raise ValueError("Failed to generate poster image")

            # Create message with the poster
            with open(image_url, 'rb') as f:
                file = File(f, filename='propaganda_poster.png')
                await channel.send(
                    file=file,
                    content=f"**{bot.propaganda_config.poster_caption}**")

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
