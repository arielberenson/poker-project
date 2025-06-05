import os
from dotenv import load_dotenv
# Then use this key to initialize your Encryptor
from cryptography.fernet import Fernet

load_dotenv()  # take environment variables from .env.

FERNET_KEY = os.getenv('FERNET_KEY').encode()  # remember to encode to bytes


class Encryptor:
    def __init__(self, key):
        self.cipher = Fernet(key)

    def encrypt(self, message: str) -> bytes:
        return self.cipher.encrypt(message.encode())

    def decrypt(self, encrypted_message: bytes) -> str:
        return self.cipher.decrypt(encrypted_message).decode()
