# main.py
"""
This is the main entry point for the application.
It initializes the configuration, loads credentials, and starts the Telegram bot.
"""

import sys
import logging
from logging_config import setup_logging

# --- Local Imports ---
from config import API_ID, API_HASH, BOT_TOKEN
from instagram_handler import load_credentials, startup_login
from telegram_bot import app, idle

if __name__ == "__main__":
    # --- Logging Configuration ---
    # It's crucial to set up logging as the very first step to ensure
    # all subsequent events in the application are properly logged.
    setup_logging()

    # The following lines silence the overly verbose loggers from third-party libraries.
    # By setting their level to WARNING, we only see important messages (like errors)
    # instead of flooding the console with routine operational details (like INFO or DEBUG).

    # Pyrogram is very verbose, logging every low-level interaction with Telegram's
    # servers. Setting it to WARNING keeps the logs clean.
    # -> To debug Telegram connection issues, change this to logging.INFO or logging.DEBUG.
    logging.getLogger("pyrogram").setLevel(logging.WARNING)

    # Urllib3 is a low-level HTTP library used by 'requests' (which instagrapi uses).
    # It logs every single connection, which is unnecessary for normal operation.
    # -> To debug raw network requests, change this to logging.INFO.
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # This is the main logger for the instagrapi library. While it's not as noisy
    # as the others, we set it to WARNING to suppress general informational messages.
    # Note: This does NOT silence the API request logs below.
    logging.getLogger("instagrapi").setLevel(logging.WARNING)

    # These are specific loggers within instagrapi that log every single API call
    # made to Instagram's private (logged-in) and public (anonymous) endpoints.
    # These logs were the source of the unwanted messages in the console.
    # -> To see every API endpoint being called, change these to logging.INFO.
    logging.getLogger("private_request").setLevel(logging.WARNING)
    logging.getLogger("public_request").setLevel(logging.WARNING)

    # Get a logger for our main script.
    # Using __name__ is a standard practice that makes log messages more informative.
    logger = logging.getLogger(__name__)

    # --- Bot Startup Sequence ---
    logger.info("--- Starting the bot ---")

    # Verify that essential Telegram credentials are set.
    if not all([API_ID, API_HASH, BOT_TOKEN]):
        logger.error(
            "FATAL: Telegram environment variables are not set. "
            "Please check your .env file or environment secrets."
        )
        sys.exit(1)

    # Load encrypted Instagram credentials if they exist.
    # Login is not performed here; it's an on-demand action in the Telegram bot.
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