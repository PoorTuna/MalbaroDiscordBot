import os
from asyncio import sleep
from logging import getLogger

from aiohttp import ClientSession
from discord import File

from discord_bot.models.token_config import TokenConfig

logger = getLogger(__name__)


async def generate_propaganda_poster(bot, api_tokens: list[str], channel: str = None):
    """Generate a propaganda poster and post it to the specified channel."""
    channel_id = bot.propaganda_config.propaganda_scheduler.poster_output_channel_id
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
            poster_text = text_prompt.strip()
            if not poster_text:
                raise ValueError("Failed to generate poster text")

            # Generate the poster image using the text and configuration
            image_url = await __generate_poster_image(
                poster_text,
                api_tokens,
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


async def __generate_poster_image(text: str, api_tokens: list[str], max_retries: int = 3) -> str:
    if not api_tokens:
        raise ValueError("No WaveSpeed tokens found")

    last_error = None
    async with ClientSession() as session:
        for token in api_tokens:
            try:
                result_json, headers = await __post_image_generation_prompt(text, session, token)
                result_url = result_json['data']['urls']['get']
                image_url = await __poll_for_image(max_retries, session, result_url, headers)
                return await __download_image(session, image_url)

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Token failed, trying next token. Error: {e}")

    logger.error(f"All tokens failed. Last error: {last_error}")
    raise Exception(f"All tokens failed. Last error: {last_error}")


async def __post_image_generation_prompt(text: str, session: ClientSession, token: str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "enable_base64_output": True,
        "enable_safety_checker": True,
        "prompt": text,
        "seed": -1,
        "size": "768*1152"
    }
    async with session.post(
            'https://api.wavespeed.ai/api/v2/wavespeed-ai/hidream-i1-full',
            headers=headers,
            json=data
    ) as resp:
        if resp.status != 200:
            raise Exception(f"Failed to create image: {await resp.text()}")
        return await resp.json(), headers


async def __poll_for_image(max_retries: int, session: ClientSession, url: str, headers: dict):
    for _ in range(max_retries):
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to get result: {await resp.text()}")

            result_data = await resp.json()
            status = result_data['data']['status']

            if status == 'completed':
                return result_data['data']['outputs'][0]

            elif status == 'failed':
                raise Exception(f"Image generation failed: {result_data['data'].get('error', 'Unknown error')}")
        await sleep(30)

    raise Exception("Image generation timed out")


async def __download_image(session: ClientSession, url: str):
    async with session.get(url) as resp:
        if resp.status != 200:
            raise Exception("Failed to download generated image")
        content = await resp.read()
        temp_path = f"temp_poster_{os.getpid()}.jpg"
        with open(temp_path, 'wb') as f:
            f.write(content)
        return temp_path
