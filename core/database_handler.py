# core/database_handler.py
"""
This module handles all database operations for the application,
such as initializing the database and managing the admins table.
"""
import sqlite3
import logging
from pathlib import Path

# --- Local Imports ---
from .config import DATABASE_FILE
from . import shared_state

# Get a logger instance for this module.
logger = logging.getLogger(__name__)


def initialize_database():
    """
    Initializes the SQLite database and creates the necessary tables if they don't exist.
    This function should be called once at application startup.
    """
    try:
        # The 'with' statement ensures the connection is closed even if errors occur.
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            # Create the 'admins' table.
            # 'user_id' is an integer and the primary key for uniqueness.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    user_id INTEGER PRIMARY KEY
                );
            """)
            # The commit is automatic when the 'with' block exits successfully.
        logger.info("[Database] Database initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"[Database] An error occurred during database initialization: {e}")


def load_admins():
    """
    Loads all admin user_ids from the database into the shared_state.super_admins set.
    This is called at startup to populate the in-memory admin list.
    """
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT user_id FROM admins;")
            # fetchall() returns a list of tuples, e.g., [(123,), (456,)]
            rows = cursor.fetchall()

            # Use a set comprehension to efficiently populate the in-memory set.
            shared_state.super_admins = {row[0] for row in rows}

        logger.info(f"[Database] Loaded {len(shared_state.super_admins)} admins from the database.")
    except sqlite3.Error as e:
        logger.error(f"[Database] An error occurred while loading admins: {e}")


def save_admins():
    """
    Saves the current set of admin user_ids from shared_state into the database.
    This function overwrites the existing table content to ensure consistency.
    """
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            # Prepare data for executemany, which requires a list of tuples.
            admin_ids_to_save = [(admin_id,) for admin_id in shared_state.super_admins]

            # The 'with' block automatically handles the transaction.
            # If any command fails, the transaction is rolled back.
            # If all commands succeed, it's committed upon exiting the block.
            cursor.execute("DELETE FROM admins;")
            cursor.executemany("INSERT INTO admins (user_id) VALUES (?);", admin_ids_to_save)

        logger.info(f"[Database] Saved {len(admin_ids_to_save)} admins to the database.")
    except sqlite3.Error as e:
        logger.error(f"[Database] An error occurred while saving admins: {e}")