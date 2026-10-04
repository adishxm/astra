"""ASTRA - Cloud Key Management Service (KMS) Cryptographic Detector (Worker 04 - Phase C).

Discovers cryptographic key specifications, algorithms, curves, and usage policies
in Cloud Infrastructure-as-Code (Terraform, CloudFormation, Bicep, ARM, and YAML/JSON manifests)
across AWS KMS, Azure Key Vault, and Google Cloud KMS.
"""

import hashlib
import json
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import RULESET_VERSION
from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    EvidenceState,
    Observation,
    SourceKind,
)


class CloudKmsDetector:
    """Discovers Cloud KMS managed keys and cryptographic specifications in IaC definitions."""

    DETECTOR_ID = "detector-cloud-kms-v1"

    SUPPORTED_EXTENSIONS = {
        ".tf", ".tfvars", ".json", ".yaml", ".yml", ".template", ".bicep", ".arm"
    }

    # AWS KMS Specifications
    AWS_KEY_SPECS = [
        (r"(?i)\bSYMMETRIC_DEFAULT\b", "AES-256-GCM", "SYMMETRIC_ENCRYPTION", 256, None, "AWS KMS default symmetric key (AES-256-GCM)"),
        (r"(?i)\bRSA_2048\b", "RSA", "ASYMMETRIC", 2048, None, "AWS KMS managed RSA-2048 asymmetric key"),
        (r"(?i)\bRSA_3072\b", "RSA", "ASYMMETRIC", 3072, None, "AWS KMS managed RSA-3072 asymmetric key"),
        (r"(?i)\bRSA_4096\b", "RSA", "ASYMMETRIC", 4096, None, "AWS KMS managed RSA-4096 asymmetric key"),
        (r"(?i)\bECC_NIST_P256\b", "ECDSA", "ASYMMETRIC", 256, "P-256", "AWS KMS managed ECC NIST P-256 key"),
        (r"(?i)\bECC_NIST_P384\b", "ECDSA", "ASYMMETRIC", 384, "P-384", "AWS KMS managed ECC NIST P-384 key"),
        (r"(?i)\bECC_NIST_P521\b", "ECDSA", "ASYMMETRIC", 521, "P-521", "AWS KMS managed ECC NIST P-521 key"),
        (r"(?i)\bECC_SECG_P256K1\b", "ECDSA", "ASYMMETRIC", 256, "secp256k1", "AWS KMS managed ECC SECG P-256k1 key"),
    ]

    # GCP Cloud KMS Algorithms
    GCP_CRYPTO_ALGORITHMS = [
        (r"(?i)\bGOOGLE_SYMMETRIC_ENCRYPTION\b", "AES-256-GCM", "SYMMETRIC_ENCRYPTION", 256, None, "GCP Cloud KMS default symmetric encryption key (AES-256-GCM)"),
        (r"(?i)\bAES_128_GCM\b", "AES-128-GCM", "SYMMETRIC_ENCRYPTION", 128, None, "GCP Cloud KMS AES-128 GCM key"),
        (r"(?i)\bAES_256_GCM\b", "AES-256-GCM", "SYMMETRIC_ENCRYPTION", 256, None, "GCP Cloud KMS AES-256 GCM key"),
        (r"(?i)\bRSA_SIGN_PSS_2048_SHA256\b", "RSA", "SIGNATURE", 2048, None, "GCP Cloud KMS RSA-PSS 2048-bit signing key"),
        (r"(?i)\bRSA_SIGN_PSS_3072_SHA256\b", "RSA", "SIGNATURE", 3072, None, "GCP Cloud KMS RSA-PSS 3072-bit signing key"),
        (r"(?i)\bRSA_SIGN_PSS_4096_SHA512\b", "RSA", "SIGNATURE", 4096, None, "GCP Cloud KMS RSA-PSS 4096-bit signing key"),
        (r"(?i)\bRSA_SIGN_PKCS1_2048_SHA256\b", "RSA", "SIGNATURE", 2048, None, "GCP Cloud KMS RSA-PKCS#1 v1.5 2048-bit signing key"),
        (r"(?i)\bRSA_SIGN_PKCS1_4096_SHA512\b", "RSA", "SIGNATURE", 4096, None, "GCP Cloud KMS RSA-PKCS#1 v1.5 4096-bit signing key"),
        (r"(?i)\bRSA_DECRYPT_OAEP_2048_SHA256\b", "RSA", "ASYMMETRIC", 2048, None, "GCP Cloud KMS RSA-OAEP 2048-bit decryption key"),
        (r"(?i)\bRSA_DECRYPT_OAEP_4096_SHA512\b", "RSA", "ASYMMETRIC", 4096, None, "GCP Cloud KMS RSA-OAEP 4096-bit decryption key"),
        (r"(?i)\bEC_SIGN_P256_SHA256\b", "ECDSA", "SIGNATURE", 256, "P-256", "GCP Cloud KMS ECDSA P-256 signing key"),
        (r"(?i)\bEC_SIGN_P384_SHA384\b", "ECDSA", "SIGNATURE", 384, "P-384", "GCP Cloud KMS ECDSA P-384 signing key"),
        (r"(?i)\bEC_SIGN_SECP256K1_SHA256\b", "ECDSA", "SIGNATURE", 256, "secp256k1", "GCP Cloud KMS ECDSA secp256k1 signing key"),
    ]

    # Azure Key Vault Key Types
    AZURE_KEY_SPECS = [
        (r"(?i)\b(RSA-HSM|RSA)\b", "RSA", "ASYMMETRIC", 2048, None, "Azure Key Vault managed RSA key"),
        (r"(?i)\b(EC-HSM|EC)\b", "ECDSA", "ASYMMETRIC", 256, "P-256", "Azure Key Vault managed EC key"),
        (r"(?i)\boct(-HSM)?\b", "AES-256-GCM", "SYMMETRIC_ENCRYPTION", 256, None, "Azure Key Vault managed symmetric key"),
    ]

    def can_analyze(self, file_path: Path) -> bool:
        """Evaluate if file is an IaC manifest or Cloud KMS configuration."""
        name_lower = file_path.name.lower()
        if any(keyword in name_lower for keyword in ["kms", "keyvault", "cloudformation", "vault", "crypto_key"]):
            return True
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def analyze_file(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Scan file for Cloud KMS definitions across AWS, Azure, and GCP."""
        observations: List[Observation] = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError:
            return []

        # Analyze line-by-line with multi-line context inspection
        for idx, line in enumerate(lines, start=1):
            line_str = line.strip()
            if not line_str or line_str.startswith(("#", "//", "/*")):
                continue

            # 1. Inspect AWS KMS specifications
            for pattern, algo, purpose, ksize, curve, rationale in self.AWS_KEY_SPECS:
                if re.search(pattern, line_str):
                    excerpt = line_str[:200]
                    obs = self._create_observation(
                        scan_id=scan_id,
                        relative_path=relative_path,
                        line_num=idx,
                        algorithm=algo,
                        purpose=purpose,
                        key_size=ksize,
                        curve=curve,
                        excerpt=excerpt,
                        provider="AWS",
                        service="AWS KMS",
                        rationale=rationale,
                    )
                    observations.append(obs)

            # 2. Inspect GCP Cloud KMS specifications
            for pattern, algo, purpose, ksize, curve, rationale in self.GCP_CRYPTO_ALGORITHMS:
                if re.search(pattern, line_str):
                    excerpt = line_str[:200]
                    obs = self._create_observation(
                        scan_id=scan_id,
                        relative_path=relative_path,
                        line_num=idx,
                        algorithm=algo,
                        purpose=purpose,
                        key_size=ksize,
                        curve=curve,
                        excerpt=excerpt,
                        provider="GCP",
                        service="Google Cloud KMS",
                        rationale=rationale,
                    )
                    observations.append(obs)

            # 3. Inspect Azure Key Vault specifications
            window_lines = lines[max(0, idx - 8):min(len(lines), idx + 8)]
            window_text = " ".join(window_lines)
            is_azure_context = any(
                term in relative_path.lower() for term in ["keyvault", "key_vault", "azure"]
            ) or bool(re.search(r"(?i)\b(azurerm_key_vault_key|key_vault_key|Microsoft\.KeyVault)\b", window_text))

            if is_azure_context and re.search(r"(?i)\b(key_type|kty)\b", line_str):
                for pattern, algo, purpose, ksize, curve, rationale in self.AZURE_KEY_SPECS:
                    if re.search(pattern, line_str):
                        key_size = ksize
                        if algo == "RSA":
                            size_match = re.search(r"(?i)key_size[\s:=]+['\"]?(\d+)['\"]?", window_text)
                            if size_match:
                                key_size = int(size_match.group(1))

                        excerpt = line_str[:200]
                        obs = self._create_observation(
                            scan_id=scan_id,
                            relative_path=relative_path,
                            line_num=idx,
                            algorithm=algo,
                            purpose=purpose,
                            key_size=key_size,
                            curve=curve,
                            excerpt=excerpt,
                            provider="Azure",
                            service="Azure Key Vault",
                            rationale=rationale,
                        )
                        observations.append(obs)

        return observations

    def _create_observation(
        self,
        scan_id: str,
        relative_path: str,
        line_num: int,
        algorithm: str,
        purpose: str,
        key_size: Optional[int],
        curve: Optional[str],
        excerpt: str,
        provider: str,
        service: str,
        rationale: str,
    ) -> Observation:
        """Helper to create standardized KMS Observation."""
        digest = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
        asset_id = f"cloud-kms-{provider.lower()}-{algorithm.lower()}-{relative_path}-{line_num}"

        return Observation(
            observation_id=str(uuid.uuid4()),
            scan_id=scan_id,
            candidate_asset_id=asset_id,
            claim_type=ClaimType.KEY_SPECIFICATION,
            source_kind=SourceKind.CONFIG,
            algorithm=algorithm,
            purpose=purpose,
            key_size_bits=key_size,
            curve_name=curve,
            relative_path=relative_path,
            start_line=line_num,
            end_line=line_num,
            evidence_digest=digest,
            sanitized_excerpt=excerpt,
            detector_id=self.DETECTOR_ID,
            ruleset_version=RULESET_VERSION,
            confidence=ConfidenceBand.CONFIRMED,
            confidence_rationale=rationale,
            state=EvidenceState.DECLARED,
            raw_parameters={
                "cloud_provider": provider,
                "service": service,
                "infrastructure_type": "CLOUD_KMS",
            },
        )
