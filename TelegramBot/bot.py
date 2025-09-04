# TelegramBot/bot.py
"""
This module initializes the Pyrogram Client instance.
It configures the bot with API credentials and sets up the plugin system
to automatically load handlers from the 'handlers' directory.
"""

from pyrogram import Client
from core.config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "Data/live_checker_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="TelegramBot.handlers")
)
