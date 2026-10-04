"""ASTRA - Source Code Cryptographic Detector (Worker 01 - MVP-02).

Performs deterministic discovery of cryptographic primitives across supported
programming languages (Python, Java, JS/TS, Go, C/C++, Rust).
Emits structured Observation objects conforming to W01 -> W02 contract.
"""

import ast
import hashlib
import re
import uuid
from pathlib import Path
from typing import List, Optional, Tuple

from app.core.config import RULESET_VERSION
from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    EvidenceState,
    Observation,
    SourceKind,
)

# Known cryptographic algorithms and their purposes
CRYPTO_SIGNATURES = [
    # Legacy / Deprecated / Vulnerable
    (r"\b(MD5|md5)\b", "MD5", "HASHING", "VULNERABLE", ConfidenceBand.HIGH),
    (r"\b(SHA-?1|sha1)\b", "SHA-1", "HASHING", "DEPRECATED", ConfidenceBand.HIGH),
    (r"\b(DES|des)\b", "DES", "ENCRYPTION", "VULNERABLE", ConfidenceBand.MEDIUM),
    (r"\b(3DES|TripleDES|DESede)\b", "3DES", "ENCRYPTION", "DEPRECATED", ConfidenceBand.HIGH),
    (r"\b(RC4|rc4|arcfour)\b", "RC4", "ENCRYPTION", "VULNERABLE", ConfidenceBand.HIGH),

    # Classical Symmetric (Standard)
    (r"\b(AES-?128|aes-?128|AES_128)\b", "AES-128", "ENCRYPTION", "CLASSICAL", ConfidenceBand.CONFIRMED),
    (r"\b(AES-?192|aes-?192|AES_192)\b", "AES-192", "ENCRYPTION", "CLASSICAL", ConfidenceBand.CONFIRMED),
    (r"\b(AES-?256|aes-?256|AES_256)\b", "AES-256", "ENCRYPTION", "CLASSICAL", ConfidenceBand.CONFIRMED),
    (r"\b(AES|aes)\b", "AES", "ENCRYPTION", "CLASSICAL", ConfidenceBand.HIGH),
    (r"\b(ChaCha20-Poly1305|chacha20-poly1305|ChaCha20)\b", "ChaCha20", "ENCRYPTION", "CLASSICAL", ConfidenceBand.CONFIRMED),

    # Classical Secure Hashing
    (r"\b(SHA-?256|sha-?256|sha256)\b", "SHA-256", "HASHING", "CLASSICAL", ConfidenceBand.CONFIRMED),
    (r"\b(SHA-?384|sha-?384|sha384)\b", "SHA-384", "HASHING", "CLASSICAL", ConfidenceBand.CONFIRMED),
    (r"\b(SHA-?512|sha-?512|sha512)\b", "SHA-512", "HASHING", "CLASSICAL", ConfidenceBand.CONFIRMED),
    (r"\b(SHA3-?256|sha3-?256)\b", "SHA3-256", "HASHING", "CLASSICAL", ConfidenceBand.CONFIRMED),
    (r"\b(SHA3-?512|sha3-?512)\b", "SHA3-512", "HASHING", "CLASSICAL", ConfidenceBand.CONFIRMED),
    (r"\b(BLAKE2b|blake2b|BLAKE2s|blake2s|BLAKE3|blake3)\b", "BLAKE2", "HASHING", "CLASSICAL", ConfidenceBand.CONFIRMED),

    # Classical Asymmetric (Quantum-Vulnerable)
    (r"\b(RSA-?1024|rsa1024)\b", "RSA-1024", "ASYMMETRIC", "VULNERABLE", ConfidenceBand.CONFIRMED),
    (r"\b(RSA-?2048|rsa2048)\b", "RSA-2048", "ASYMMETRIC", "QUANTUM_VULNERABLE", ConfidenceBand.CONFIRMED),
    (r"\b(RSA-?3072|rsa3072)\b", "RSA-3072", "ASYMMETRIC", "QUANTUM_VULNERABLE", ConfidenceBand.CONFIRMED),
    (r"\b(RSA-?4096|rsa4096)\b", "RSA-4096", "ASYMMETRIC", "QUANTUM_VULNERABLE", ConfidenceBand.CONFIRMED),
    (r"\b(RSA|rsa)\b", "RSA", "ASYMMETRIC", "QUANTUM_VULNERABLE", ConfidenceBand.HIGH),
    (r"\b(DSA|dsa)\b", "DSA", "SIGNATURE", "VULNERABLE", ConfidenceBand.HIGH),
    (r"\b(ECDSA|ecdsa)\b", "ECDSA", "SIGNATURE", "QUANTUM_VULNERABLE", ConfidenceBand.CONFIRMED),
    (r"\b(Ed25519|ed25519)\b", "Ed25519", "SIGNATURE", "QUANTUM_VULNERABLE", ConfidenceBand.CONFIRMED),
    (r"\b(X25519|x25519)\b", "X25519", "KEY_EXCHANGE", "QUANTUM_VULNERABLE", ConfidenceBand.CONFIRMED),
    (r"\b(ECDH|ecdh)\b", "ECDH", "KEY_EXCHANGE", "QUANTUM_VULNERABLE", ConfidenceBand.CONFIRMED),
    (r"\b(secp256k1|secp256r1|prime256v1|P-256|P-384|P-521)\b", "ECC-Curve", "ASYMMETRIC", "QUANTUM_VULNERABLE", ConfidenceBand.CONFIRMED),

    # Post-Quantum Cryptography (NIST Standardized & Candidates)
    (r"\b(ML-KEM-?512|ML-KEM-?768|ML-KEM-?1024|ml-kem)\b", "ML-KEM", "KEY_EXCHANGE", "POST_QUANTUM", ConfidenceBand.CONFIRMED),
    (r"\b(Kyber-?512|Kyber-?768|Kyber-?1024|CRYSTALS-Kyber)\b", "Kyber", "KEY_EXCHANGE", "POST_QUANTUM", ConfidenceBand.CONFIRMED),
    (r"\b(ML-DSA-?44|ML-DSA-?65|ML-DSA-?87|ml-dsa)\b", "ML-DSA", "SIGNATURE", "POST_QUANTUM", ConfidenceBand.CONFIRMED),
    (r"\b(Dilithium2|Dilithium3|Dilithium5|CRYSTALS-Dilithium)\b", "Dilithium", "SIGNATURE", "POST_QUANTUM", ConfidenceBand.CONFIRMED),
    (r"\b(SLH-DSA|slh-dsa|SPHINCS\+?|sphincs\+?)\b", "SLH-DSA", "SIGNATURE", "POST_QUANTUM", ConfidenceBand.CONFIRMED),
    (r"\b(Falcon-?512|Falcon-?1024|falcon)\b", "Falcon", "SIGNATURE", "POST_QUANTUM", ConfidenceBand.CONFIRMED),
    (r"\b(Classic-McEliece|ClassicMcEliece|mceliece)\b", "Classic-McEliece", "KEY_EXCHANGE", "POST_QUANTUM", ConfidenceBand.CONFIRMED),
]

