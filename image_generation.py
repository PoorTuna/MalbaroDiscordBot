import os
import logging
import requests
import asyncio
import json

logger = logging.getLogger(__name__)


def load_tokens():
    """Load tokens from config file."""
    try:
        with open('tokens_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading tokens: {e}")
        return {"discord_token": "", "segmind_tokens": []}


async def generate_poster_text(prompt):
    """Generate text for a propaganda poster."""
    # For now, just return the prompt as-is since we're focusing on image generation
    return prompt.strip()


async def generate_poster_image(text,
                                theme="motivational",
                                style="soviet propaganda poster style"):
    """Generate a propaganda poster image using Segmind's API."""
    try:
        tokens = load_tokens().get('segmind_tokens', [])
        if not tokens:
            raise ValueError("No Segmind tokens found")

        last_error = None
        for token in tokens:
            try:
                # Construct the prompt
                prompt = f"Generate a {style} poster. have a text saying '{text}' incorporated artistically. Theme: {theme}"

                payload = {
                    "prompt": prompt,
                    "steps": 20,
                    "seed": 1184522,
                    "aspect_ratio": "2:3",
                    "base64": False
                }

                headers = {"x-api-key": token.strip()}

                # Run the API call in a thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, lambda: requests.post(
                        "https://api.segmind.com/v1/stable-diffusion-3.5-large-txt2img",
                        json=payload,
                        headers=headers))

                if response.status_code == 200:
                    logger.info(
                        f"Successfully generated image with token ending in ...{token[-4:]}"
                    )
                    # Handle direct image response
                    if response.headers.get('content-type') == 'image/jpeg':
                        # Save temporarily
                        temp_path = f"temp_poster_{os.getpid()}.jpeg"
                        with open(temp_path, 'wb') as f:
                            f.write(response.content)
                        return temp_path
                    else:
                        raise Exception(
                            "Expected image/jpeg response from API")
                elif response.status_code == 429:
                    logger.warning(
                        f"Token ...{token[-4:]} is rate limited, trying next token"
                    )
                    continue
                else:
                    last_error = f"API request failed: {response.status_code}"
                    continue

            except Exception as e:
                last_error = str(e)
                continue

        raise Exception(f"All tokens failed. Last error: {last_error}")

    except Exception as e:
        logger.error(f"Error generating poster image: {e}", exc_info=True)
        raise
