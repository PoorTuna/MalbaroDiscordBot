
import logging
from steam.client import SteamClient
from steam.enums.common import EPersonaState
import asyncio

logger = logging.getLogger(__name__)

class SteamMonitor:
    def __init__(self, bot):
        self.bot = bot
        self.client = SteamClient()
        self.watching_steam_ids = set()
        self.previous_statuses = {}
        self.is_monitoring = False

    async def start(self):
        """Start monitoring all configured Steam profiles."""
        try:
            steam_ids = self.bot.propaganda_config.propaganda_scheduler.get("steam_ids", [])
            if not steam_ids:
                logger.warning("No Steam IDs configured for monitoring")
                return

            self.watching_steam_ids = set(steam_ids)
            self.is_monitoring = True
            self.client.anonymous_login()
            
            while self.is_monitoring:
                for steam_id in self.watching_steam_ids:
                    try:
                        user = self.client.get_user(steam_id)
                        current_status = {
                            'state': user.state,
                            'game_id': user.game_id
                        }

                        # CS2's game ID is 730
                        if (steam_id in self.previous_statuses and 
                            current_status['game_id'] == 730 and 
                            self.previous_statuses[steam_id]['game_id'] != 730):
                            logger.info(f"User {steam_id} started playing CS2!")
                            await self.handle_cs2_start()

                        self.previous_statuses[steam_id] = current_status
                    except Exception as e:
                        logger.error(f"Error checking Steam ID {steam_id}: {e}")

                await asyncio.sleep(30)  # Check every 30 seconds

        except Exception as e:
            logger.error(f"Error in Steam monitoring: {e}")
            self.is_monitoring = False

    async def stop(self):
        """Stop monitoring Steam profiles."""
        self.is_monitoring = False
        if self.client:
            self.client.logout()

    async def handle_cs2_start(self):
        """Handle when a user starts playing CS2."""
        try:
            voice_channel_id = self.bot.propaganda_config.propaganda_scheduler.get("voice_channel_id")
            playlist_url = self.bot.propaganda_config.propaganda_scheduler.get("cs2_alert_video_url")
            
            if voice_channel_id and playlist_url:
                voice_channel = self.bot.get_channel(voice_channel_id)
                if voice_channel:
                    await self.bot.music_player.join_and_play(None, playlist_url, force_voice_channel=True)
            else:
                logger.warning("Voice channel or CS2 alert video URL not configured")
        except Exception as e:
            logger.error(f"Error playing CS2 alert: {e}")
