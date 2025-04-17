import os
import logging
import asyncio
from openai import OpenAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def generate_poster_text(prompt):
    """
    Generate text for a propaganda poster using OpenAI's text generation.
    
    Args:
        prompt (str): The text prompt to guide the generation of poster text
        
    Returns:
        str: The generated poster text
    """
    try:
        # Run the API call in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: _generate_text_sync(prompt)
        )
    except Exception as e:
        logger.error(f"Error generating poster text: {e}", exc_info=True)
        return "UNITE FOR PROGRESS"  # Default fallback text

def _generate_text_sync(prompt):
    """Synchronous function for generating text using OpenAI."""
    response = client.chat.completions.create(
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": "You are a propaganda slogan generator. Create short, impactful, and persuasive text suitable for a propaganda poster. The text should be concise (10 words or less) and powerful."
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.7
    )
    
    # Extract and return the generated text
    return response.choices[0].message.content.strip().replace('"', '')

async def generate_poster_image(text, theme="motivational", style="soviet propaganda poster style"):
    """
    Generate a propaganda poster image using OpenAI's DALL-E.
    
    Args:
        text (str): The text to include on the poster
        theme (str): The theme or subject of the propaganda
        style (str): The art style for the poster
        
    Returns:
        str: URL of the generated image
    """
    try:
        # Construct the prompt for image generation
        prompt = f"A propaganda poster in {style} style with the theme of {theme}. The poster has the text '{text}' prominently displayed. The image should look like a genuine political propaganda poster with bold colors, symbolic imagery, and dramatic composition."
        
        # Run the API call in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: _generate_image_sync(prompt)
        )
        
        return result
    except Exception as e:
        logger.error(f"Error generating poster image: {e}", exc_info=True)
        raise

def _generate_image_sync(prompt):
    """Synchronous function for generating images using OpenAI."""
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    
    # Return the URL of the generated image
    return response.data[0].url
