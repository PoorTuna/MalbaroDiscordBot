"""
Pre-defined themes and styles for propaganda posters.
These can be used as suggestions or defaults by the bot.
"""

# Themes represent the subject matter or focus of the propaganda
THEMES = [
    "motivational",
    "technological progress",
    "unity",
    "productivity",
    "innovation",
    "national pride",
    "future vision",
    "scientific advancement",
    "space exploration",
    "environmental protection",
    "industrial strength",
    "digital revolution",
    "artificial intelligence",
    "collective achievement",
    "global cooperation",
    "military might",
    "social harmony",
    "educational excellence",
    "health and wellness",
    "energy independence"
]

# Styles represent the artistic approach and visual aesthetic
STYLES = [
    "soviet propaganda poster style",
    "art deco",
    "constructivist",
    "socialist realism",
    "chinese cultural revolution",
    "world war II american poster",
    "cold war era",
    "bauhaus",
    "futurism",
    "vaporwave",
    "cyberpunk",
    "retro-futurism",
    "minimalist",
    "brutalist",
    "pop art",
    "silkscreen print",
    "woodcut",
    "lithograph",
    "digital collage",
    "photomontage"
]

# Text prompts to guide the generation of poster text
TEXT_PROMPTS = [
    "Generate a short, inspiring slogan for a propaganda poster about technology and progress",
    "Create a patriotic slogan calling for national unity",
    "Write a propaganda slogan about the superiority of our scientific achievements",
    "Generate a motivational slogan for workers to increase productivity",
    "Create a slogan emphasizing collective effort and shared goals",
    "Write a propaganda phrase highlighting military strength and readiness",
    "Generate a slogan about building a better future through cooperation",
    "Create an educational propaganda slogan encouraging learning and development",
    "Write a short propaganda phrase about industrial might and production",
    "Generate a slogan about embracing technological innovation",
    "Create a propaganda slogan focusing on space exploration and discovery",
    "Write a short phrase for environmental protection with propaganda style",
    "Generate a slogan about the digital revolution changing society",
    "Create a propaganda phrase about the power of artificial intelligence",
    "Write a slogan emphasizing vigilance against enemies",
    "Generate a propaganda phrase about health and physical fitness",
    "Create a slogan about energy independence and resource management",
    "Write a propaganda phrase glorifying agricultural achievements",
    "Generate a slogan about cultural superiority and artistic excellence",
    "Create a propaganda phrase about economic prosperity and growth"
]

def get_random_theme():
    """Return a random propaganda theme."""
    import random
    return random.choice(THEMES)

def get_random_style():
    """Return a random propaganda art style."""
    import random
    return random.choice(STYLES)

def get_random_text_prompt():
    """Return a random text generation prompt."""
    import random
    return random.choice(TEXT_PROMPTS)
