# chat_app/utils/crypto.py
import os
import base64
from typing import Union
from django.conf import settings
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Recommended: store a base64-encoded 32-byte key in settings.AES_KEY_B64
def _get_key() -> bytes:
    key_b64 = getattr(settings, "AES_KEY_B64", None)
    if not key_b64:
        raise ValueError("AES_KEY_B64 is not configured in settings")
    if isinstance(key_b64, str):
        return base64.b64decode(key_b64)
    return key_b64  # already bytes

def encrypt(plaintext: Union[str, bytes]) -> str:
    """
    Encrypt plaintext (str or bytes). Returns base64 string containing nonce||ciphertext.
    """
    if isinstance(plaintext, str):
        plaintext = plaintext.encode("utf-8")
    key = _get_key()
    if len(key) not in (16, 24, 32):
        raise ValueError("Invalid AES key length; expected 16, 24 or 32 bytes")
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce recommended for AESGCM
    ct = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    blob = nonce + ct
    return base64.b64encode(blob).decode("utf-8")

def decrypt(token_b64: str) -> bytes:
    """
    Decrypt a base64 token produced by encrypt(). Returns bytes; decode to text as needed.
    """
    if not token_b64:
        return b""
    blob = base64.b64decode(token_b64)
    nonce = blob[:12]
    ct = blob[12:]
    key = _get_key()
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, associated_data=None)

#models,crypto,settings