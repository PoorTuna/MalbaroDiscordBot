import logging
from threading import Thread

from fastapi.requests import Request
from fastapi.responses import JSONResponse

from discord_bot.api.app import templates, app
from discord_bot.bot import PropagandaBot
from discord_bot.models.bot_state import get_bot_state
from discord_bot.models.propaganda_config import get_propaganda_config
from discord_bot.models.token_config import get_token_config
from discord_bot.run_discord_bot import run_discord_bot

logger = logging.getLogger(__name__)
bot_state = get_bot_state()


@app.get('/')
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.on_event("startup")
@app.post('/start_bot')
async def start_bot():
    propaganda_config = get_propaganda_config()
    tokens_config = get_token_config()
    propaganda_bot = PropagandaBot(bot_config=propaganda_config, token_config=tokens_config)
    if bot_state.thread is not None and bot_state.thread.is_alive():
        return JSONResponse({"status": "Bot already running"})

    try:
        bot_state.status = "Starting..."
        bot_state.thread = Thread(target=run_discord_bot,
                                  args=[propaganda_bot, tokens_config], daemon=True)
        bot_state.thread.start()
        # steam_monitor = get_steam_monitor(propaganda_bot)
        # await steam_monitor.start()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        bot_state.status = f"Error: {str(e)}"
        return JSONResponse({"status": bot_state.status}), 500

    return JSONResponse({"status": "Bot & Steam monitoring starting"})


@app.get('/bot_status')
def get_bot_status():
    return JSONResponse({"status": bot_state.status})
