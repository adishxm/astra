"""Holdout Python verification with alternate primitives."""
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.asymmetric import ec

def generate_ecc_key():
    # Quantum-vulnerable ECDSA on SECP256R1
    curve = ec.SECP256R1()
    private_key = ec.generate_private_key(curve)
    return private_key

def seal_payload(key: bytes, nonce: bytes, data: bytes) -> bytes:
    # ChaCha20 cipher usage
    chacha = ChaCha20Poly1305(key)
    return chacha.encrypt(nonce, data, None)
