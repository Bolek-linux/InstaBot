# main.py
"""
This is the main entry point for the application.
It initializes the configuration, loads credentials, and starts the Telegram bot.
"""

import sys
import logging
from pyrogram import idle

from core.logging_config import setup_logging

# --- Local Imports ---
from core.config import API_ID, API_HASH, BOT_TOKEN, DATA_DIR
from core.instagram_handler import load_credentials, startup_login
from telegram.bot import app


if __name__ == "__main__":
    # --- Logging Configuration ---
    # It's crucial to set up logging as the very first step. The 'setup_logging'
    # function now handles the entire configuration, including setting levels
    # for third-party libraries and directing their output to specific files.
    setup_logging()

    # Get a logger for our main script.
    # Using __name__ is a standard practice that makes log messages more informative.
    logger = logging.getLogger(__name__)

    # --- Bot Startup Sequence ---
    logger.info("--- Starting the bot ---")

    # --- Ensure data Directory Exists ---
    # This guarantees that session and credential files have a place to be stored.
    DATA_DIR.mkdir(exist_ok=True)

    # Verify that essential Telegram credentials are set.
    if not all([API_ID, API_HASH, BOT_TOKEN]):
        logger.error(
            "FATAL: Telegram environment variables are not set. "
            "Please check your .env file or environment secrets."
        )
        sys.exit(1)

    # Load encrypted Instagram credentials if they exist.
    load_credentials()

    # Attempt a startup login to Instagram if credentials were loaded.
    # This restores the previous session without user interaction.
    startup_login()

    logger.info("[Pyrogram] Starting the bot...")
    app.start()
    logger.info("[Pyrogram] The bot has been launched! Send the /start command.")

    # Keep the bot running until it's manually stopped (e.g., with Ctrl+C).
    idle()

    logger.info("[Pyrogram] The bot has been stopped.")