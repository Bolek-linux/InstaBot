# instagram_handler.py
"""
This module handles all interactions with the Instagrapi library,
including credential management, login procedures, and live stream checks.
"""

import asyncio

from pyrogram.types import Message

# --- Integration libraries ---
from instagrapi import Client as InstagrapiClient

# --- Instagrapi exception imports ---
from instagrapi.exceptions import (
    UserNotFound, FeedbackRequired, BadPassword,
    LoginRequired, ChallengeRequired, SentryBlock,
    ProxyAddressIsBlocked, ClientForbiddenError
)

# --- Local Imports ---
from config import (
    CREDENTIALS_FILE, SESSION_FILE,
    CRITICAL_INSTAGRAM_EXCEPTIONS
)
import shared_state
from encryption_handler import encrypt_data, decrypt_data


# --- Credential Management Logic ---
def load_credentials():
    """
    Loads and decrypts Instagram credentials from the credentials file into the shared state.
    """
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, "rb") as f:  # Open in binary read mode
            encrypted_data = f.read()
        shared_state.ig_credentials = decrypt_data(encrypted_data)
        print("[Credentials] Decrypted credentials loaded from file.")
    else:
        print("[Credentials] credentials.json file not found.")

def save_credentials():
    """
    Encrypts and saves the current Instagram credentials from shared state to the credentials file.
    """
    encrypted_data = encrypt_data(shared_state.ig_credentials)
    with open(CREDENTIALS_FILE, "wb") as f:  # Open in binary write mode
        f.write(encrypted_data)
    print("[Credentials] Encrypted credentials saved to file.")


# --- Instagram Login Logic ---
def perform_instagram_login(username, password) -> InstagrapiClient:
    """
    Handles the blocking login process for Instagrapi.

    This function attempts to log in using an existing session file or
    by creating a new one with the provided username and password. This function
    is designed to be run in a separate thread to avoid blocking the bot's event loop.

    Parameters
    ----------
    username : str
        The Instagram username.
    password : str
        The Instagram password.

    Returns
    -------
    InstagrapiClient
        An authenticated instagrapi.Client instance.

    Raises
    ------
    CRITICAL_INSTAGRAM_EXCEPTIONS
        If a critical, unrecoverable login error occurs.
    """
    client = InstagrapiClient()
    if SESSION_FILE.exists():
        client.load_settings(SESSION_FILE)
        print("[Instagrapi] Session loaded from file.")
        client.login(username, password)
        client.get_timeline_feed()  # Verify that the session is valid
        print("[Instagrapi] Session is still valid.")
    else:
        client.login(username, password)
        print("[Instagrapi] Logged in for the first time.")
        client.dump_settings(SESSION_FILE)
        print(f"[Instagrapi] New session has been saved to {SESSION_FILE.name}.")
    return client

