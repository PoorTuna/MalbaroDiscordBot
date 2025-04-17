import os
import logging
import requests
import asyncio

logger = logging.getLogger(__name__)

def get_segmind_api_key():
    """Get Segmind API key from environment variable."""
    api_key = os.getenv('SEGMIND_API_KEY')
    if not api_key and os.path.exists('segmind_key.txt'):
        with open('segmind_key.txt', 'r') as f:
            api_key = f.read().strip()
    os.environ['SEGMIND_API_KEY'] = api_key  # Update environment variable
    return api_key

async def generate_poster_text(prompt):
    """Generate text for a propaganda poster."""
    # For now, just return the prompt as-is since we're focusing on image generation
    return prompt.strip()

async def generate_poster_image(text, theme="motivational", style="soviet propaganda poster style"):
    """Generate a propaganda poster image using Segmind's API."""
    try:
        api_key = get_segmind_api_key()
        if not api_key:
            raise ValueError("Segmind API key not found")

        # Construct the prompt
        prompt = f"Generate a {style} poster. have a text saying '{text}' incorporated artistically. Theme: {theme}"

        payload = {
            "prompt": prompt,
            "steps": 20,
            "seed": 1184522,
            "aspect_ratio": "2:3",
            "base64": False
        }

        headers = {
            "x-api-key": api_key
        }

        # Run the API call in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(
                "https://api.segmind.com/v1/stable-diffusion-3.5-turbo-txt2img",
                json=payload,
                headers=headers,
                stream=True
            )
        )

        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}")
            
        if response.headers.get('content-type') == 'application/json':
            result = response.json()
            return result.get('image_url')
        else:
            # If we got a direct image response, we need to get a URL instead
            response = requests.post(
                "https://api.segmind.com/v1/stable-diffusion-3.5-turbo-txt2img",
                json=payload,
                headers=headers
            )
            result = response.json()
            return result.get('image_url')

    except Exception as e:
        logger.error(f"Error generating poster image: {e}", exc_info=True)
        raise