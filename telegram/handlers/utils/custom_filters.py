# telegram/handlers/utils/custom_filters.py
"""
This module defines a custom Pyrogram filter to detect a secret command
by comparing its hash with a stored value.
"""
import logging
from pyrogram import filters
from pyrogram.types import Message
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from core.config import HASHED_SECRET_COMMAND

# Get a logger instance for this module.
logger = logging.getLogger(__name__)

# Initialize the PasswordHasher once at the module level for efficiency.
ph = PasswordHasher()


async def _secret_command_filter(_, __, message: Message) -> bool:
    """
    Verifies if the message text matches the stored secret command hash.

    This function is the core logic for the custom filter. It checks the
    plaintext of a message against the Argon2 hash stored in the configuration.

    Returns
    -------
    bool
        True if the message text matches the hash, False otherwise.
    """
    # The filter should only process text messages.
    if not message.text:
        return False

    # Ensure the hashed command is configured before attempting to verify.
    if not HASHED_SECRET_COMMAND:
        # ZMIANA: Zastąpiono print() loggerem.
        logger.warning("[Filter] Secret command filter triggered, but HASHED_SECRET_COMMAND is not set in config.")
        return False

    try:
        # Verify the message text against the stored hash.
        ph.verify(HASHED_SECRET_COMMAND, message.text)
        logger.debug(f"[Filter] Secret command successfully verified for user {message.from_user.id}.")
        return True
    except VerifyMismatchError:
        # This is expected when the text does not match; not an error.
        return False
    except Exception as e:
        # Log any other unexpected errors during Argon2 verification.
        logger.error(f"[Filter] An unexpected error occurred during Argon2 verification: {e}")
        return False


# Create a Pyrogram filter instance from the logic function.
# This instance can then be imported and used in message handlers.
secret_command_filter = filters.create(_secret_command_filter)