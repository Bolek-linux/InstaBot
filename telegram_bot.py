# telegram_bot.py
"""
This module contains all the Telegram bot logic using Pyrogram.
It defines command handlers and the main message processing logic.
"""

import asyncio
import logging
from pyrogram import Client as PyrogramClient, filters, idle
from pyrogram.types import Message

# --- Local Imports ---
from config import API_ID, API_HASH, BOT_TOKEN, CRITICAL_INSTAGRAM_EXCEPTIONS, SESSION_FILE, CREDENTIALS_FILE
from instagram_handler import (
    attempt_login,
    check_livestream,
    save_credentials
)
import shared_state

logger = logging.getLogger(__name__)

# --- Telegram Bot Initialization ---
app = PyrogramClient("live_checker_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# --- Command Handlers ---
@app.on_message(filters.command("start"))
async def start_handler(client: PyrogramClient, message: Message):
    """Handles the /start command, displaying a welcome message."""
    await message.reply_text(
        "Welcome! I am a bot that checks for Instagram live streams.\n\n"
        "**Available Commands:**\n"
        "▫️ `/setlogin <username>` - Sets the Instagram username.\n"
        "▫️ `/setpassword <password>` - Sets the Instagram password (message will be deleted).\n"
        "▫️ `/login` - Manually attempts to log in using the saved credentials.\n"
        "▫️ `/status` - Checks if the bot is currently logged in to Instagram.\n"
        "▫️ `/logout` - Logs the bot out and clears all saved data.\n\n"
        "After a successful login, you can send me a username to check if they are live."
    )


@app.on_message(filters.command("setlogin"))
async def set_login_handler(client: PyrogramClient, message: Message):
    """Handles setting the Instagram username."""
    if shared_state.instagrapi_client is not None:
        await message.reply_text(
            "❌ **Action denied:** The bot is already logged in.\n\n"
            "To change credentials, please use the `/logout` command first."
        )
        return

    try:
        username = message.text.split(" ", 1)[1].strip()
        shared_state.ig_credentials["username"] = username
        save_credentials()
        await message.reply_text(f"✅ Instagram username has been set to: `{username}`.")

        if "password" in shared_state.ig_credentials and shared_state.ig_credentials["password"]:
            await message.reply_text("Both username and password are set. Use the `/login` command to connect.")
        else:
            await message.reply_text("Now, please set the password using `/setpassword <password>`.")

    except IndexError:
        await message.reply_text("Incorrect usage. Format: `/setlogin <username>`")


@app.on_message(filters.command("setpassword"))
async def set_password_handler(client: PyrogramClient, message: Message):
    """Handles setting the Instagram password and deletes the message for security."""
    if shared_state.instagrapi_client is not None:
        await message.reply_text(
            "❌ **Action denied:** The bot is already logged in.\n\n"
            "To change credentials, please use the `/logout` command first."
        )
        await message.delete()
        return

    try:
        password = message.text.split(" ", 1)[1].strip()
        shared_state.ig_credentials["password"] = password
        save_credentials()

        await message.reply_text(
            "✅ Instagram password has been set. Your message with the password will be deleted shortly.")

        if "username" in shared_state.ig_credentials and shared_state.ig_credentials["username"]:
            await message.reply_text("Both username and password are set. Use the `/login` command to connect.")
        else:
            await message.reply_text("Now, please set the username using `/setlogin <username>`.")

        await asyncio.sleep(2)
        await message.delete()

    except IndexError:
        await message.reply_text("Incorrect usage. Format: `/setpassword <password>`")


@app.on_message(filters.command("login"))
async def login_command_handler(client: PyrogramClient, message: Message):
    """Manually triggers the login process."""
    if shared_state.instagrapi_client is not None:
        await message.reply_text("ℹ️ **Info:** The bot is already logged in.")
        return

    if "username" in shared_state.ig_credentials and "password" in shared_state.ig_credentials:
        # Call the login function with a flag indicating it's a manual first attempt.
        await attempt_login(message, manual_first_attempt=True)
    else:
        await message.reply_text(
            "❌ **Cannot log in:** Credentials are not set.\n\n"
            "Please use `/setlogin <username>` and `/setpassword <password>` first."
        )


@app.on_message(filters.command("logout"))
async def logout_command_handler(client: PyrogramClient, message: Message):
    """Handles logging out and clearing all credentials and session files."""
    if not shared_state.instagrapi_client and not shared_state.ig_credentials:
        await message.reply_text("ℹ️ **Info:** The bot is not logged in and no credentials are saved.")
        return

    shared_state.instagrapi_client = None
    shared_state.ig_credentials = {}

    if SESSION_FILE.exists(): SESSION_FILE.unlink()
    if CREDENTIALS_FILE.exists(): CREDENTIALS_FILE.unlink()

    logger.info("[Logout] User has manually cleared all credentials and session data.")
    await message.reply_text(
        "✅ **Logged Out Successfully.**\n\n"
        "All credentials and session files have been deleted. "
        "You can now set new credentials using `/setlogin` and `/setpassword`."
    )


@app.on_message(filters.command("status"))
async def status_command_handler(client: PyrogramClient, message: Message):
    """Checks the current login status for Instagram."""
    if shared_state.instagrapi_client:
        await message.reply_text("✅ The bot is successfully logged in to Instagram.")
    else:
        await message.reply_text(
            "❌ The bot is not logged in to Instagram. Use /setlogin and /setpassword, then /login.")


# --- Main Message Handler ---
@app.on_message(
    filters.text & filters.private & ~filters.command(["start", "setlogin", "setpassword", "login", "status"]))
async def message_handler(client: PyrogramClient, message: Message):
    """Handles regular text messages to check for live streams."""
    if shared_state.instagrapi_client is None:
        await message.reply_text(
            "The bot is not ready yet (not logged in to Instagram). "
            "Please make sure you have configured your username and password, then use the /login command."
        )
        return

    username = message.text.strip().replace("@", "")
    processing_message = await message.reply_text(f"Checking if `{username}` is broadcasting... Please wait.")

    try:
        result = await asyncio.to_thread(check_livestream, shared_state.instagrapi_client, username)

        if result["status"] == "success":
            if result["live"]:
                response_text = (f"✅ **Yes, `{username}` is now live!**"
                                 f"\n\n**Broadcast ID:** `{result['broadcast_id']}`"
                                 f"\n\n**Link to the MPD manifest:**\n`{result['mpd_url']}`"
                                 f"\n\n**Record command:**\n`streamlink \"{result['mpd_url']}\" best --stdout | ffmpeg -i pipe:0 -c copy {result['broadcast_id']}.mp4`")
            else:
                response_text = f"❌ **No, `{username}` is not live streaming.**"

        # Handle the new "private" status.
        elif result["status"] == "private":
            response_text = f"ℹ️ **Info:** {result['message']}"

        else:  # This covers the "error" status
            response_text = f"⚠️ **Error:** {result['message']}"

        await processing_message.edit_text(response_text, disable_web_page_preview=True)

    except CRITICAL_INSTAGRAM_EXCEPTIONS as _e:
        logger.critical("\n--- A CRITICAL ERROR OCCURRED DURING BOT OPERATION. ---")
        shared_state.instagrapi_client = None  # Reset the client
        if SESSION_FILE.exists(): SESSION_FILE.unlink()
        if CREDENTIALS_FILE.exists(): CREDENTIALS_FILE.unlink()
        shared_state.ig_credentials = {}
        logger.warning("[Credentials] Deleted credentials file due to a critical session error.")
        await processing_message.edit_text(
            f"⚠️ **Critical Error:** A problem occurred with the Instagram session (e.g., logout). The session and credentials have been reset. Please configure and log in again.\n\n`{_e}`")