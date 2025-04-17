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

def get_working_segmind_token():
    """Get a working Segmind token, trying others only if the first fails."""
    tokens = load_tokens().get('segmind_tokens', [])
    if not tokens:
        raise ValueError("No Segmind tokens found in tokens_config.json")
    
    # Try the first token
    token = tokens[0].strip()
    try:
        logger.info("Attempting to use primary token...")
        response = requests.post(
            "https://api.segmind.com/v1/stable-diffusion-3.5-turbo-txt2img",
            headers={"x-api-key": token},
            json={"prompt": "test", "steps": 1}
        )
        if response.status_code == 200:
            return token
        
        # If first token fails, try others only for specific error cases
        if response.status_code in [429, 402, 403]:  # Rate limit or quota exceeded
            logger.warning(f"Primary token failed with status {response.status_code}, trying backup tokens")
            for backup_token in tokens[1:]:
                try:
                    response = requests.post(
                        "https://api.segmind.com/v1/stable-diffusion-3.5-turbo-txt2img",
                        headers={"x-api-key": backup_token.strip()},
                        json={"prompt": "test", "steps": 1}
                    )
                    if response.status_code == 200:
                        return backup_token.strip()
                except Exception as e:
                    logger.warning(f"Backup token failed: {str(e)}")
                    continue
                    
        logger.error(f"Primary token failed with status {response.status_code}: {response.text}")
        raise ValueError(f"Token error: {response.status_code}")
        
    except Exception as e:
        logger.error(f"Error with primary token: {str(e)}")
        raise ValueError(f"Token error: {str(e)}")
    
    raise ValueError("No working Segmind token found - all tokens failed")

async def generate_poster_text(prompt):
    """Generate text for a propaganda poster."""
    # For now, just return the prompt as-is since we're focusing on image generation
    return prompt.strip()

async def generate_poster_image(text, theme="motivational", style="soviet propaganda poster style"):
    """Generate a propaganda poster image using Segmind's API."""
    try:
        api_key = get_working_segmind_token()
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
                headers=headers
            )
        )

        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}")

        # Handle direct image response
        if response.headers.get('content-type') == 'image/jpeg':
            # Save temporarily
            temp_path = f"temp_poster_{os.getpid()}.jpeg" #changed to .jpeg
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            return temp_path
        else:
            raise Exception("Expected image/jpeg response from API")

    except Exception as e:
        logger.error(f"Error generating poster image: {e}", exc_info=True)
        raise