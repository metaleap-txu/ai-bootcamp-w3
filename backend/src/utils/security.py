"""Security utilities for password encryption and decryption."""
import os
from pathlib import Path

from cryptography.fernet import Fernet

# Encryption key path in user's home directory
KEY_DIR = Path.home() / ".db_query"
KEY_PATH = KEY_DIR / "secret.key"


def ensure_encryption_key() -> None:
    """Ensure encryption key exists, create if it doesn't."""
    KEY_DIR.mkdir(parents=True, exist_ok=True)
    
    if not KEY_PATH.exists():
        # Generate new encryption key
        key = Fernet.generate_key()
        KEY_PATH.write_bytes(key)
        # Set restrictive permissions (owner read/write only)
        os.chmod(KEY_PATH, 0o600)


def get_cipher() -> Fernet:
    """
    Load encryption key and create cipher instance.
    
    Returns:
        Fernet: Cipher instance for encryption/decryption
        
    Raises:
        FileNotFoundError: If encryption key doesn't exist
    """
    ensure_encryption_key()
    key = KEY_PATH.read_bytes()
    return Fernet(key)


def encrypt_password(password: str) -> str:
    """
    Encrypt a password for secure storage.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Base64-encoded encrypted password
        
    Example:
        >>> encrypted = encrypt_password("my_secret_password")
        >>> encrypted.startswith("gAAAAA")  # Fernet ciphertext prefix
        True
    """
    cipher = get_cipher()
    encrypted_bytes = cipher.encrypt(password.encode())
    return encrypted_bytes.decode()


def decrypt_password(encrypted_password: str) -> str:
    """
    Decrypt an encrypted password.
    
    Args:
        encrypted_password: Base64-encoded encrypted password
        
    Returns:
        str: Plain text password
        
    Raises:
        cryptography.fernet.InvalidToken: If encrypted_password is invalid
        
    Example:
        >>> encrypted = encrypt_password("my_secret_password")
        >>> decrypted = decrypt_password(encrypted)
        >>> decrypted == "my_secret_password"
        True
    """
    cipher = get_cipher()
    decrypted_bytes = cipher.decrypt(encrypted_password.encode())
    return decrypted_bytes.decode()
