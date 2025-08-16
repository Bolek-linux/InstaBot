# main.py
"""
This is the main entry point for the application.
It initializes the configuration, loads credentials, and starts the Telegram bot.
"""

import sys

# --- Local Imports ---
from config import API_ID, API_HASH, BOT_TOKEN
from instagram_handler import load_credentials, startup_login
from telegram_bot import app, idle

if __name__ == "__main__":
    print("--- Starting the bot ---")

    if not all([API_ID, API_HASH, BOT_TOKEN]):
        print("ERROR: Telegram environment variables are not set. Please check your .env file.")
        sys.exit(1)

    # Load credentials if they exist, but do not attempt to log in on startup.
    # Login is now an on-demand action triggered by the user in Telegram.
    load_credentials()
    startup_login()

    print("[Pyrogram] Starting the bot...")
    app.start()
    print("[Pyrogram] The bot has been launched! Send the /start command.")
    idle()
    print("[Pyrogram] The bot has been stopped..")