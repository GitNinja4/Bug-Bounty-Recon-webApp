from telegram import Bot

# Bot token and your chat ID
BOT_TOKEN = "7954354887:AAEiywBT6IT2EbDXQzN6VQ_NlyO8gSDNlUw"
CHAT_ID = "1446481039"

# Initialize the bot
bot = Bot(token=BOT_TOKEN)

# Function to send a message
def send_message(message):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"Error sending message: {e}")