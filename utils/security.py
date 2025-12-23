import os
from cryptography.fernet import Fernet

KEY_PATH = 'resources/data/secret.key'
os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)

def _load_key():
    """Loads the key from the key file or generates a new one."""
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, 'rb') as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_PATH, 'wb') as key_file:
            key_file.write(key)
        return key

_key = _load_key()
_cipher_suite = Fernet(_key)

def encrypt_data(data: bytes) -> bytes:
    """Encrypts the given data."""
    return _cipher_suite.encrypt(data)

def decrypt_data(token: bytes) -> bytes:
    """Decrypts the given token."""
    return _cipher_suite.decrypt(token)
