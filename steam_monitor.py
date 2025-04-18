import logging
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

class SteamMonitor:
    def __init__(self, bot):
        self.bot = bot
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
                steam_ids = ','.join(self.watching_steam_ids)
                api_key = self.bot.propaganda_config.steam_api_key

                async with aiohttp.ClientSession() as session:
                    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={steam_ids}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()

                            for player in data['response']['players']:
                                steam_id = player['steamid']
                                game_id = player.get('gameid')
                                is_playing_cs2 = game_id == '730'  # CS2/CSGO game ID

                                was_playing_cs2 = self.previous_statuses.get(steam_id, False)

                                if is_playing_cs2 and not was_playing_cs2:
                                    logger.info(f"User {steam_id} started playing CS2!")
                                    await self.handle_cs2_start()
                                elif not is_playing_cs2 and was_playing_cs2:
                                    logger.info(f"User {steam_id} stopped playing CS2.")

                                self.previous_statuses[steam_id] = is_playing_cs2

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in Steam monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def stop(self):
        """Stop monitoring Steam profiles."""
        self.is_monitoring = False

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