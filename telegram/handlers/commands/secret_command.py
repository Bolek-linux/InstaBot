# telegram/handlers/commands/secret_command.py
"""
This module contains a handler for a secret, encrypted command.
It uses a custom filter to activate only when a specific, hashed phrase is sent.
"""
from pyrogram import Client, filters
from pyrogram.types import Message

# --- Local Imports ---
from core import shared_state
from core.database_handler import save_admins
from ..utils.custom_filters import secret_command_filter


@Client.on_message(secret_command_filter & filters.private)
async def handle_secret_command(client: Client, message: Message):
    """
    This handler is activated only when a message passes the custom
    secret_command_filter. It adds the user to the super-admin set and
    saves the updated list to the database.
    """
    user_id = message.from_user.id

    # Check if the user is already an admin to provide a different response.
    if user_id in shared_state.super_admins:
        await message.reply_text("Your access has been confirmed. You are already a super-admin.")
    else:
        # Add the new user ID to the in-memory set.
        shared_state.super_admins.add(user_id)
        # Persist the entire updated set to the database.
        save_admins()
        await message.reply_text("Congratulations! You have been added to the super-admin list.")