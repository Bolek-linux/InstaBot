# TelegramBot/handlers/messages/text_message.py
import asyncio
import logging
import re

from pyrogram import Client, filters
from pyrogram.types import Message

# --- Local Imports ---
from config import CRITICAL_INSTAGRAM_EXCEPTIONS, SESSION_FILE, CREDENTIALS_FILE
from instagram_handler import check_livestream
import shared_state


logger = logging.getLogger(__name__)


def is_valid_instagram_username(username: str) -> bool:
    """
    Checks if a string adheres to Instagram's username rules.

    According to Instagram's policies, a username must be between 1 and 30
    characters long. It can only contain letters, numbers, periods (.),
    and underscores (_). It cannot start or end with a period, nor can it
    contain consecutive periods.

    Args:
        username (str): The username string to validate.

    Returns:
        bool: True if the username is valid, False otherwise.
    """
    # 1. Check length constraints (1 to 30 characters).
    if not 1 <= len(username) <= 30:
        return False

    # 2. Check for invalid start or end characters (period).
    if username.startswith('.') or username.endswith('.'):
        return False

    # 3. Use regex to ensure only allowed characters are present and check for
    #    the consecutive periods rule, which regex doesn't easily cover.
    allowed_chars_pattern = re.compile(r"^[a-zA-Z0-9_.]+$")
    if not allowed_chars_pattern.match(username) or '..' in username:
        return False

    return True


def extract_instagram_username(input_string: str) -> str | None:
    """
    Extracts and validates an Instagram username from a URL or a raw string.

    This function handles various Instagram URL formats (e.g., profiles,
    live broadcasts, posts) and also validates direct username strings,
    which may or may not include an '@' prefix.

    Args:
        input_string (str): The full Instagram URL or a potential username string.

    Returns:
        str | None: The validated username if found, otherwise None.
    """
    # This regex captures the username from common Instagram URL patterns.
    # It looks for the string between "instagram.com/" and the next "/" or
    # the end of the string, which is where the username is consistently located.
    url_pattern = re.compile(
        r"^(?:https?://)?(?:www\.)?instagram\.com/(?P<username>[a-zA-Z0-9_.]+)"
    )

    match = url_pattern.match(input_string)

    potential_username = ""

    if match:
        # If the input is a URL that matches the pattern, extract the named group.
        potential_username = match.group("username")
    else:
        # If not a URL, treat the entire input as a potential username.
        # Remove the '@' prefix if it exists.
        potential_username = input_string.lstrip('@')

    # Regardless of the source, validate the potential username against the rules.
    if is_valid_instagram_username(potential_username):
        return potential_username

    # Return None if no valid username can be derived from the input string.
    return None


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

    username = extract_instagram_username(message.text)
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