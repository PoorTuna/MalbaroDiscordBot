
# Discord Propaganda Bot

A Discord bot that generates and posts propaganda-style images on a schedule, with music playback capabilities.

## Requirements

### Python Version
- Python 3.11 or higher

### System Dependencies
- FFmpeg (for audio processing)
- pkg-config
- libffi
- libsodium
- libxcrypt
- PostgreSQL
- OpenSSL

### Python Dependencies
See `requirements.txt` for the complete list of Python packages. Key dependencies include:
- discord.py (2.5.2+)
- Flask (3.1.0+)
- APScheduler (3.11.0+)
- python-dotenv (1.1.0+)
- pytz (2025.2+)

## Configuration Files

### propaganda_config.json
```json
{
    "voice_channel_id": ID of the Discord voice channel for music
    "channel_id": ID of the Discord text channel for propaganda posts
    "hour": Hour of the day for scheduled posts (24-hour format)
    "minute": Minute of the hour for scheduled posts
    "timezone": Timezone for scheduling (e.g., "Asia/Jerusalem")
    "text_prompt": Template for image generation
    "poster_caption": Caption prefix for posted images
    "max_retries": Maximum attempts for image generation
    "youtube_playlist_url": URL of the propaganda music playlist
}
```

### tokens_config.json
```json
{
    "discord_token": Your Discord bot token
    "wavespeed_tokens": Array of WaveSpeed API tokens for image generation
}
```

## Setup and Running

1. Configure your tokens:
   - Create `tokens_config.json` with your Discord bot token and WaveSpeed API tokens
   - Alternatively, set the `DISCORD_TOKEN` environment variable

2. Configure propaganda settings:
   - Adjust `propaganda_config.json` with your desired settings
   - Set appropriate channel IDs and scheduling preferences

3. Run the bot:
   - Click the "Run" button in Replit
   - The bot will start and connect to Discord
   - The web interface will be available on port 5000

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

