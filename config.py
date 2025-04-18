import json
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PropagandaConfig:
    """Configuration manager for the propaganda poster bot."""

    DEFAULT_CONFIG_FILE = "propaganda_config.json"

    def __init__(self):
        """Initialize configuration with default values and load saved config if it exists."""
        # Get config file path from environment variable or use default
        config_dir = os.getenv("PROPAGANDA_CONFIG_DIR", '')
        self.config_file = os.path.join(config_dir, self.DEFAULT_CONFIG_FILE)
        self.propaganda_scheduler = {
            "time": {
                "hour": 12,
                "minute": 0
            },
            "timezone": 'Asia/Jerusalem',
            "poster_output_channel_id": None,
            "voice_channel_id": None,
            "youtube_playlist_url": ""
        }
        self.text_prompt = "Generate a short, inspiring slogan for a propaganda poster about technology and progress"
        self.poster_caption = "A True Malborian Culture Piece:"
        self.max_retries = 3

        # Load saved configuration if it exists
        self.load_config()

    def load_config(self):
        """Load configuration from file if it exists."""
        config_path = Path(self.config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as file:
                    config_data = json.load(file)

                # Update attributes from loaded config
                for key, value in config_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                        logger.info(f"Loaded config value: {key}={value}")

                logger.info("Successfully loaded configuration from file")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error in configuration: {e}")
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")

    def save_config(self):
        """Save the current configuration to a file."""
        try:
            config_data = {
                "propaganda_scheduler": self.propaganda_scheduler,
                "text_prompt": self.text_prompt,
                "poster_caption": self.poster_caption,
                "max_retries": self.max_retries
            }

            with open(self.config_file, 'w') as file:
                json.dump(config_data, file, indent=4)

            logger.info("Saved configuration to file")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def set_channel_id(self, channel_id):
        """Set the channel ID for posting propaganda."""
        self.propaganda_scheduler["poster_output_channel_id"] = channel_id
        self.save_config()

    def set_post_time(self, hour, minute):
        """Set the time for daily propaganda posts."""
        self.propaganda_scheduler["time"]["hour"] = hour
        self.propaganda_scheduler["time"]["minute"] = minute
        self.save_config()

    def set_theme(self, theme):
        """Set the theme for propaganda posters."""
        self.theme = theme
        self.save_config()

    def set_style(self, style):
        """Set the art style for propaganda posters."""
        self.style = style
        self.save_config()

    def set_text_prompt(self, prompt):
        """Set the text prompt for generating poster content."""
        self.text_prompt = prompt
        self.save_config()

    def set_poster_caption(self, caption):
        """Set the caption for the generated poster."""
        self.poster_caption = caption
        self.save_config()