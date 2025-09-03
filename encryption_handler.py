# encryption_handler.py
"""
This module handles the encryption and decryption of sensitive data,
such as the Instagram credentials file. It uses the AES-GCM algorithm
provided by the 'cryptography' library's Fernet implementation.
"""

import logging
import os
import json
from cryptography.fernet import Fernet, InvalidToken


logger = logging.getLogger(__name__)


# The encryption key is loaded from an environment variable for security.
# Storing sensitive keys directly in the code is highly discouraged.
key = os.getenv("ENCRYPTION_KEY")
if not key:
    raise ValueError("ENCRYPTION_KEY is not set in the environment variables.")

cipher_suite = Fernet(key.encode())


def encrypt_data(data: dict) -> bytes:
    """
    Encrypts a dictionary by first serializing it to a JSON string.

    Parameters
    ----------
    data : dict
        The dictionary to encrypt.

    Returns
    -------
    bytes
        The encrypted data as bytes.
    """
    # The dictionary is converted to a JSON string, then to bytes for encryption.
    plaintext = json.dumps(data).encode('utf-8')
    return cipher_suite.encrypt(plaintext)


def decrypt_data(encrypted_data: bytes) -> dict:
    """
    Decrypts data and parses it back into a dictionary from a JSON string.

    Parameters
    ----------
    encrypted_data : bytes
        The encrypted data to decrypt.

    Returns
    -------
    dict
        The decrypted dictionary. Returns an empty dictionary if decryption fails
        (e.g., due to an invalid key or corrupted data).
    """
    try:
        decrypted_plaintext = cipher_suite.decrypt(encrypted_data)
        # The decrypted bytes are converted back to a string, then parsed as JSON.
        return json.loads(decrypted_plaintext.decode('utf-8'))
    except InvalidToken:
        logger.error("[Encryption] Decryption failed: Invalid token or key. Returning empty credentials.")
        return {}
    except Exception as e:
        logger.error(f"[Encryption] An unexpected error occurred during decryption: {e}")
        return {}