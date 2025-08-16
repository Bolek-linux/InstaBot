# shared_state.py
"""
This module contains the shared state of the application to avoid circular imports.
It holds the global instance of the Instagrapi client and the Instagram credentials.
"""

from instagrapi import Client as InstagrapiClient

# Global variable for storing the instagrapi client instance.
# It's initialized as None and gets populated upon successful login.
instagrapi_client: InstagrapiClient | None = None

# Global dictionary for storing Instagram credentials in memory.
ig_credentials: dict = {}