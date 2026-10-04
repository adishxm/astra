"""Positive cryptographic usage in Python."""
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def generate_key():
    # RSA-2048 keypair generation
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    return private_key

def encrypt_data(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    # AES-256 cipher in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    return encryptor.update(plaintext) + encryptor.finalize()

def calculate_checksums(data: bytes):
    # Deprecated MD5 and modern SHA-256
    legacy_md5 = hashlib.md5(data).hexdigest()
    secure_sha256 = hashlib.sha256(data).hexdigest()
    return legacy_md5, secure_sha256
