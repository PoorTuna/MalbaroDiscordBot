from flask import Flask, render_template, jsonify
import threading
import os
import logging
from dotenv import load_dotenv
from bot import PropagandaBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")

# Global variable to track if the bot is running
bot_thread = None
bot_instance = None
bot_status = "Not started"

def run_discord_bot():
    """Run the Discord bot in a separate thread."""
    global bot_status
    try:
        load_dotenv()
        
        # Check for required environment variables
        required_vars = ['DISCORD_TOKEN', 'OPENAI_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            bot_status = f"Error: Missing environment variables: {', '.join(missing_vars)}"
            return
        
        # Initialize and run the bot
        global bot_instance
        bot_instance = PropagandaBot()
        logger.info("Starting Discord propaganda poster bot...")
        bot_status = "Running"
        bot_instance.run(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        bot_status = f"Error: {str(e)}"

@app.route('/')
def home():
    """Home page route."""
    return render_template('index.html')

@app.route('/start_bot', methods=['POST'])
def start_bot():
    """Start the Discord bot."""
    global bot_thread, bot_status
    
    if bot_thread is None or not bot_thread.is_alive():
        bot_status = "Starting..."
        bot_thread = threading.Thread(target=run_discord_bot)
        bot_thread.daemon = True
        bot_thread.start()
        return jsonify({"status": "Bot starting"})
    else:
        return jsonify({"status": "Bot already running"})

@app.route('/bot_status')
def get_bot_status():
    """Get the current status of the bot."""
    global bot_status
    return jsonify({"status": bot_status})

# Create templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)

# Create a simple index.html file in the templates directory
if not os.path.exists('templates/index.html'):
    with open('templates/index.html', 'w') as f:
        f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Discord Propaganda Poster Bot</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <style>
        body {
            padding: 20px;
        }
        .bot-status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
        }
    </style>
</head>
<body data-bs-theme="dark">
    <div class="container">
        <div class="row mt-4">
            <div class="col-md-8 offset-md-2">
                <div class="card">
                    <div class="card-header">
                        <h1 class="text-center">Discord Propaganda Poster Bot</h1>
                    </div>
                    <div class="card-body">
                        <p class="lead">This bot generates propaganda-style posters using OpenAI's GPT-4o and DALL-E models, and posts them to your Discord server.</p>
                        
                        <div class="alert alert-info">
                            <h5>Bot Commands:</h5>
                            <ul>
                                <li><code>!generate</code> - Generate a propaganda poster immediately</li>
                                <li><code>!set_channel</code> - Set the current channel for daily posters</li>
                                <li><code>!set_time</code> - Set the daily posting time (format: HH:MM in UTC)</li>
                                <li><code>!set_theme</code> - Set the theme for propaganda posters</li>
                                <li><code>!set_style</code> - Set the art style for propaganda posters</li>
                                <li><code>!set_text_prompt</code> - Set the text prompt for generating poster text</li>
                                <li><code>!show_config</code> - Show the current bot configuration</li>
                            </ul>
                        </div>
                        
                        <div class="text-center mt-4">
                            <button id="startBot" class="btn btn-primary">Start Bot</button>
                        </div>
                        
                        <div id="botStatus" class="bot-status alert alert-secondary mt-4">
                            Bot Status: <span id="statusText">Not started</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('startBot').addEventListener('click', function() {
            fetch('/start_bot', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('statusText').textContent = data.status;
                checkBotStatus();
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
        
        function checkBotStatus() {
            fetch('/bot_status')
            .then(response => response.json())
            .then(data => {
                const statusText = document.getElementById('statusText');
                statusText.textContent = data.status;
                
                const statusDiv = document.getElementById('botStatus');
                if (data.status === 'Running') {
                    statusDiv.className = 'bot-status alert alert-success';
                } else if (data.status.startsWith('Error')) {
                    statusDiv.className = 'bot-status alert alert-danger';
                } else if (data.status === 'Starting...') {
                    statusDiv.className = 'bot-status alert alert-info';
                } else {
                    statusDiv.className = 'bot-status alert alert-secondary';
                }
                
                // Continue checking status every 2 seconds if the bot is starting
                if (data.status === 'Starting...') {
                    setTimeout(checkBotStatus, 2000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
        
        // Check initial status
        checkBotStatus();
    </script>
</body>
</html>
        """)

# Auto-start the bot when the app starts
if __name__ == "__main__":
    start_bot()