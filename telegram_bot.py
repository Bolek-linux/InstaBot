# telegram_bot.py
"""
This module contains all the Telegram bot logic using Pyrogram.
It defines command handlers and the main message processing logic.
"""

import asyncio
from pyrogram import Client as PyrogramClient, filters, idle
from pyrogram.types import Message

# --- Local Imports ---
from config import API_ID, API_HASH, BOT_TOKEN, CRITICAL_INSTAGRAM_EXCEPTIONS, SESSION_FILE, CREDENTIALS_FILE
from instagram_handler import (
    initialize_instagram_client,
    check_livestream,
    save_credentials
)
import shared_state

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
        "▫️ `/status` - Checks if the bot is currently logged in to Instagram.\n\n"
        "After a successful login, you can send me a username to check if they are live."
    )

@app.on_message(filters.command("setlogin"))
async def set_login_handler(client: PyrogramClient, message: Message):
    """Handles setting the Instagram username."""
    try:
        username = message.text.split(" ", 1)[1].strip()
        shared_state.ig_credentials["username"] = username
        save_credentials()
        await message.reply_text(f"✅ Instagram username has been set to: `{username}`.")

        if "password" in shared_state.ig_credentials and shared_state.ig_credentials["password"]:
            # print('logging')
            await initialize_instagram_client(message)
        else:
            await message.reply_text("Now, please set the password using `/setpassword <password>`.")
    except IndexError:
        await message.reply_text("Incorrect usage. Format: `/setlogin <username>`")

@app.on_message(filters.command("setpassword"))
async def set_password_handler(client: PyrogramClient, message: Message):
    """Handles setting the Instagram password and deletes the message for security."""
    try:
        password = message.text.split(" ", 1)[1].strip()
        shared_state.ig_credentials["password"] = password
        save_credentials()

        confirmation_msg = await message.reply_text("✅ Instagram password has been set. Your message with the password will be deleted shortly.")

        if "username" in shared_state.ig_credentials and shared_state.ig_credentials["username"]:
            # print('logging')
            await initialize_instagram_client(confirmation_msg)
        else:
            await confirmation_msg.reply_text("Now, please set the username using `/setlogin <username>`.")

        await asyncio.sleep(2)
        await message.delete()
    except IndexError:
        await message.reply_text("Incorrect usage. Format: `/setpassword <password>`")

@app.on_message(filters.command("login"))
async def login_command_handler(client: PyrogramClient, message: Message):
    """Manually triggers the login process."""
    if "username" in shared_state.ig_credentials and "password" in shared_state.ig_credentials:
        await initialize_instagram_client(message)
        # print('logging')
        print(shared_state.ig_credentials)
    else:
        await message.reply_text(
            "❌ **Cannot log in:** Credentials are not set.\n\n"
            "Please use `/setlogin <username>` and `/setpassword <password>` first."
        )

@app.on_message(filters.command("status"))
async def status_command_handler(client: PyrogramClient, message: Message):
    """Checks the current login status for Instagram."""
    if shared_state.instagrapi_client:
        await message.reply_text("✅ The bot is successfully logged in to Instagram.")
    else:
        await message.reply_text("❌ The bot is not logged in to Instagram. Use /setlogin and /setpassword, then /login.")

# --- Main Message Handler ---
@app.on_message(filters.text & filters.private & ~filters.command(["start", "setlogin", "setpassword", "login", "status"]))
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
                                 f"\n\n**Link to the MPD manifest:**\n`{result['mpd_url']}`")
            else:
                response_text = f"❌ **No, `{username}` is not live streaming.**"
        else:
            response_text = f"⚠️ **Error:** {result['message']}"

        await processing_message.edit_text(response_text, disable_web_page_preview=True)

    except CRITICAL_INSTAGRAM_EXCEPTIONS as _e:
        print("\n--- A CRITICAL ERROR OCCURRED DURING BOT OPERATION. ---")
        shared_state.instagrapi_client = None # Reset the client
        if SESSION_FILE.exists(): SESSION_FILE.unlink()
        if CREDENTIALS_FILE.exists(): CREDENTIALS_FILE.unlink()
        shared_state.ig_credentials = {}
        print("[Credentials] Deleted credentials file due to a critical session error.")
        await processing_message.edit_text(
            f"⚠️ **Critical Error:** A problem occurred with the Instagram session (e.g., logout). The session and credentials have been reset. Please configure and log in again.\n\n`{_e}`")
