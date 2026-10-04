import os
import json
import datetime
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

CORPUS_ROOT = Path("backend/tests/fixtures/corpus").resolve()
os.makedirs(CORPUS_ROOT, exist_ok=True)

# 1. Python fixtures
py_dir = CORPUS_ROOT / "python"
py_dir.mkdir(parents=True, exist_ok=True)

(py_dir / "crypto_positive.py").write_text('''"""Positive cryptographic usage in Python."""
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
''', encoding="utf-8")

(py_dir / "crypto_negative.py").write_text('''"""Negative cryptographic usage in Python - should produce 0 findings."""

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
''', encoding="utf-8")

# 2. JavaScript fixtures
js_dir = CORPUS_ROOT / "javascript"
js_dir.mkdir(parents=True, exist_ok=True)

(js_dir / "crypto_positive.js").write_text('''/**
 * Positive cryptographic usage in Node.js / JavaScript.
 */
const crypto = require('crypto');

function createAesCipher(secretKey, iv) {
    // AES-256 encryption
    return crypto.createCipheriv('aes-256-gcm', secretKey, iv);
}

function computeHashes(buffer) {
    // SHA-256 and legacy MD5
    const sha256 = crypto.createHash('sha256').update(buffer).digest('hex');
    const md5 = crypto.createHash('md5').update(buffer).digest('hex');
    return { sha256, md5 };
}

function verifyRsaSignature(publicKey, signature, data) {
    // RSA-2048 signature verification
    const verifier = crypto.createVerify('RSA-SHA256');
    verifier.update(data);
    return verifier.verify(publicKey, signature);
}

module.exports = { createAesCipher, computeHashes, verifyRsaSignature };
''', encoding="utf-8")

(js_dir / "crypto_negative.js").write_text('''/**
 * Negative cryptographic fixture in JavaScript.
 * Mentions crypto concepts in comments only.
 */

function formatUserKey(userId, keyPrefix) {
    // Variable name contains 'key', but no cryptographic algorithm is used
    // This function formats a composite cache key
    const cacheKey = `${keyPrefix}_user_${userId}`;
    return cacheKey.toLowerCase();
}

function calculateSum(numbers) {
    // Pure arithmetic
    return numbers.reduce((acc, curr) => acc + curr, 0);
}

module.exports = { formatUserKey, calculateSum };
''', encoding="utf-8")

# 3. Go fixtures
go_dir = CORPUS_ROOT / "go"
go_dir.mkdir(parents=True, exist_ok=True)

(go_dir / "crypto_positive.go").write_text('''package main

import (
	"crypto/aes"
	"crypto/md5"
	"crypto/rsa"
	"crypto/sha256"
	"fmt"
)

func RunCryptoRoutines() {
	// AES-256 block cipher initialization
	key := make([]byte, 32)
	block, err := aes.NewCipher(key)
	if err != nil {
		panic(err)
	}
	_ = block

	// RSA-2048 key declaration
	rsaKeySize := "RSA-2048"
	fmt.Println(rsaKeySize)

	// SHA-256 and MD5 hashing
	h := sha256.New()
	m := md5.New()
	_ = h
	_ = m
}
''', encoding="utf-8")

(go_dir / "crypto_negative.go").write_text('''package main

import (
	"fmt"
	"strings"
)

// Negative fixture: Mentions keys and tokens in business logic
func GenerateApiKeyFormat(prefix string, id int64) string {
	// Formats an ID with a prefix
	return fmt.Sprintf("%s-%d", strings.ToUpper(prefix), id)
}

func ProcessTransactions(amounts []float64) float64 {
	total := 0.0
	for _, a := range amounts {
		total += a
	}
	return total
}
''', encoding="utf-8")

# 4. Java fixture
java_dir = CORPUS_ROOT / "java"
java_dir.mkdir(parents=True, exist_ok=True)

(java_dir / "CryptoPositive.java").write_text('''package com.astra.test;

import java.security.KeyPairGenerator;
import java.security.MessageDigest;
import javax.crypto.Cipher;

public class CryptoPositive {
    public void setupCryptography() throws Exception {
        // RSA-2048 Key Pair Generator
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA-2048");

        // AES-256 Symmetric Encryption
        Cipher cipher = Cipher.getInstance("AES-256");

        // SHA-256 Hash Digest
        MessageDigest sha = MessageDigest.getInstance("SHA-256");

        // Deprecated MD5 Digest
        MessageDigest md5 = MessageDigest.getInstance("MD5");
    }
}
''', encoding="utf-8")

# 5. C fixture
c_dir = CORPUS_ROOT / "c"
c_dir.mkdir(parents=True, exist_ok=True)

