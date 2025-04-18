# Discord Propaganda Bot

A Discord bot that generates and posts propaganda-style images on a schedule, with music playback capabilities.

## System Requirements

### Required Software
- Python 3.11 or higher
- FFmpeg (for audio processing)
- libffi
- libsodium

### Dependencies
All Python dependencies are listed in `requirements.txt`. Install them using:
```bash
pip install -r requirements.txt
```

## Configuration Files

### propaganda_config.json
Configure the bot's behavior with this file. Example configuration:
```json
{
    "propaganda_scheduler": {
        "time": {
            "hour": 12,
            "minute": 15
        },
        "timezone": "Asia/Jerusalem",
        "poster_output_channel_id": 123456789012345678,
        "voice_channel_id": 123456789012345678,
        "youtube_playlist_url": "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
    },
    "text_prompt": "A vintage military recruitment poster featuring [your description]",
    "poster_caption": "A True Malborian Culture Piece:",
    "max_retries": 3,
    "youtube_playlist_url": "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
}
```

### tokens_config.json
Store your API tokens in this file. Example configuration:
```json
{
    "discord_token": "your_discord_bot_token_here",
    "wavespeed_tokens": ["token1", "token2", "token3"]
}
```

## Setup and Running

1. Install the required system dependencies
2. Configure your tokens in `tokens_config.json`
3. Configure bot settings in `propaganda_config.json`
4. Run the bot:
   ```bash
   python main.py
   ```

## Bot Commands

- `/generate`: Generate a propaganda poster immediately
- `/set_channel`: Set the current channel for propaganda posts
- `/set_time`: Set daily posting schedule
- `/set_timezone`: Configure the timezone
- `/show_config`: Display current configuration
- `/play`: Play music from a YouTube URL
- `/leave`: Disconnect from voice channel
- `/set_voice_channel`: Set the default voice channel

## Web Interface

The bot includes a web interface running on port 5000 that allows you to:
- Monitor bot status
- Start/stop the bot
- View basic configuration

## Error Handling

The bot includes comprehensive error handling for:
- API rate limits
- Authentication issues
- Content policy violations
- Network timeouts
- Invalid configurations

## Important Notes

- Keep your Discord and WaveSpeed tokens secure
- Ensure proper permissions for the bot in your Discord server
- The bot requires both text and voice channel permissions for full functionality
- Image generation depends on WaveSpeed API availability