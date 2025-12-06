import hmac
import hashlib
import os

MAC_KEY_PATH = "mac_key.bin"


def load_or_create_mac_key():
    if os.path.exists(MAC_KEY_PATH):
        with open(MAC_KEY_PATH, "rb") as f:
            return f.read()
    else:
        key = os.urandom(32)
        with open(MAC_KEY_PATH, "wb") as f:
            f.write(key)
        return key


def compute_mac(message: str, key: bytes) -> bytes:
    """
    Retorna el MAC en bytes, NO hex. 
    """
    h = hmac.new(key, message.encode(), hashlib.sha256)
    return h.digest()   


def verify_mac(message: str, key: bytes, tag: bytes) -> bool:
    """
    Compara bytes vs bytes.
    """
    h = hmac.new(key, message.encode(), hashlib.sha256)
    expected = h.digest() 
    return hmac.compare_digest(expected, tag)