# Sensitive patterns that must be sanitized / redacted
SECRET_REDACTION_PATTERN = re.compile(
    r'(?i)(?:key|secret|password|token|private|credential)\s*[:=]\s*["\']([^"\']{8,})["\']'
)


def sanitize_snippet(snippet: str) -> Tuple[str, bool]:
    """Sanitize snippet by masking apparent secrets or private tokens."""
    redacted = False
    def _repl(match):
        nonlocal redacted
        redacted = True
        return match.group(0).replace(match.group(1), "[REDACTED_SECRET]")

    sanitized = SECRET_REDACTION_PATTERN.sub(_repl, snippet)
    return sanitized, redacted


def strip_line_comments(line: str) -> str:
    """Filter out comments so comment-only mentions don't trigger false positives."""
    clean = line.strip()
    if not clean:
        return ""
    # Full-line comments across Python, JS, C, Java, Go, Rust, SQL, config
    if clean.startswith(("//", "#", "/*", "*", "*/", ";", "--", "rem ")):
        return ""

    # Strip trailing inline comments if not inside quotes
    in_single = False
    in_double = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif not in_single and not in_double:
            if ch == "#":
                return line[:i].strip()
            if ch == "/" and i + 1 < len(line) and line[i + 1] == "/":
                return line[:i].strip()
    return clean


