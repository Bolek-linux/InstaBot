# TelegramBot/handlers/commands/start_command.py
from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
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