async def initialize_instagram_client(message: Message):
    """
    Asynchronous wrapper to initialize the Instagrapi client.

    It orchestrates the login process, handles all critical exceptions,
    and informs the user about the outcome via a Telegram message.

    Parameters
    ----------
    message : Message
        The Pyrogram message object to reply to with status updates.
    """
    shared_state.instagrapi_client = None  # Reset client before attempting to log in

    username = shared_state.ig_credentials.get("username")
    password = shared_state.ig_credentials.get("password")

    if not (username and password):
        await message.reply_text("Missing username or password. Use /setlogin and /setpassword.")
        return

    await message.reply_text("Credentials received. Attempting to log in to Instagram...")

    try:
        new_client = await asyncio.to_thread(perform_instagram_login, username, password)
        shared_state.instagrapi_client = new_client
        print("[Instagrapi] Successfully logged in and initialized the client.")
        await message.reply_text("✅ Successfully logged in to Instagram!")

    except BadPassword as e:
        print("--- CRITICAL ERROR: Invalid password. ---")
        if SESSION_FILE.exists(): SESSION_FILE.unlink()
        if CREDENTIALS_FILE.exists(): CREDENTIALS_FILE.unlink()
        shared_state.ig_credentials = {}
        print("[Credentials] Deleted file with invalid credentials.")
        await message.reply_text(f"⚠️ **Login Failed:** Invalid password. Your credentials have been cleared. Please set them again.\n\n`{e}`")
    except LoginRequired as e:
        print("--- CRITICAL ERROR: Session has expired or is invalid. ---")
        if SESSION_FILE.exists(): SESSION_FILE.unlink()
        if CREDENTIALS_FILE.exists(): CREDENTIALS_FILE.unlink()
        shared_state.ig_credentials = {}
        print("[Credentials] Deleted credentials file due to expired session.")
        await message.reply_text(f"⚠️ **Login Failed:** Session expired. Your credentials have been cleared. Please set them again.\n\n`{e}`")
    except ChallengeRequired as e:
        print("--- CRITICAL ERROR: Account verification (checkpoint) required. ---")
        await message.reply_text(f"⚠️ **Login Failed:** Account verification required (checkpoint). Please log in via the app or browser to resolve this.\n\n`{e}`")
    except (SentryBlock, ProxyAddressIsBlocked) as e:
        print("--- CRITICAL ERROR: IP address has been blocked. ---")
        await message.reply_text(f"⚠️ **Login Failed:** Your IP address has been blocked by Instagram. Please change your proxy or IP address.\n\n`{e}`")
    except ClientForbiddenError as e:
        print("--- CRITICAL ERROR: Instagram account may be suspended or disabled. ---")
        await message.reply_text(f"⚠️ **Login Failed:** It appears the Instagram account has been suspended or disabled.\n\n`{e}`")
    except CRITICAL_INSTAGRAM_EXCEPTIONS as e:
        print(f"--- CRITICAL ERROR: A critical login error occurred: {e} ---")
        await message.reply_text(f"⚠️ **Login Failed:** A critical error prevented login.\n\n`{e}`")
    except Exception as e:
        print(f"--- CRITICAL ERROR: An unexpected error occurred during login: {e} ---")
        await message.reply_text(f"⚠️ **Critical Error:** An unexpected error occurred during login.\n\n`{e}`")


# --- Instagrapi Core Function ---
def check_livestream(cl: InstagrapiClient, username: str) -> dict:
    """
    Checks if a given Instagram user is currently live-streaming.

    Handles non-critical errors gracefully and re-raises critical exceptions
    that indicate a session-wide problem.

    Parameters
    ----------
    cl : InstagrapiClient
        An authenticated instagrapi.Client instance.
    username : str
        The Instagram username to check.

    Returns
    -------
    dict
        A dictionary containing the status of the check.
        On success: `{"status": "success", "live": True, ...}` or `{"status": "success", "live": False}`
        On error: `{"status": "error", "message": "..."}`
    """
    try:
        print(f"[Instagrapi] Checking live stream for {username}...")
        user_id = cl.user_id_from_username(username)
        response_data = cl.private_request(f"feed/user/{user_id}/story/")

        if broadcast_object := response_data.get("broadcast"):
            broadcast_id = broadcast_object.get("id")
            mpd_url = broadcast_object.get("dash_playback_url")
            print(f"[Instagrapi] Live stream found for {username}.")
            return {"status": "success", "live": True, "broadcast_id": broadcast_id, "mpd_url": mpd_url}
        else:
            print(f"[Instagrapi] User {username} is not broadcasting.")
            return {"status": "success", "live": False}

    except UserNotFound:
        print(f"[Instagrapi] ERROR: User {username} not found.")
        return {"status": "error", "message": f"User '{username}' not found.."}
    except FeedbackRequired as _e:
        print(f"[Instagrapi] ERROR: Action blocked (FeedbackRequired) while checking {username}.")
        return {"status": "error", "message": f"The bot's Instagram account is temporarily blocked. Please try again later.\n\n`{_e}`"}
    except CRITICAL_INSTAGRAM_EXCEPTIONS:
        raise  # Re-throw the exception to be handled globally
    except Exception as _e:
        print(f"[Instagrapi] An unexpected error occurred while checking {username}: {_e}")
        return {"status": "error", "message": f"An unexpected internal error occurred: {_e}"}