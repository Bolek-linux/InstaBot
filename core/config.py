# core/config.py
"""
This module holds the application's configuration and constants.
It loads environment variables and defines file paths and critical error types.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from instagrapi.exceptions import (
    LoginRequired, BadPassword, ChallengeRequired,
    SentryBlock, ProxyAddressIsBlocked, ClientForbiddenError
)

# Load environment variables from a .env file
load_dotenv()

# --- Core Directories ---
DATA_DIR = Path("data")

# --- Configuration Files ---
SESSION_FILE = DATA_DIR / "session.enc"
CREDENTIALS_FILE = DATA_DIR / "credentials.enc"
DATABASE_FILE = DATA_DIR / "app_database.db"

# --- Telegram Credentials ---
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- Secret Command Configuration ---
# Hashed version of the secret command for administrative actions.
# This value should be generated using the 'utils/secret_hasher.py' script.
HASHED_SECRET_COMMAND = os.getenv("HASHED_SECRET_COMMAND")

# --- Critical Instagram Errors ---
# These exceptions indicate a fundamental problem with the Instagram session.
CRITICAL_INSTAGRAM_EXCEPTIONS = (
    LoginRequired, BadPassword, ChallengeRequired,
    SentryBlock, ProxyAddressIsBlocked, ClientForbiddenError
)