(c_dir / "crypto_positive.c").write_text('''#include <stdio.h>

void execute_crypto_routines() {
    // OpenSSL EVP algorithm names
    const char *cipher_name = "AES-256";
    const char *asym_algo = "RSA-2048";
    const char *hash_algo = "SHA-256";
    const char *legacy_hash = "MD5";

    printf("Selected crypto: %s, %s, %s, %s\\n",
           cipher_name, asym_algo, hash_algo, legacy_hash);
}
''', encoding="utf-8")

# 6. Manifest fixtures
man_dir = CORPUS_ROOT / "manifests"
man_dir.mkdir(parents=True, exist_ok=True)

(man_dir / "package.json").write_text(json.dumps({
    "name": "astra-positive-npm",
    "version": "1.0.0",
    "dependencies": {
        "crypto-js": "^4.2.0",
        "node-forge": "^1.3.1"
    }
}, indent=2), encoding="utf-8")

(man_dir / "requirements.txt").write_text("""cryptography>=41.0.0
pycryptodome==3.19.0
""", encoding="utf-8")

clean_man_dir = man_dir / "clean"
clean_man_dir.mkdir(parents=True, exist_ok=True)
(clean_man_dir / "package.json").write_text(json.dumps({
    "name": "astra-clean-npm",
    "version": "1.0.0",
    "dependencies": {
        "express": "^4.19.2",
        "lodash": "^4.17.21"
    }
}, indent=2), encoding="utf-8")

# 7. Certificate fixtures
cert_dir = CORPUS_ROOT / "certificates"
cert_dir.mkdir(parents=True, exist_ok=True)

# Generate genuine RSA-2048 self-signed cert
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Delhi"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ASTRA Verification"),
    x509.NameAttribute(NameOID.COMMON_NAME, "astra-test-rsa2048.internal"),
])
cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(private_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
    .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
    .sign(private_key, hashes.SHA256())
)
cert_pem = cert.public_bytes(serialization.Encoding.PEM)
(cert_dir / "valid_rsa_cert.pem").write_bytes(cert_pem)

# Negative cert fixture (plain text file with .pem extension)
(cert_dir / "not_a_cert.pem").write_text("""This is plain text with no ASN.1 or cryptographic data.
It has no cert headers or base64 data.
""", encoding="utf-8")

# 8. Config fixtures
cfg_dir = CORPUS_ROOT / "configs"
cfg_dir.mkdir(parents=True, exist_ok=True)

(cfg_dir / "tls_positive.conf").write_text("""# Nginx TLS Configuration with strong and legacy parameters
server {
    listen 443 ssl;
    server_name secure.example.com;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers on;
}
""", encoding="utf-8")

(cfg_dir / "plain_nginx.conf").write_text("""# Plain web server without SSL/TLS configuration
server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
""", encoding="utf-8")

# 9. Holdout fixtures
holdout_dir = CORPUS_ROOT / "holdout"
holdout_dir.mkdir(parents=True, exist_ok=True)

(holdout_dir / "holdout_python.py").write_text('''"""Holdout Python verification with alternate primitives."""
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
''', encoding="utf-8")

(holdout_dir / "holdout_js.js").write_text('''/** Holdout JS test */
const crypto = require('crypto');

function encryptSecret(key, iv, text) {
    // AES-128 cipher
    const cipher = crypto.createCipheriv('aes-128-cbc', key, iv);
    return cipher.update(text, 'utf8', 'hex') + cipher.final('hex');
}

function hashData(buffer) {
    // SHA-512
    return crypto.createHash('sha512').update(buffer).digest('hex');
}

module.exports = { encryptSecret, hashData };
''', encoding="utf-8")

(holdout_dir / "holdout_go.go").write_text('''package main

import (
	"crypto/ed25519"
	"crypto/sha512"
)

func RunHoldout() {
	// Ed25519 signing
	pub, priv, _ := ed25519.GenerateKey(nil)
	_ = pub
	_ = priv

	// SHA-512 hashing
	h := sha512.New()
	_ = h
}
''', encoding="utf-8")

holdout_man_dir = holdout_dir / "manifests"
holdout_man_dir.mkdir(parents=True, exist_ok=True)
(holdout_man_dir / "package.json").write_text(json.dumps({
    "name": "holdout-dependencies",
    "version": "2.0.0",
    "dependencies": {
        "bcrypt": "^5.1.1",
        "tweetnacl": "^1.0.3"
    }
}, indent=2), encoding="utf-8")

(holdout_dir / "holdout_config.yaml").write_text("""server:
  tls_version: "TLSv1.3"
  algorithm: "AES"
""", encoding="utf-8")

