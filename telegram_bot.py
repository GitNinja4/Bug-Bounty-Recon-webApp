from telegram import Bot
import os
import asyncio
from typing import Optional

# Get bot token and chat ID from environment variables
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Initialize the bot if environment variables are set
bot: Optional[Bot] = None
if BOT_TOKEN and CHAT_ID:
    bot = Bot(token=BOT_TOKEN)

# Function to send a message
def send_message(message: str) -> None:
    if not bot or not CHAT_ID:
        print("Telegram bot not configured - skipping notification")
        return
    
    try:
        # Create event loop if one doesn't exist
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Send message synchronously
        loop.run_until_complete(bot.send_message(
            chat_id=CHAT_ID,
            text=message
        ))
    except Exception as e:
        print(f"Error sending message: {e}")