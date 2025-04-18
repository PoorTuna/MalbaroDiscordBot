import logging
from steam.client import SteamClient
import asyncio
from eventemitter import EventEmitter

logger = logging.getLogger(__name__)


class SteamMonitor:

    def __init__(self, bot):
        self.bot = bot
        self.client = None
        self.watching_steam_ids = set()
        self.previous_statuses = {}
        self.is_monitoring = False

    async def start(self):
        """Start monitoring all configured Steam profiles."""
        try:
            steam_ids = self.bot.propaganda_config.propaganda_scheduler.get(
                "steam_ids", [])
            if not steam_ids:
                logger.warning("No Steam IDs configured for monitoring")
                return

            self.watching_steam_ids = set(steam_ids)

            # Initialize Steam client
            self.client = SteamClient()
            self.client._events = {}  # Initialize events dictionary

            # Connect and login synchronously with better error handling
            try:
                logger.info("Attempting to connect to Steam...")
                if not self.client.connect():
                    logger.error(
                        "Failed to connect to Steam - connection failed")
                    return
                logger.info("Steam connection successful")

                logger.info("Attempting anonymous Steam login...")
                if not self.client.anonymous_login():
                    logger.error(
                        "Failed to login to Steam anonymously - login failed")
                    return
                logger.info("Steam anonymous login successful")

            except Exception as e:
                logger.error(f"Error connecting to Steam: {e}")
            # Start monitoring
            asyncio.create_task(self._monitor_loop())
            logger.info("Steam monitoring started successfully")

        except Exception as e:
            logger.error(f"Error starting Steam monitor: {e}")
            self.is_monitoring = False

    async def _monitor_loop(self):
        """Background task for Steam monitoring."""
        self.is_monitoring = True
        while self.is_monitoring:
            try:
                if not self.client or not self.client.connected:
                    logger.warning(
                        "Steam client disconnected, attempting to reconnect..."
                    )
                    await self.stop()
                    await asyncio.sleep(5)
                    await self.start()
                    continue

                for steam_id in self.watching_steam_ids:
                    try:
                        user = self.client.get_user(int(steam_id))
                        print(user.game_played_app_id, "xddddd")

                        if user:
                            if not self.client.user or not hasattr(
                                    self.client.user, 'personas'):
                                logger.debug(
                                    f"Client user or personas not ready for Steam ID {steam_id}"
                                )
                                continue

                            persona = self.client.user.personas.get(
                                user.steam_id)
                            if persona:
                                game_id = getattr(persona,
                                                  "game_played_app_id", None)
                                is_playing_cs2 = game_id in [730, 2371320]

                                was_playing_cs2 = self.previous_statuses.get(
                                    steam_id, False)

                                if is_playing_cs2 and not was_playing_cs2:
                                    logger.info(
                                        f"User {steam_id} started playing CS2!"
                                    )
                                    await self.handle_cs2_start()

                                elif not is_playing_cs2 and was_playing_cs2:
                                    logger.info(
                                        f"User {steam_id} stopped playing CS2."
                                    )

                                self.previous_statuses[
                                    steam_id] = is_playing_cs2
                            else:
                                logger.debug(
                                    f"No persona info available for {steam_id}"
                                )
                        else:
                            logger.warning(f"User {steam_id} not found")
                    except Exception as e:
                        logger.error(
                            f"Error checking Steam ID {steam_id}: {e}")

                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in Steam monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def stop(self):
        """Stop monitoring Steam profiles."""
        self.is_monitoring = False
        if self.client:
            if self.client.connected:
                self.client.logout()
            self.client.disconnect()

    async def handle_cs2_start(self):
        """Handle when a user starts playing CS2."""
        try:
            voice_channel_id = self.bot.propaganda_config.propaganda_scheduler.get(
                "voice_channel_id")
            video_url = self.bot.propaganda_config.propaganda_scheduler.get(
                "cs2_alert_video_url")

            if voice_channel_id and video_url:
                voice_channel = self.bot.get_channel(voice_channel_id)
                if voice_channel:
                    await self.bot.music_player.join_and_play(
                        None, video_url, force_voice_channel=True)
            else:
                logger.warning(
                    "Voice channel or CS2 alert video URL not configured")
        except Exception as e:
            logger.error(f"Error playing CS2 alert: {e}")
