
# telegram/handlers/commands/secret_command.py
"""
This module contains a handler for a secret, encrypted command.
It uses a custom filter to activate only when a specific, hashed phrase is sent.
"""
from pyrogram import Client, filters
from pyrogram.types import Message
# Import the custom filter from its location within the handlers' structure.
from ..utils.custom_filters import secret_command_filter


@Client.on_message(secret_command_filter & filters.private)
async def handle_secret_command(client: Client, message: Message):
    """
    This handler is activated only when a message passes the custom
    secret_command_filter, ensuring it only responds to the correct secret phrase.
    """
    # Respond to the user, confirming that the secret command was successful.
    await message.reply_text("Congratulations! You have activated the secret, encrypted command!")