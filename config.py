import json
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PropagandaConfig:
    """Configuration manager for the propaganda poster bot."""
    
    CONFIG_FILE = "propaganda_config.json"
    
    def __init__(self):
        """Initialize configuration with default values and load saved config if it exists."""
        # Default configuration
        self.channel_id = None  # Discord channel ID to post propaganda to
        self.hour = 12          # Hour of the day to post (UTC)
        self.minute = 0         # Minute of the hour to post (UTC)
        self.theme = "motivational"  # Theme of the propaganda
        self.style = "soviet propaganda poster style"  # Art style of the propaganda
        self.text_prompt = "Generate a short, inspiring slogan for a propaganda poster about technology and progress"
        
        # Load saved configuration if it exists
        self.load_config()
    
    def load_config(self):
        """Load configuration from file if it exists."""
        config_path = Path(self.CONFIG_FILE)
        if config_path.exists():
            try:
                with open(config_path, 'r') as file:
                    config_data = json.load(file)
                
                # Update attributes from loaded config
                for key, value in config_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                
                logger.info("Loaded configuration from file")
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
    
    def save_config(self):
        """Save the current configuration to a file."""
        try:
            config_data = {
                "channel_id": self.channel_id,
                "hour": self.hour,
                "minute": self.minute,
                "theme": self.theme,
                "style": self.style,
                "text_prompt": self.text_prompt
            }
            
            with open(self.CONFIG_FILE, 'w') as file:
                json.dump(config_data, file, indent=4)
            
            logger.info("Saved configuration to file")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def set_channel_id(self, channel_id):
        """Set the channel ID for posting propaganda."""
        self.channel_id = channel_id
        self.save_config()
    
    def set_post_time(self, hour, minute):
        """Set the time for daily propaganda posts (in UTC)."""
        self.hour = hour
        self.minute = minute
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
