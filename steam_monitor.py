
import logging
from steam.client import SteamClient
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
            self.client.anonymous_login()
            
            # Create monitoring task
            asyncio.create_task(self._monitor_loop())
        except Exception as e:
            logger.error(f"Error starting Steam monitor: {e}")
            self.is_monitoring = False

    async def _monitor_loop(self):
        """Background task for Steam monitoring."""
        self.is_monitoring = True
        while self.is_monitoring:
            try:
                for steam_id in self.watching_steam_ids:
                    try:
                        user = self.client.get_user(steam_id)
                        # Check for both CS2 and CSGO game IDs
                        is_playing_cs2 = user.game_id in [730, 2371320]

                        # Only trigger if user wasn't playing CS2 before but is now
                        if (steam_id not in self.previous_statuses or
                            (is_playing_cs2 and not self.previous_statuses[steam_id])):
                            logger.info(f"User {steam_id} started playing CS2!")
                            await self.handle_cs2_start()

                        self.previous_statuses[steam_id] = is_playing_cs2
                    except Exception as e:
                        logger.error(f"Error checking Steam ID {steam_id}: {e}")

                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in Steam monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def stop(self):
        """Stop monitoring Steam profiles."""
        self.is_monitoring = False
        if self.client:
            self.client.logout()

    async def handle_cs2_start(self):
        """Handle when a user starts playing CS2."""
        try:
            voice_channel_id = self.bot.propaganda_config.propaganda_scheduler.get("voice_channel_id")
            video_url = self.bot.propaganda_config.propaganda_scheduler.get("cs2_alert_video_url")
            
            if voice_channel_id and video_url:
                voice_channel = self.bot.get_channel(voice_channel_id)
                if voice_channel:
                    await self.bot.music_player.join_and_play(None, video_url, force_voice_channel=True)
            else:
                logger.warning("Voice channel or CS2 alert video URL not configured")
        except Exception as e:
            logger.error(f"Error playing CS2 alert: {e}")
