import json
import logging
import os
import threading

from flask import Flask, render_template, jsonify

from bot import PropagandaBot
from discord_bot.commands import register_commands

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")

bot_thread = None
bot_instance = None
bot_status = "Not started"


def run_discord_bot():
    global bot_status, bot_instance
    try:
        if not os.path.exists('tokens_config.json'):
            logger.error(
                "tokens_config.json not found."
            )
            bot_status = "Error: No tokens found"
            return

        with open('tokens_config.json', 'r') as f:
            tokens = json.load(f)

        if not tokens.get('discord_token'):
            logger.error("Discord token not found in config")
            bot_status = "Error: Discord token not found in config"
            return

        bot_instance = PropagandaBot()
        register_commands(bot_instance)
        logger.info("Starting Discord propaganda poster bot...")
        bot_instance.run(tokens['discord_token'])
        bot_status = "Running"
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        bot_status = f"Error: {str(e)}"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/start_bot', methods=['POST'])
def start_bot():
    global bot_thread, bot_status
    if bot_thread is None or not bot_thread.is_alive():
        try:
            bot_status = "Starting..."
            bot_thread = threading.Thread(target=run_discord_bot)
            bot_thread.daemon = True
            bot_thread.start()
            return jsonify({"status": "Bot starting"})
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            bot_status = f"Error: {str(e)}"
            return jsonify({"status": bot_status}), 500
    return jsonify({"status": "Bot already running"})


def start_bot_automatically():
    with app.test_client() as client:
        client.post('/start_bot')


@app.route('/bot_status')
def get_bot_status():
    global bot_status
    return jsonify({"status": bot_status})
