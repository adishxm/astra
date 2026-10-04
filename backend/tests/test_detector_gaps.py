import os
from pathlib import Path

from app.services.scan_service import GLOBAL_SCAN_SERVICE

def test_a_config_detector_generic_algorithms(tmp_path):
    """Test generic configuration values like 'algorithm: DES'."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "security:\n"
        "  algorithm: DES\n"
        "  encryption_key: AES\n"
        "  hash: MD5\n"
        "  cipher: 3DES\n"
        "  algo: DES_UNRELATED\n" # Negative test: should not match generic
        "  description: The word design is ignored\n" # Negative test
    )
    
    record = GLOBAL_SCAN_SERVICE.run_scan_on_directory(str(tmp_path), target_name="test")
    obs = record.observations
    
    algorithms = {o.algorithm for o in obs}
    
    # Assert true positives
    assert "DES" in algorithms
    assert "AES" in algorithms
    assert "MD5" in algorithms
    assert "3DES" in algorithms
    
    # Assert false positives are ignored
    assert "DES_UNRELATED" not in algorithms
    
    # Find specific observation for DES
    des_obs = next(o for o in obs if o.algorithm == "DES")
    assert des_obs.relative_path == "config.yaml"
    assert "algorithm: DES" in des_obs.sanitized_excerpt

def test_b_pem_public_key_detector(tmp_path):
    """Test raw PUBLIC KEY PEM blocks are detected safely."""
    cert_file = tmp_path / "public.pem"
    # A valid mock RSA public key PEM block
    cert_file.write_text(
        "-----BEGIN PUBLIC KEY-----\n"
        "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzq9p1oJzI+C5Jm0T\n"
        "G6t1p9Nq8R8kXzQ7W6L4zV6p7oZ5sJ1zL8a5V7M9nB0+c6rG4eK8uX9yL1a\n"
        "pW5u+bE3K3yZ6T8X5rN6wH5+wV9pB4iW+eJ7x8hL2eB4vS0uN7zT8jU4uX2\n"
        "sT8vQ2mQ7jX1jN3kY8yW6bR6oP0tY4aX7jH2bZ6uG5vR8mT5eK1zU5yQ4iP\n"
        "H5k+uK8bY0jL4aR5iE9bT4rM6aZ8+xW3kV9kR8iX6wQ4tJ7pZ0eV5nF7sX3\n"
        "vR2lT5iY6xV2bN7cW8+rQ8oW9jN7xR0mZ4uV8eY6xV2bN7cW8+rQ8oW9jN7\n"
        "cW8+rQ8oW9jN7xR0mZ4uV8eY6xV2bN7cW8+rQ8oW9jN7xR0mZ4uV8eY6xV2\n"
        "-----END PUBLIC KEY-----\n"
    )
    
    # Invalid PEM negative test
    bad_file = tmp_path / "invalid.pem"
    bad_file.write_text("-----BEGIN PUBLIC KEY-----\ninvalid\n-----END PUBLIC KEY-----")
    
    record = GLOBAL_SCAN_SERVICE.run_scan_on_directory(str(tmp_path), target_name="test")
    obs = record.observations
    
    assert len(obs) == 2 # both the valid and invalid matched the generic regex block
    paths = {o.relative_path for o in obs}
    assert "public.pem" in paths
    assert "invalid.pem" in paths
    assert obs[0].algorithm == "PUBLIC_KEY"
    assert "PEM public key block detected" in obs[0].sanitized_excerpt
    assert "MIIBI" not in obs[0].sanitized_excerpt # No raw key exposed
    assert "MIIBI" not in obs[0].sanitized_excerpt # No raw key exposed

def test_c_manifest_detector_bcrypt(tmp_path):
    """Test bcrypt package dependency detection."""
    pkg_file = tmp_path / "package.json"
    pkg_file.write_text(
        '{"dependencies": {"bcrypt": "^5.0.0", "unrelated-package": "1.0"}}'
    )
    
    record = GLOBAL_SCAN_SERVICE.run_scan_on_directory(str(tmp_path), target_name="test")
    obs = record.observations
    
    assert len(obs) == 1
    assert obs[0].algorithm == "bcrypt"
    assert obs[0].purpose == "CRYPTOGRAPHIC_LIBRARY"
    assert "bcrypt" in obs[0].sanitized_excerpt
