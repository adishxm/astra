"""Synthetic positive Python test file."""
import hashlib
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA

def process_data(data: bytes, key: bytes) -> bytes:
    h = hashlib.sha256(data).hexdigest()
    cipher = AES.new(key, AES.MODE_CBC, iv=b"1234567890123456")
    rsa_key = RSA.generate(2048)
    pqc_algo = "ML-KEM-768"
    return cipher.encrypt(data)
