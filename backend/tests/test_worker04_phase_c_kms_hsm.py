"""ASTRA - Worker 04 Phase C Cloud KMS & PKCS#11 HSM Discovery Tests.

Verifies:
  1. CloudKmsDetector extracts AWS KMS key specs (SYMMETRIC_DEFAULT, RSA_2048, ECC_NIST_P384).
  2. CloudKmsDetector extracts Azure Key Vault (RSA-4096, EC P-256) and GCP KMS (GOOGLE_SYMMETRIC_ENCRYPTION, RSA_SIGN_PSS_2048_SHA256).
  3. Pkcs11HsmDetector extracts PKCS#11 mechanisms (CKM_RSA_PKCS, CKM_ECDSA, CKM_AES_GCM, CKM_SHA256) and token security flags.
  4. Master scan pipeline aggregates Cloud KMS and PKCS#11 findings into canonical assets and CycloneDX 1.6 CBOM.
"""

import io
import shutil
import tempfile
import zipfile
from pathlib import Path

import pytest

from app.discovery.detectors.cloud_kms_detector import CloudKmsDetector
from app.discovery.detectors.pkcs11_detector import Pkcs11HsmDetector
from app.services.scan_service import GLOBAL_SCAN_SERVICE, GLOBAL_SCAN_STORE
from app.discovery.models import ClaimType, ConfidenceBand, SourceKind


def test_cloud_kms_detector_aws_kms(tmp_path):
    """Verify detection of AWS KMS customer managed keys and specifications."""
    detector = CloudKmsDetector()
    tf_content = """
resource "aws_kms_key" "app_encryption" {
  description             = "Master symmetric data encryption key"
  deletion_window_in_days = 30
  key_usage               = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
}

resource "aws_kms_key" "signing_key" {
  description             = "Asymmetric token signing key"
  key_usage               = "SIGN_VERIFY"
  customer_master_key_spec = "RSA_2048"
}

resource "aws_kms_key" "ecc_exchange" {
  description             = "Elliptic curve key"
  key_usage               = "SIGN_VERIFY"
  key_spec                = "ECC_NIST_P384"
}
"""
    tf_file = tmp_path / "kms_manifest.tf"
    tf_file.write_text(tf_content, encoding="utf-8")

    assert detector.can_analyze(tf_file) is True
    observations = detector.analyze_file(tf_file, "kms_manifest.tf", "test-scan-1")

    assert len(observations) >= 3

    # Check SYMMETRIC_DEFAULT
    symm = [o for o in observations if o.algorithm == "AES-256-GCM"]
    assert len(symm) >= 1
    assert symm[0].key_size_bits == 256
    assert symm[0].purpose == "SYMMETRIC_ENCRYPTION"
    assert symm[0].raw_parameters["cloud_provider"] == "AWS"

    # Check RSA_2048
    rsa_obs = [o for o in observations if o.algorithm == "RSA"]
    assert len(rsa_obs) >= 1
    assert rsa_obs[0].key_size_bits == 2048
    assert rsa_obs[0].purpose == "ASYMMETRIC"

    # Check ECC_NIST_P384
    ecc_obs = [o for o in observations if o.algorithm == "ECDSA"]
    assert len(ecc_obs) >= 1
    assert ecc_obs[0].curve_name == "P-384"
    assert ecc_obs[0].key_size_bits == 384


def test_cloud_kms_detector_azure_and_gcp(tmp_path):
    """Verify detection of Azure Key Vault and GCP Cloud KMS configurations."""
    detector = CloudKmsDetector()

    # Azure template
    azure_content = """
resource "azurerm_key_vault_key" "vault_rsa" {
  name         = "corp-vault-key"
  key_vault_id = azurerm_key_vault.main.id
  key_type     = "RSA"
  key_size     = 4096
}

resource "azurerm_key_vault_key" "vault_ec" {
  name         = "corp-ec-key"
  key_vault_id = azurerm_key_vault.main.id
  key_type     = "EC"
  curve        = "P-256"
}
"""
    azure_file = tmp_path / "azure_keyvault.tf"
    azure_file.write_text(azure_content, encoding="utf-8")

    obs_azure = detector.analyze_file(azure_file, "azure_keyvault.tf", "test-scan-2")
    assert any(o.algorithm == "RSA" and o.key_size_bits == 4096 for o in obs_azure)
    assert any(o.algorithm == "ECDSA" and o.curve_name == "P-256" for o in obs_azure)

    # GCP template
    gcp_content = """
resource "google_kms_crypto_key" "storage_key" {
  name     = "storage-crypto-key"
  key_ring = google_kms_key_ring.keyring.id
  purpose  = "ENCRYPT_DECRYPT"
  version_template {
    algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
  }
}

resource "google_kms_crypto_key" "pss_key" {
  name     = "pss-signing-key"
  key_ring = google_kms_key_ring.keyring.id
  purpose  = "ASYMMETRIC_SIGN"
  version_template {
    algorithm = "RSA_SIGN_PSS_2048_SHA256"
  }
}
"""
    gcp_file = tmp_path / "gcp_kms.tf"
    gcp_file.write_text(gcp_content, encoding="utf-8")

    obs_gcp = detector.analyze_file(gcp_file, "gcp_kms.tf", "test-scan-3")
    assert any(o.algorithm == "AES-256-GCM" and o.raw_parameters.get("cloud_provider") == "GCP" for o in obs_gcp)
    assert any(o.algorithm == "RSA" and o.purpose == "SIGNATURE" for o in obs_gcp)


