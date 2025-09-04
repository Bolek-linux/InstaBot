# TelegramBot/handlers/commands/insta_conf_commands.py
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

# --- Local Imports ---
from config import SESSION_FILE, CREDENTIALS_FILE
from instagram_handler import save_credentials, attempt_login

import shared_state


logger = logging.getLogger(__name__)


@Client.on_message(filters.command("setlogin"))
async def set_login_handler(client: Client, message: Message):
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


@Client.on_message(filters.command("setpassword"))
async def set_password_handler(client: Client, message: Message):
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


@Client.on_message(filters.command("login"))
async def login_command_handler(client: Client, message: Message):
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


@Client.on_message(filters.command("logout"))
async def logout_command_handler(client: Client, message: Message):
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


@Client.on_message(filters.command("status"))
async def status_command_handler(client: Client, message: Message):
    """Checks the current login status for Instagram."""
    if shared_state.instagrapi_client:
        await message.reply_text("✅ The bot is successfully logged in to Instagram.")
    else:
        await message.reply_text(
            "❌ The bot is not logged in to Instagram. Use /setlogin and /setpassword, then /login.")