"""ASTRA - Worker 01 MVP-01 Comprehensive Test Suite.

Validates safe intake, zip bomb defenses, directory traversal prevention,
symlink escape blocking, dangerous file skipping, and sandbox isolation.
Satisfies Acceptance Criteria: AC-01, AC-02, AC-11, AC-13.
"""

import io
import os
import stat
import tarfile
import tempfile
import zipfile
from pathlib import Path
import pytest

from app.core.config import IntakeLimits
from app.core.security import (
    DecompressionBombError,
    MalformedArchiveError,
    PathTraversalError,
    SymlinkEscapeError,
)
from app.intake.extractor import SafeArchiveExtractor
from app.intake.models import ArchiveType, IntakeRequest, ScanStatus
from app.intake.sandbox import SandboxManager


@pytest.fixture
def temp_workspace():
    """Temporary workspace for test artifacts and sandboxes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_valid_zip_extraction(temp_workspace):
    """Test extracting a standard valid ZIP containing source, manifests, and certs."""
    archive_path = temp_workspace / "valid_repo.zip"
    sandbox_dir = temp_workspace / "sandbox_valid_zip"

    # Create test ZIP with multiple supported files
    with zipfile.ZipFile(archive_path, "w") as zf:
        zf.writestr("src/crypto_service.py", "import hashlib\ndef hash_pwd(p):\n    return hashlib.sha256(p).hexdigest()\n")
        zf.writestr("package.json", '{"name": "test-app", "dependencies": {"crypto-js": "^4.2.0"}}')
        zf.writestr("certs/server.crt", "-----BEGIN CERTIFICATE-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...\n-----END CERTIFICATE-----\n")
        zf.writestr("docs/README.md", "# Test Documentation\nNothing sensitive here.\n")

    extractor = SafeArchiveExtractor()
    manifest = extractor.process_and_extract(
        archive_path=archive_path,
        sandbox_dir=sandbox_dir,
        scan_id="test-scan-001",
        declared_scope="TEST_REPO",
        tenant_id="tenant-alpha",
    )

    assert manifest.status == ScanStatus.COMPLETE
    assert manifest.archive_type == ArchiveType.ZIP
    assert manifest.extracted_file_count == 4
    assert manifest.skipped_file_count == 0
    assert manifest.total_uncompressed_bytes > 0
    assert len(manifest.files) == 4

    # Verify extracted files exist on disk in sandbox
    assert (sandbox_dir / "src/crypto_service.py").exists()
    assert (sandbox_dir / "package.json").exists()
    assert (sandbox_dir / "certs/server.crt").exists()
    assert (sandbox_dir / "docs/README.md").exists()


def test_valid_tar_gz_extraction(temp_workspace):
    """Test extracting a standard valid TAR.GZ archive."""
    archive_path = temp_workspace / "valid_repo.tar.gz"
    sandbox_dir = temp_workspace / "sandbox_valid_tar"

    with tarfile.open(archive_path, "w:gz") as tf:
        data1 = b"package main\nimport \"crypto/aes\"\nfunc main() {}\n"
        ti1 = tarfile.TarInfo(name="main.go")
        ti1.size = len(data1)
        tf.addfile(ti1, io.BytesIO(data1))

        data2 = b"go 1.22\nmodule example.com/crypto\n"
        ti2 = tarfile.TarInfo(name="go.mod")
        ti2.size = len(data2)
        tf.addfile(ti2, io.BytesIO(data2))

    extractor = SafeArchiveExtractor()
    manifest = extractor.process_and_extract(
        archive_path=archive_path,
        sandbox_dir=sandbox_dir,
        scan_id="test-scan-002",
    )

    assert manifest.status == ScanStatus.COMPLETE
    assert manifest.archive_type == ArchiveType.TAR_GZ
    assert manifest.extracted_file_count == 2
    assert (sandbox_dir / "main.go").exists()
    assert (sandbox_dir / "go.mod").exists()


def test_path_traversal_zip_rejection(temp_workspace):
    """Test that a ZIP containing '../' directory traversal is blocked."""
    archive_path = temp_workspace / "traversal.zip"
    sandbox_dir = temp_workspace / "sandbox_traversal"

    with zipfile.ZipFile(archive_path, "w") as zf:
        zf.writestr("../../etc/passwd", "root:x:0:0:root:/root:/bin/bash\n")

    extractor = SafeArchiveExtractor()
    with pytest.raises(PathTraversalError) as exc_info:
        extractor.process_and_extract(archive_path, sandbox_dir, "test-scan-traversal")

    assert exc_info.value.code == "REJECTION_PATH_TRAVERSAL"
    # Ensure sandbox was cleaned up
    assert not sandbox_dir.exists()


def test_path_traversal_tar_rejection(temp_workspace):
    """Test that a TAR containing directory traversal is blocked."""
    archive_path = temp_workspace / "traversal.tar"
    sandbox_dir = temp_workspace / "sandbox_tar_traversal"

    with tarfile.open(archive_path, "w") as tf:
        data = b"malicious content"
        ti = tarfile.TarInfo(name="../../escaped.txt")
        ti.size = len(data)
        tf.addfile(ti, io.BytesIO(data))

    extractor = SafeArchiveExtractor()
    with pytest.raises(PathTraversalError) as exc_info:
        extractor.process_and_extract(archive_path, sandbox_dir, "test-scan-tar-traversal")

    assert exc_info.value.code == "REJECTION_PATH_TRAVERSAL"
    assert not sandbox_dir.exists()


def test_absolute_path_traversal_rejection(temp_workspace):
    """Test that absolute paths like /root/secret.key or C:/windows/win.ini are rejected."""
    archive_path = temp_workspace / "abs_path.zip"
    sandbox_dir = temp_workspace / "sandbox_abs"

    with zipfile.ZipFile(archive_path, "w") as zf:
        zf.writestr("/var/data/secret.key", "sensitive-key-data")

    extractor = SafeArchiveExtractor()
    with pytest.raises(PathTraversalError):
        extractor.process_and_extract(archive_path, sandbox_dir, "test-scan-abs")


def test_null_byte_path_rejection():
    """Test that member paths with null bytes are rejected."""
    from app.core.security import sanitize_relative_path

    with pytest.raises(PathTraversalError) as exc_info:
        sanitize_relative_path("harmless.txt\0.exe")

    assert exc_info.value.code == "REJECTION_NULL_BYTE"


def test_zip_bomb_compression_ratio_defense(temp_workspace):
    """Test that archives exceeding compression ratio threshold are rejected before extraction."""
    archive_path = temp_workspace / "bomb.zip"
    sandbox_dir = temp_workspace / "sandbox_bomb"

    # Create a zip containing highly compressible repeating data
    # 5MB of zeros compresses to a few hundred bytes in zip
    compressible_data = b"0" * (5 * 1024 * 1024)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("huge_zeroes.dat", compressible_data)

    # Set strict compression ratio limit of 20:1
    strict_limits = IntakeLimits(max_compression_ratio=20.0)
    extractor = SafeArchiveExtractor(limits=strict_limits)

    with pytest.raises(DecompressionBombError) as exc_info:
        extractor.process_and_extract(archive_path, sandbox_dir, "test-scan-bomb")

    assert exc_info.value.code == "REJECTION_ZIP_BOMB_DETECTED"
    assert not sandbox_dir.exists()


def test_archive_size_limit_exceeded(temp_workspace):
    """Test that archives exceeding raw byte limit are rejected immediately."""
    archive_path = temp_workspace / "oversized.zip"
    sandbox_dir = temp_workspace / "sandbox_oversized"

    with open(archive_path, "wb") as f:
        f.write(b"PK\x03\x04" + b"X" * 1000)

    # Set tiny limit of 500 bytes
    strict_limits = IntakeLimits(max_archive_size_bytes=500)
    extractor = SafeArchiveExtractor(limits=strict_limits)

    with pytest.raises(DecompressionBombError) as exc_info:
        extractor.process_and_extract(archive_path, sandbox_dir, "test-scan-oversized")

    assert exc_info.value.code == "REJECTION_ARCHIVE_SIZE_EXCEEDED"


def test_file_count_limit_exceeded(temp_workspace):
    """Test that archives with too many members are rejected."""
    archive_path = temp_workspace / "too_many_files.zip"
    sandbox_dir = temp_workspace / "sandbox_many"

    with zipfile.ZipFile(archive_path, "w") as zf:
        for i in range(15):
            zf.writestr(f"file_{i}.txt", f"content {i}")

    # Set file count limit to 10
    strict_limits = IntakeLimits(max_file_count=10)
    extractor = SafeArchiveExtractor(limits=strict_limits)

    with pytest.raises(DecompressionBombError) as exc_info:
        extractor.process_and_extract(archive_path, sandbox_dir, "test-scan-many")

    assert exc_info.value.code == "REJECTION_FILE_COUNT_EXCEEDED"


def test_dangerous_extension_policy(temp_workspace):
    """Test that dangerous binary/script files (.exe, .ps1) are safely skipped and flagged."""
    archive_path = temp_workspace / "mixed.zip"
    sandbox_dir = temp_workspace / "sandbox_mixed"

    with zipfile.ZipFile(archive_path, "w") as zf:
        zf.writestr("src/app.py", "print('hello')\n")
        zf.writestr("bin/trojan.exe", b"MZ\x90\x00malicious")
        zf.writestr("scripts/deploy.ps1", "Write-Output 'deploy'")

    extractor = SafeArchiveExtractor()
    manifest = extractor.process_and_extract(archive_path, sandbox_dir, "test-scan-mixed")

    assert manifest.status == ScanStatus.COMPLETE
    assert manifest.extracted_file_count == 1  # Only app.py extracted
    assert manifest.skipped_file_count == 2    # trojan.exe and deploy.ps1 skipped

    # Verify trojan.exe was NOT written to disk
    assert (sandbox_dir / "src/app.py").exists()
    assert not (sandbox_dir / "bin/trojan.exe").exists()
    assert not (sandbox_dir / "scripts/deploy.ps1").exists()


def test_symlink_rejection_in_tar(temp_workspace):
    """Test that symlinks in TAR archives are blocked to prevent symlink escape."""
    archive_path = temp_workspace / "symlink_test.tar"
    sandbox_dir = temp_workspace / "sandbox_symlink"

    with tarfile.open(archive_path, "w") as tf:
        ti = tarfile.TarInfo(name="link_to_passwd")
        ti.type = tarfile.SYMTYPE
        ti.linkname = "/etc/passwd"
        tf.addfile(ti)

    extractor = SafeArchiveExtractor()
    with pytest.raises(SymlinkEscapeError) as exc_info:
        extractor.process_and_extract(archive_path, sandbox_dir, "test-scan-symlink")

    assert exc_info.value.code == "REJECTION_UNSAFE_SYMLINK"
    assert not sandbox_dir.exists()


def test_malformed_archive_rejection(temp_workspace):
    """Test that corrupted non-archive data is rejected with MalformedArchiveError."""
    archive_path = temp_workspace / "corrupted.zip"
    sandbox_dir = temp_workspace / "sandbox_corrupt"

    with open(archive_path, "wb") as f:
        f.write(b"THIS IS NOT A VALID ARCHIVE HEADER AT ALL")

    extractor = SafeArchiveExtractor()
    with pytest.raises(MalformedArchiveError) as exc_info:
        extractor.process_and_extract(archive_path, sandbox_dir, "test-scan-corrupt")

    assert exc_info.value.code == "REJECTION_UNSUPPORTED_ARCHIVE_TYPE"


def test_sandbox_manager_lifecycle(temp_workspace):
    """Test the complete SandboxManager lifecycle including manifest JSON persistence."""
    archive_path = temp_workspace / "lifecycle_test.zip"
    with zipfile.ZipFile(archive_path, "w") as zf:
        zf.writestr("app.py", "import ssl\nctx = ssl.create_default_context()\n")
        zf.writestr("requirements.txt", "cryptography>=42.0.0\n")

    manager = SandboxManager(base_dir=temp_workspace / "sandboxes")
    request = IntakeRequest(
        archive_path=str(archive_path),
        declared_scope="LIFECYCLE_REPO",
        tenant_id="tenant-123",
    )

    manifest = manager.execute_intake(request)

    assert manifest.status == ScanStatus.COMPLETE
    sandbox_path = Path(manifest.sandbox_directory)
    assert sandbox_path.exists()
    assert (sandbox_path / "app.py").exists()
    assert (sandbox_path / "requirements.txt").exists()

    # Check that scan_manifest.json was written to the sandbox
    manifest_file = sandbox_path / "scan_manifest.json"
    assert manifest_file.exists()

    # Test sandbox cleanup
    cleaned = manager.cleanup_sandbox(manifest.scan_id)
    assert cleaned is True
    assert not sandbox_path.exists()
