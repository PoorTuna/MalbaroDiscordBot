
import os
import logging
import requests
import asyncio
import json
import time

logger = logging.getLogger(__name__)

def load_tokens():
    """Load tokens from config file."""
    try:
        with open('tokens_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading tokens: {e}")
        return {"discord_token": "", "wavespeed_api_key": ""}

async def generate_poster_text(prompt):
    """Generate text for a propaganda poster."""
    return prompt.strip()

async def generate_poster_image(text, theme="motivational", style="soviet propaganda poster style"):
    """Generate a propaganda poster image using WaveSpeed API."""
    try:
        tokens = load_tokens()
        api_tokens = tokens.get('wavespeed_tokens', [])
        if not api_tokens:
            raise ValueError("No WaveSpeed tokens found")
        
        last_error = None
        for token in api_tokens:
            try:
                # Step 1: Create image generation request
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }

        prompt = f"A {style} poster. {text}. Theme: {theme}"
        data = {
            "enable_base64_output": True,
            "enable_safety_checker": True,
            "prompt": prompt,
            "seed": -1,
            "size": "768*1152"
        }

        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.post(
                'https://api.wavespeed.ai/api/v2/wavespeed-ai/hidream-i1-full',
                headers=headers,
                json=data
            )
        )

        if response.status_code != 200:
            raise Exception(f"Failed to create image: {response.text}")

        result = response.json()
        result_url = result['data']['urls']['get']

        # Step 2: Poll for completion and get final image URL
        max_attempts = 30
        attempt = 0
        while attempt < max_attempts:
            result_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.get(result_url, headers=headers)
            )
            
            if result_response.status_code != 200:
                raise Exception(f"Failed to get result: {result_response.text}")

            result_data = result_response.json()
            if result_data['data']['status'] == 'completed':
                image_url = result_data['data']['outputs'][0]
                
                # Download the image
                image_response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: requests.get(image_url)
                )
                
                if image_response.status_code != 200:
                    raise Exception("Failed to download generated image")

                # Save temporarily
                temp_path = f"temp_poster_{os.getpid()}.jpg"
                with open(temp_path, 'wb') as f:
                    f.write(image_response.content)
                return temp_path

            if result_data['data']['status'] == 'failed':
                raise Exception(f"Image generation failed: {result_data['data'].get('error', 'Unknown error')}")

            attempt += 1
            await asyncio.sleep(1)

        raise Exception("Timeout waiting for image generation")

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Token failed, trying next token. Error: {e}")
                continue

        raise Exception(f"All tokens failed. Last error: {last_error}")

    except Exception as e:
        logger.error(f"Error generating poster image: {e}", exc_info=True)
        raise