(holdout_dir / "holdout_negative.py").write_text('''"""Holdout negative fixture with misleading variable names."""

class AuthSessionManager:
    """Manages sessions. Note: We use tokens rather than passwords."""
    
    def __init__(self):
        # 'secret_token' and 'encryption_key_id' in names
        self.secret_token = "abc123xyz"
        self.encryption_key_id = 9988

    def validate_session(self, user_agent: str) -> bool:
        # Standard string comparison
        return len(user_agent) > 10
''', encoding="utf-8")

# 10. Write labels.json
labels_data = {
    "corpus_version": "1.0",
    "training_set": [
        {
            "relative_path": "python/crypto_positive.py",
            "surface": "SOURCE_CODE",
            "is_negative": False,
            "expected_algorithms": ["RSA-2048", "AES-256", "MD5", "SHA-256"]
        },
        {
            "relative_path": "python/crypto_negative.py",
            "surface": "SOURCE_CODE",
            "is_negative": True,
            "expected_algorithms": []
        },
        {
            "relative_path": "javascript/crypto_positive.js",
            "surface": "SOURCE_CODE",
            "is_negative": False,
            "expected_algorithms": ["AES-256", "SHA-256", "MD5", "RSA-2048"]
        },
        {
            "relative_path": "javascript/crypto_negative.js",
            "surface": "SOURCE_CODE",
            "is_negative": True,
            "expected_algorithms": []
        },
        {
            "relative_path": "go/crypto_positive.go",
            "surface": "SOURCE_CODE",
            "is_negative": False,
            "expected_algorithms": ["AES-256", "RSA-2048", "SHA-256", "MD5"]
        },
        {
            "relative_path": "go/crypto_negative.go",
            "surface": "SOURCE_CODE",
            "is_negative": True,
            "expected_algorithms": []
        },
        {
            "relative_path": "java/CryptoPositive.java",
            "surface": "SOURCE_CODE",
            "is_negative": False,
            "expected_algorithms": ["RSA-2048", "AES-256", "SHA-256", "MD5"]
        },
        {
            "relative_path": "c/crypto_positive.c",
            "surface": "SOURCE_CODE",
            "is_negative": False,
            "expected_algorithms": ["AES-256", "RSA-2048", "SHA-256", "MD5"]
        },
        {
            "relative_path": "manifests/package.json",
            "surface": "MANIFEST",
            "is_negative": False,
            "expected_algorithms": ["crypto-js", "node-forge"]
        },
        {
            "relative_path": "manifests/requirements.txt",
            "surface": "MANIFEST",
            "is_negative": False,
            "expected_algorithms": ["cryptography", "pycryptodome"]
        },
        {
            "relative_path": "manifests/clean/package.json",
            "surface": "MANIFEST",
            "is_negative": True,
            "expected_algorithms": []
        },
        {
            "relative_path": "certificates/valid_rsa_cert.pem",
            "surface": "CERTIFICATE",
            "is_negative": False,
            "expected_algorithms": ["RSA-2048"]
        },
        {
            "relative_path": "certificates/not_a_cert.pem",
            "surface": "CERTIFICATE",
            "is_negative": True,
            "expected_algorithms": []
        },
        {
            "relative_path": "configs/tls_positive.conf",
            "surface": "CONFIG",
            "is_negative": False,
            "expected_algorithms": ["TLSv1.2", "TLSv1.3", "ECDHE-AES256-GCM", "ECDHE-AES128-GCM"]
        },
        {
            "relative_path": "configs/plain_nginx.conf",
            "surface": "CONFIG",
            "is_negative": True,
            "expected_algorithms": []
        }
    ],
    "holdout_set": [
        {
            "relative_path": "holdout/holdout_python.py",
            "surface": "SOURCE_CODE",
            "is_negative": False,
            "expected_algorithms": ["ECDSA", "ChaCha20"]
        },
        {
            "relative_path": "holdout/holdout_js.js",
            "surface": "SOURCE_CODE",
            "is_negative": False,
            "expected_algorithms": ["AES-128", "SHA-512"]
        },
        {
            "relative_path": "holdout/holdout_go.go",
            "surface": "SOURCE_CODE",
            "is_negative": False,
            "expected_algorithms": ["Ed25519", "SHA-512"]
        },
        {
            "relative_path": "holdout/manifests/package.json",
            "surface": "MANIFEST",
            "is_negative": False,
            "expected_algorithms": ["bcrypt", "tweetnacl"]
        },
        {
            "relative_path": "holdout/holdout_config.yaml",
            "surface": "CONFIG",
            "is_negative": False,
            "expected_algorithms": ["TLSv1.3", "AES"]
        },
        {
            "relative_path": "holdout/holdout_negative.py",
            "surface": "SOURCE_CODE",
            "is_negative": True,
            "expected_algorithms": []
        }
    ]
}

(CORPUS_ROOT / "labels.json").write_text(json.dumps(labels_data, indent=2), encoding="utf-8")
print(f"Corpus generated successfully at {CORPUS_ROOT}")
