from asyncio import create_task, sleep
from functools import cache
from logging import getLogger

from aiohttp import ClientSession

from steam_monitor.handle_cs2_monitor import handle_cs2_start

logger = getLogger(__name__)


class SteamMonitor:
    def __init__(self, propaganda_bot):
        self.propaganda_bot = propaganda_bot
        self.watching_steam_ids = set()
        self.previous_statuses = {}
        self.is_monitoring = False

    async def start(self):
        """Start monitoring all configured Steam profiles."""
        try:
            steam_ids = self.propaganda_bot.propaganda_config.propaganda_scheduler.get(
                "steam_ids", [])
            if not steam_ids:
                logger.warning("No Steam IDs configured for monitoring")
                return

            self.watching_steam_ids = set(steam_ids)
            create_task(self._monitor_loop())
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
                api_key = self.propaganda_bot.propaganda_config.steam_api_key

                async with ClientSession() as session:
                    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={steam_ids}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()

                            for player in data['response']['players']:
                                steam_id = player['steamid']
                                game_id = player.get('gameid')
                                is_playing_cs2 = game_id == '730'  # CS2/CSGO game ID

                                was_playing_cs2 = self.previous_statuses.get(
                                    steam_id, False)

                                if is_playing_cs2 and not was_playing_cs2:
                                    logger.info(
                                        f"User {steam_id} started playing CS2!"
                                    )
                                    await handle_cs2_start(self)
                                elif not is_playing_cs2 and was_playing_cs2:
                                    logger.info(
                                        f"User {steam_id} stopped playing CS2."
                                    )
                                    # Reset status when they stop playing
                                    self.previous_statuses[steam_id] = False
                                else:
                                    # Always update the status
                                    self.previous_statuses[
                                        steam_id] = is_playing_cs2

                await sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in Steam monitoring loop: {e}")
                await sleep(5)  # Wait before retrying

    async def stop(self):
        """Stop monitoring Steam profiles."""
        self.is_monitoring = False


@cache
def get_steam_monitor(propaganda_bot):
    return SteamMonitor(propaganda_bot)
