import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str):
    """Sends a message to a specified Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials (TOKEN or CHAT_ID) not found in .env file. Skipping notification.")
        return False

    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'  # Allows for bold, italics, etc.
    }

    try:
        response = requests.post(api_url, json=payload, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        print("Successfully sent summary to Telegram.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message to Telegram: {e}")
        return False

if __name__ == '__main__':
    # For testing purposes
    print("Testing Telegram Notifier...")
    if send_telegram_message("Hello from the Medical Chatbot! This is a test message."):
        print("Test message sent successfully.")
    else:
        print("Failed to send test message. Check your .env configuration and network.")
