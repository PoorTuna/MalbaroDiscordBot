import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_invite_link():
    """Generate a Discord bot invite link with proper permissions for slash commands."""
    load_dotenv()
    
    # Get the bot token from environment variables
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables")
        return None
    
    try:
        # Extract the bot's client ID from the token
        # This is a simplistic approach and might not work for all token formats
        # But it's a common structure for Discord tokens
        client_id = token.split('.')[0]
        
        # If client ID can't be extracted from token, ask the user to provide it
        if not client_id.isdigit():
            logger.warning("Couldn't extract client ID from token")
            client_id = input("Please enter your bot's client ID: ").strip()

        # Calculate permissions integer for required permissions
        # 2147483647 is a full permissions integer, but we'll use specific ones
        permissions = (
            0x0000000000000008  # View Channels
            | 0x0000000000000010  # Manage Channels
            | 0x0000000000000400  # View Audit Log
            | 0x0000000000000800  # View Server Insights
            | 0x0000000000001000  # Manage Server
            | 0x0000000000004000  # Manage Roles
            | 0x0000000000008000  # Manage Webhooks
            | 0x0000000000010000  # Manage Emojis And Stickers
            | 0x0000000000020000  # View Audit Log
            | 0x0000000000040000  # View Webhooks
            | 0x0000000000080000  # Use Application Commands
            | 0x0000000000200000  # Request To Speak
            | 0x0000000000400000  # Manage Events
            | 0x0000000000800000  # Manage Threads
            | 0x0000000002000000  # Send Messages In Threads
            | 0x0000000004000000  # Use Public Threads
            | 0x0000000008000000  # Use Private Threads
            | 0x0000000010000000  # Use External Stickers
            | 0x0000000020000000  # Send Messages
            | 0x0000000040000000  # Manage Messages
            | 0x0000000080000000  # Embed Links
            | 0x0000000100000000  # Attach Files
            | 0x0000000200000000  # Read Message History
            | 0x0000000400000000  # Mention Everyone
            | 0x0000000800000000  # Use External Emojis
            | 0x0000001000000000  # Add Reactions
            | 0x0000008000000000  # Connect
        )
        
        # Generate the invite URL
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions={permissions}&scope=bot%20applications.commands"
        
        return invite_url
    except Exception as e:
        logger.error(f"Error generating invite link: {e}")
        return None

if __name__ == "__main__":
    invite_url = generate_invite_link()
    
    if invite_url:
        print("\n=== DISCORD BOT INVITE LINK ===")
        print(f"\n{invite_url}\n")
        print("Use this link to invite your bot to your server with the correct permissions for slash commands.")
        print("After re-inviting, it may take up to an hour for slash commands to appear in Discord's UI.")
        print("However, guild-specific commands should appear much faster.\n")
    else:
        print("Failed to generate invite link. Please check your environment variables.")