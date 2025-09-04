# TelegramBot/handlers/messages/text_message.py
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

# --- Local Imports ---
from config import CRITICAL_INSTAGRAM_EXCEPTIONS, SESSION_FILE, CREDENTIALS_FILE
from instagram_handler import check_livestream
import shared_state


logger = logging.getLogger(__name__)


@Client.on_message(
    filters.text & filters.private & ~filters.command(["start", "setlogin", "setpassword", "login", "status"]))
async def message_handler(client: Client, message: Message):
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