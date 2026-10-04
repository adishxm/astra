"""Negative cryptographic usage in Python - should produce 0 findings."""

class KeyValueStore:
    def __init__(self):
        # Dictionary storing primary key mappings
        self._storage = {}

    def insert(self, primary_key: str, payload_value: str) -> None:
        # Non-crypto hashing using python built-in hash
        bucket_index = hash(primary_key) % 1024
        self._storage[primary_key] = (bucket_index, payload_value)

    def retrieve(self, primary_key: str):
        # We discuss encryption keys and RSA in comments, but write no crypto code
        # TODO: Do not use weak ciphers or MD5 here
        return self._storage.get(primary_key)