class SourceCryptoDetector:
    """Discovers cryptographic usage in source code files."""

    DETECTOR_ID = "detector-source-code-v1"

    SUPPORTED_EXTENSIONS = {
        ".py", ".java", ".js", ".jsx", ".ts", ".tsx",
        ".go", ".c", ".cpp", ".h", ".hpp", ".rs"
    }

    def can_analyze(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def analyze_file(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Scan a source code file and produce observations."""
        observations: List[Observation] = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError as e:
            # Emit FAILED state observation
            return [
                Observation(
                    observation_id=str(uuid.uuid4()),
                    scan_id=scan_id,
                    candidate_asset_id=f"failed-{relative_path}",
                    claim_type=ClaimType.ALGORITHM_USE,
                    source_kind=SourceKind.SOURCE_CODE,
                    relative_path=relative_path,
                    evidence_digest=hashlib.sha256(str(e).encode()).hexdigest(),
                    sanitized_excerpt=f"File unreadable: {e}",
                    detector_id=self.DETECTOR_ID,
                    ruleset_version=RULESET_VERSION,
                    confidence=ConfidenceBand.LOW,
                    confidence_rationale="Read failure",
                    state=EvidenceState.FAILED,
                )
            ]

        # 1. Specialized Python AST Scanner if python file
        if file_path.suffix.lower() == ".py":
            py_obs = self._analyze_python_ast(lines, relative_path, scan_id)
            observations.extend(py_obs)

        # 2. Universal Pattern & Token Scanner across all lines
        seen_keys = set()
        in_block_comment = False
        in_triple_quote = None

        for idx, line in enumerate(lines, start=1):
            line_clean = line.strip()
            if not line_clean:
                continue

            # Skip block comments (/* ... */)
            if in_block_comment:
                if "*/" in line_clean:
                    in_block_comment = False
                    line = line[line.find("*/") + 2:]
                    line_clean = line.strip()
                    if not line_clean:
                        continue
                else:
                    continue

            # Skip Python / docstring blocks (""" or ''')
            if in_triple_quote:
                if in_triple_quote in line_clean:
                    quote_marker = in_triple_quote
                    in_triple_quote = None
                    line = line[line.find(quote_marker) + 3:]
                    line_clean = line.strip()
                    if not line_clean:
                        continue
                else:
                    continue
            else:
                # Check for single-line complete docstrings
                if (line_clean.startswith('"""') and line_clean.endswith('"""') and len(line_clean) >= 6) or \
                   (line_clean.startswith("'''") and line_clean.endswith("'''") and len(line_clean) >= 6):
                    continue
                # Check if multi-line docstring begins
                if line_clean.startswith('"""') and line_clean.count('"""') % 2 == 1:
                    in_triple_quote = '"""'
                    continue
                elif line_clean.startswith("'''") and line_clean.count("'''") % 2 == 1:
                    in_triple_quote = "'''"
                    continue
                elif line_clean.startswith("/*") and "*/" not in line_clean:
                    in_block_comment = True
                    continue

            code_only = strip_line_comments(line)
            if not code_only:
                # Skip pure comments and empty lines to prevent false positive findings
                continue

            for regex, algo_name, purpose, q_status, conf in CRYPTO_SIGNATURES:
                if re.search(regex, code_only, re.IGNORECASE):
                    dedup_key = (algo_name, idx)
                    if dedup_key in seen_keys:
                        continue
                    seen_keys.add(dedup_key)

                    excerpt = line_clean[:200]
                    sanitized_excerpt, redacted = sanitize_snippet(excerpt)
                    digest = hashlib.sha256(sanitized_excerpt.encode()).hexdigest()

                    # Infer key size if detectable in line
                    key_size = None
                    if "256" in algo_name:
                        key_size = 256
                    elif "512" in algo_name:
                        key_size = 512
                    elif "128" in algo_name:
                        key_size = 128
                    elif "2048" in algo_name:
                        key_size = 2048
                    elif "4096" in algo_name:
                        key_size = 4096

                    observations.append(
                        Observation(
                            observation_id=str(uuid.uuid4()),
                            scan_id=scan_id,
                            candidate_asset_id=f"{algo_name.lower()}-{relative_path}-{idx}",
                            claim_type=ClaimType.ALGORITHM_USE,
                            source_kind=SourceKind.SOURCE_CODE,
                            algorithm=algo_name,
                            purpose=purpose,
                            key_size_bits=key_size,
                            relative_path=relative_path,
                            start_line=idx,
                            end_line=idx,
                            evidence_digest=digest,
                            sanitized_excerpt=sanitized_excerpt,
                            redacted=redacted,
                            detector_id=self.DETECTOR_ID,
                            ruleset_version=RULESET_VERSION,
                            confidence=conf,
                            confidence_rationale=f"Pattern match for {algo_name} in {file_path.suffix} source code",
                            state=EvidenceState.OBSERVED,
                            raw_parameters={"quantum_status": q_status},
                        )
                    )

        return observations

    def _analyze_python_ast(
        self,
        lines: List[str],
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Use Python AST to extract confirmed imports and call sites."""
        content = "".join(lines)
        obs: List[Observation] = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return obs

        for node in ast.walk(tree):
            # Detect: from hashlib import sha256, md5 or from cryptography... import rsa
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if "hashlib" in module or "cryptography" in module or "Crypto" in module:
                    non_algo_helpers = {
                        "cipher", "ciphers", "algorithm", "algorithms", "mode", "modes",
                        "hazmat", "primitives", "asymmetric", "symmetric", "hashes",
                        "padding", "backends", "default_backend", "serialization", "x509",
                        "backend", "types", "utils"
                    }
                    for alias in node.names:
                        if alias.name.lower() in non_algo_helpers:
                            continue
                        algo = alias.name.upper()
                        sanitized, red = sanitize_snippet(lines[node.lineno - 1].strip() if node.lineno <= len(lines) else "")
                        obs.append(
                            Observation(
                                observation_id=str(uuid.uuid4()),
                                scan_id=scan_id,
                                candidate_asset_id=f"ast-import-{alias.name.lower()}-{relative_path}-{node.lineno}",
                                claim_type=ClaimType.ALGORITHM_USE,
                                source_kind=SourceKind.SOURCE_CODE,
                                algorithm=algo,
                                purpose="CRYPTOGRAPHIC_IMPORT",
                                relative_path=relative_path,
                                start_line=node.lineno,
                                end_line=node.lineno,
                                evidence_digest=hashlib.sha256(sanitized.encode()).hexdigest(),
                                sanitized_excerpt=sanitized,
                                redacted=red,
                                detector_id="detector-source-ast-py",
                                ruleset_version=RULESET_VERSION,
                                confidence=ConfidenceBand.CONFIRMED,
                                confidence_rationale=f"Verified Python AST Import of {alias.name} from {module}",
                                state=EvidenceState.OBSERVED,
                            )
                        )

        return obs
