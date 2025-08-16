from cryptography.fernet import Fernet
# Generates a new, secure key
key = Fernet.generate_key()
print(f"Your new encryption key: {key.decode()}")