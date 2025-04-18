
# Discord Propaganda Bot

A Discord bot that generates and posts propaganda-style images on a schedule, with music playback capabilities and CS2 game monitoring features.

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
        "youtube_playlist_url": "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID",
        "steam_ids": ["76561198244212404"],
        "cs2_alert_video_url": "https://www.youtube.com/watch?v=YOUR_ALERT_VIDEO_ID"
    },
    "text_prompt": "A vintage military recruitment poster featuring [your description]",
    "poster_caption": "A True Malborian Culture Piece:",
    "max_retries": 3
}
```

### tokens_config.json
Store your API tokens in this file. Example configuration:
```json
{
    "discord_token": "your_discord_bot_token_here",
    "wavespeed_tokens": ["token1", "token2", "token3"],
    "steam_api_key": "your_steam_api_key_here"
}
```

### Getting a Steam API Key
To obtain your Steam API key:
1. Go to https://steamcommunity.com/dev/apikey
2. Sign in with your Steam account
3. Enter a domain name (can be anything for personal use)
4. Accept the Steam Web API Terms of Use
5. Click "Register" to generate your API key
6. Copy the generated key and paste it in your `tokens_config.json` file

## Features

### Propaganda Generation
- Scheduled daily propaganda poster generation
- Custom text prompts and captions
- AI-powered image generation

### Music System
- YouTube playlist support
- Voice channel integration
- Background music during events

### CS2 Game Monitoring
- Steam profile monitoring
- Custom alert videos when users start playing CS2
- Automatic voice channel notifications

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

- Keep your Discord, Steam and WaveSpeed tokens secure
- Ensure proper permissions for the bot in your Discord server
- The bot requires both text and voice channel permissions for full functionality
- Steam monitoring requires valid Steam API key and Steam IDs
- Image generation depends on WaveSpeed API availability
