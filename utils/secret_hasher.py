# utils/secret_hasher.py
"""
A utility script to generate a secure Argon2 hash for a secret command.

This script prompts the user for a secret command phrase and generates a hash
that can be stored in the .env file. The application uses this hash to verify
the command without exposing the plaintext secret in the code or configuration.
"""
# ZMIANA: Cały plik został przepisany, aby był zgodny ze standardami projektu.
from argon2 import PasswordHasher


def main():
    """
    Prompts for a secret command, hashes it, and prints the result.
    """
    # Initialize the PasswordHasher from the argon2 library.
    ph = PasswordHasher()

    # Prompt the user to enter the secret command they wish to hash.
    secret_command = input("Enter the secret command to generate a hash for: ")

    # Generate the Argon2 hash of the provided command.
    hashed_command = ph.hash(secret_command)

    # Display the results to the user.
    print("\n--- Generated Hash ---")
    print(f"Your secret command: {secret_command}")
    print(f"Its Argon2 hash: {hashed_command}")
    print("\nIMPORTANT: Copy the full hash and add it to your .env file as:")
    print(f'HASHED_SECRET_COMMAND="{hashed_command}"')


# Ensure the script runs only when executed directly.
if __name__ == "__main__":
    main()