def test_pkcs11_hsm_detector(tmp_path):
    """Verify detection of PKCS#11 hardware security module mechanisms and token profiles."""
    detector = Pkcs11HsmDetector()
    pkcs11_content = """
# SoftHSM v2 configuration file
directories.tokendir = /var/lib/softhsm/tokens/
objectstore.backend = file
log.level = INFO

slot.0.token_label = "Production-Master-HSM"
slot.0.module = /usr/lib/softhsm/libsofthsm2.so
slot.0.flags = CKF_LOGIN_REQUIRED, CKF_USER_PIN_INITIALIZED, CKF_PROTECTED_AUTHENTICATION_PATH

# Enforced hardware mechanisms
mechanisms.allowed = [
    CKM_RSA_PKCS,
    CKM_RSA_PKCS_KEY_PAIR_GEN,
    CKM_ECDSA,
    CKM_AES_GCM,
    CKM_SHA256
]
"""
    hsm_file = tmp_path / "softhsm2.conf"
    hsm_file.write_text(pkcs11_content, encoding="utf-8")

    assert detector.can_analyze(hsm_file) is True
    observations = detector.analyze_file(hsm_file, "softhsm2.conf", "test-scan-4")

    assert len(observations) >= 4

    # Check RSA mechanism
    rsa_obs = [o for o in observations if o.algorithm == "RSA"]
    assert len(rsa_obs) >= 1
    assert rsa_obs[0].raw_parameters["hardware_standard"] == "PKCS#11"
    assert "CKF_LOGIN_REQUIRED" in rsa_obs[0].raw_parameters["security_flags"]

    # Check ECDSA mechanism
    ecdsa_obs = [o for o in observations if o.algorithm == "ECDSA"]
    assert len(ecdsa_obs) >= 1
    assert ecdsa_obs[0].purpose in ["SIGNATURE", "KEY_GENERATION"]

    # Check AES-GCM mechanism
    aes_obs = [o for o in observations if o.algorithm == "AES-GCM"]
    assert len(aes_obs) >= 1
    assert aes_obs[0].key_size_bits == 256

    # Check SHA-256 mechanism
    sha_obs = [o for o in observations if o.algorithm == "SHA-256"]
    assert len(sha_obs) >= 1
    assert sha_obs[0].purpose == "HASH"


def test_full_pipeline_with_kms_and_hsm():
    """Verify that full scan pipeline aggregates Cloud KMS and PKCS#11 into CBOM."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "infra/kms.tf",
            'resource "aws_kms_key" "data" {\n'
            '  customer_master_key_spec = "RSA_2048"\n'
            '}\n'
        )
        zf.writestr(
            "config/pkcs11.conf",
            'slot.0.token_label = "HSM-Token"\n'
            'mechanisms = CKM_AES_GCM\n'
        )
    buf.seek(0)

    # Save to temp zip file
    temp_dir = tempfile.mkdtemp(prefix="astra_test_kms_pipeline_")
    archive_path = Path(temp_dir) / "enterprise_infra.zip"
    with open(archive_path, "wb") as f:
        f.write(buf.getvalue())

    try:
        record = GLOBAL_SCAN_SERVICE.run_scan_on_archive(
            archive_path=str(archive_path),
            target_name="enterprise_infra.zip",
        )

        assert record.scan_id is not None
        assert len(record.observations) >= 2

        # Verify findings include both RSA and AES-GCM
        algos = {obs.algorithm for obs in record.observations}
        assert "RSA" in algos
        assert "AES-GCM" in algos

        # Verify CBOM component generation
        cbom = record.cbom_data
        assert cbom["bomFormat"] == "CycloneDX"
        components = cbom.get("components", [])
        assert len(components) >= 2

        comp_algos = {
            c.get("cryptoProperties", {}).get("algorithmProperties", {}).get("name")
            for c in components
        }
        assert "RSA" in comp_algos or any("RSA" in str(c) for c in components)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
