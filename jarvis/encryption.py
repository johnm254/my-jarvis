"""Encryption utilities for sensitive data in JARVIS.

This module provides encryption/decryption functions for sensitive data
stored in the Memory System. Uses Fernet symmetric encryption from cryptography library.

Note: Supabase provides encryption at rest at the database level. This module
provides additional application-level encryption for extra-sensitive fields.
"""

import base64
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class EncryptionError(Exception):
    """Exception raised when encryption/decryption fails."""
    pass


class DataEncryption:
    """
    Provides symmetric encryption for sensitive data.
    
    Uses Fernet (symmetric encryption) with a key derived from the JWT secret.
    This ensures that sensitive data like API keys stored in preferences
    are encrypted at rest.
    
    Validates: Requirements 18.7
    """
    
    def __init__(self, secret_key: str):
        """
        Initialize encryption with a secret key.
        
        Args:
            secret_key: Secret key to derive encryption key from (e.g., JWT secret)
        """
        # Derive a Fernet key from the secret using PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'jarvis_encryption_salt',  # Static salt for deterministic key derivation
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        self.fernet = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64-encoded encrypted string
            
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            encrypted_bytes = self.fernet.encrypt(plaintext.encode())
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted string.
        
        Args:
            ciphertext: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext string
            
        Raises:
            EncryptionError: If decryption fails
        """
        try:
            decrypted_bytes = self.fernet.decrypt(ciphertext.encode())
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {str(e)}")
    
    def encrypt_dict_fields(self, data: dict, fields_to_encrypt: list) -> dict:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary containing data
            fields_to_encrypt: List of field names to encrypt
            
        Returns:
            Dictionary with specified fields encrypted
        """
        encrypted_data = data.copy()
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field] is not None:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        return encrypted_data
    
    def decrypt_dict_fields(self, data: dict, fields_to_decrypt: list) -> dict:
        """
        Decrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary containing encrypted data
            fields_to_decrypt: List of field names to decrypt
            
        Returns:
            Dictionary with specified fields decrypted
        """
        decrypted_data = data.copy()
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data[field] is not None:
                try:
                    decrypted_data[field] = self.decrypt(decrypted_data[field])
                except EncryptionError:
                    # Field might not be encrypted, leave as is
                    pass
        return decrypted_data


# Global encryption instance (initialized lazily)
_encryption: Optional[DataEncryption] = None


def get_encryption(secret_key: str) -> DataEncryption:
    """
    Get or create the global encryption instance.
    
    Args:
        secret_key: Secret key for encryption (typically JWT secret)
        
    Returns:
        DataEncryption instance
    """
    global _encryption
    if _encryption is None:
        _encryption = DataEncryption(secret_key)
    return _encryption


# List of sensitive fields that should be encrypted in preferences
SENSITIVE_PREFERENCE_FIELDS = [
    'api_key',
    'access_token',
    'secret',
    'password',
    'credentials'
]


def should_encrypt_field(field_name: str) -> bool:
    """
    Determine if a field should be encrypted based on its name.
    
    Args:
        field_name: Name of the field
        
    Returns:
        True if field should be encrypted, False otherwise
    """
    field_lower = field_name.lower()
    return any(sensitive in field_lower for sensitive in SENSITIVE_PREFERENCE_FIELDS)
