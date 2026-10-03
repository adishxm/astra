"""ASTRA - Safe Archive Extractor.

Performs adversarial-resistant archive intake with:
- Magic byte format verification (no blind trust of client extension)
- Zip-bomb and cumulative expansion defenses
- Directory traversal & path normalization defenses
- Symlink escape and hard link blocking
- Streaming byte-limited file writing
- Per-file SHA-256 evidence hashing
"""

import bz2
import gzip
import os
import shutil
import stat
import tarfile
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple

from app.core.config import (
    COLLECTOR_VERSION,
    INTAKE_ENGINE_VERSION,
    RULESET_VERSION,
    IntakeLimits,
)
from app.core.security import (
    DecompressionBombError,
    MalformedArchiveError,
    PathTraversalError,
    SecurityException,
    SymlinkEscapeError,
    compute_file_sha256,
    sanitize_relative_path,
    verify_sandbox_containment,
)
from app.intake.models import (
    ArchiveType,
    ExtractedFileEntry,
    ScanManifest,
    ScanStatus,
)


class SafeArchiveExtractor:
    """Safely extracts archives into a sandboxed directory with adversarial defenses."""

    def __init__(self, limits: Optional[IntakeLimits] = None):
        self.limits = limits or IntakeLimits()

    def identify_archive_type(self, archive_path: Path) -> ArchiveType:
        """Inspect file magic bytes to determine actual archive container type."""
        try:
            with open(archive_path, "rb") as f:
                header = f.read(512)
        except OSError as e:
            raise MalformedArchiveError(
                "REJECTION_FILE_UNREADABLE", f"Cannot read archive file: {e}"
            )

        if len(header) < 4:
            raise MalformedArchiveError(
                "REJECTION_FILE_EMPTY_OR_TRUNCATED", "Archive file is truncated or empty"
            )

        # ZIP magic: PK\x03\x04 or empty PK\x05\x06
        if header.startswith(b"PK\x03\x04") or header.startswith(b"PK\x05\x06"):
            return ArchiveType.ZIP

        # GZIP magic: \x1f\x8b
        if header.startswith(b"\x1f\x8b"):
            return ArchiveType.TAR_GZ

        # BZIP2 magic: BZh
        if header.startswith(b"BZh"):
            return ArchiveType.TAR_BZ2

        # TAR magic: ustar at offset 257
        if len(header) >= 265 and header[257:262] == b"ustar":
            return ArchiveType.TAR

        # Fallback check for uncompressed standard tar with zero-filled header blocks
        try:
            if tarfile.is_tarfile(archive_path):
                return ArchiveType.TAR
        except Exception:
            pass

        return ArchiveType.UNKNOWN

    def process_and_extract(
        self,
        archive_path: Path,
        sandbox_dir: Path,
        scan_id: str,
        declared_scope: str = "LOCAL_ARCHIVE",
        tenant_id: str = "default-tenant",
    ) -> ScanManifest:
        """Execute full safety validation and extraction into sandbox_dir.

        Returns a complete ScanManifest with state COMPLETE, or raises SecurityException.
        """
        # 1. Check raw file existence and size
        if not archive_path.is_file():
            raise MalformedArchiveError(
                "REJECTION_FILE_NOT_FOUND", f"Archive not found: {archive_path}"
            )

        raw_sha256, raw_size_bytes = compute_file_sha256(archive_path)

        if raw_size_bytes == 0:
            raise MalformedArchiveError(
                "REJECTION_ZERO_BYTE_FILE", "Uploaded archive is zero bytes"
            )

        if raw_size_bytes > self.limits.max_archive_size_bytes:
            raise DecompressionBombError(
                "REJECTION_ARCHIVE_SIZE_EXCEEDED",
                f"Archive size {raw_size_bytes} exceeds limit {self.limits.max_archive_size_bytes}",
            )

        archive_type = self.identify_archive_type(archive_path)
        if archive_type == ArchiveType.UNKNOWN:
            raise MalformedArchiveError(
                "REJECTION_UNSUPPORTED_ARCHIVE_TYPE",
                "Unrecognized archive signature; supported formats are ZIP, TAR, TAR.GZ, TAR.BZ2",
            )

        sandbox_dir.mkdir(parents=True, exist_ok=True)

        manifest = ScanManifest(
            scan_id=scan_id,
            archive_name=archive_path.name,
            archive_sha256=raw_sha256,
            archive_size_bytes=raw_size_bytes,
            archive_type=archive_type,
            declared_scope=declared_scope,
            tenant_id=tenant_id,
            status=ScanStatus.VALIDATING,
            intake_engine_version=INTAKE_ENGINE_VERSION,
            collector_version=COLLECTOR_VERSION,
            ruleset_version=RULESET_VERSION,
            sandbox_directory=str(sandbox_dir),
        )

        try:
            if archive_type == ArchiveType.ZIP:
                self._extract_zip(archive_path, sandbox_dir, manifest, raw_size_bytes)
            else:
                self._extract_tar(archive_path, sandbox_dir, manifest, raw_size_bytes)

            # Compute overall compression ratio
            if raw_size_bytes > 0:
                manifest.compression_ratio = round(
                    manifest.total_uncompressed_bytes / raw_size_bytes, 2
                )

            manifest.status = ScanStatus.COMPLETE
            manifest.completed_at = manifest.started_at

            return manifest

        except Exception as e:
            # Clean up sandbox directory on extraction failure
            if sandbox_dir.exists():
                shutil.rmtree(sandbox_dir, ignore_errors=True)

            code = getattr(e, "code", "REJECTION_EXTRACTION_FAILED")
            message = str(e)
            manifest.status = ScanStatus.REJECTED
            manifest.rejection_code = code
            manifest.rejection_reason = message
            raise

    def _extract_zip(
        self,
        archive_path: Path,
        sandbox_dir: Path,
        manifest: ScanManifest,
        raw_size_bytes: int,
    ) -> None:
        """Safely extract a ZIP archive with pre-validation and streaming byte limits."""
        try:
            zf = zipfile.ZipFile(archive_path, mode="r")
        except zipfile.BadZipFile as e:
            raise MalformedArchiveError(
                "REJECTION_MALFORMED_ZIP", f"Archive is corrupt or not a valid ZIP: {e}"
            )

        with zf:
            infolist = zf.infolist()
            manifest.total_files_in_archive = len(infolist)

            if len(infolist) > self.limits.max_file_count:
                raise DecompressionBombError(
                    "REJECTION_FILE_COUNT_EXCEEDED",
                    f"Archive member count ({len(infolist)}) exceeds maximum limit of {self.limits.max_file_count}",
                )

            # Pre-scan headers to detect compression bomb or obvious traversal before extracting
            declared_uncompressed_total = sum(item.file_size for item in infolist)
            if declared_uncompressed_total > self.limits.max_uncompressed_size_bytes:
                raise DecompressionBombError(
                    "REJECTION_UNCOMPRESSED_SIZE_EXCEEDED",
                    f"Declared uncompressed size {declared_uncompressed_total} exceeds limit {self.limits.max_uncompressed_size_bytes}",
                )

            ratio = declared_uncompressed_total / max(1, raw_size_bytes)
            if ratio > self.limits.max_compression_ratio:
                raise DecompressionBombError(
                    "REJECTION_ZIP_BOMB_DETECTED",
                    f"Compression ratio {ratio:.1f}:1 exceeds safety threshold of {self.limits.max_compression_ratio}:1",
                )

            cumulative_uncompressed = 0
            extracted_files: List[ExtractedFileEntry] = []

            for zip_info in infolist:
                # 1. Sanitize member path
                raw_filename = zip_info.filename
                # Skip directory entries
                if raw_filename.endswith("/"):
                    continue

                rel_path = sanitize_relative_path(
                    raw_filename, max_length=self.limits.max_path_length
                )
                dest_path = sandbox_dir / rel_path

                # Verify containment
                verify_sandbox_containment(sandbox_dir, dest_path)

                # 2. Check for symlinks in ZIP
                # In ZIP, unix attributes are stored in upper 16 bits of external_attr
                unix_mode = zip_info.external_attr >> 16
                if unix_mode and stat.S_ISLNK(unix_mode):
                    raise SymlinkEscapeError(
                        "REJECTION_UNSAFE_SYMLINK",
                        f"Symlinks are disallowed in archive intake: {raw_filename}",
                    )

                # 3. Check dangerous extension policy
                ext = rel_path.suffix.lower()
                if ext in self.limits.blocked_dangerous_extensions:
                    manifest.skipped_file_count += 1
                    extracted_files.append(
                        ExtractedFileEntry(
                            relative_path=str(rel_path).replace("\\", "/"),
                            size_bytes=zip_info.file_size,
                            sha256="skipped-dangerous-extension",
                            file_extension=ext,
                            is_supported=False,
                            skip_reason=f"BLOCKED_DANGEROUS_EXTENSION_{ext}",
                        )
                    )
                    continue

                # 4. Stream extraction with active byte counting
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                file_bytes_written = 0
                import hashlib

                file_hasher = hashlib.sha256()

                with zf.open(zip_info) as source, open(dest_path, "wb") as target:
                    while chunk := source.read(65536):
                        file_bytes_written += len(chunk)
                        cumulative_uncompressed += len(chunk)

                        if file_bytes_written > self.limits.max_single_file_size_bytes:
                            raise DecompressionBombError(
                                "REJECTION_SINGLE_FILE_SIZE_EXCEEDED",
                                f"File {raw_filename} exceeded single-file size limit of {self.limits.max_single_file_size_bytes}",
                            )

                        if cumulative_uncompressed > self.limits.max_uncompressed_size_bytes:
                            raise DecompressionBombError(
                                "REJECTION_UNCOMPRESSED_SIZE_EXCEEDED",
                                f"Cumulative extraction exceeded limit of {self.limits.max_uncompressed_size_bytes}",
                            )

                        file_hasher.update(chunk)
                        target.write(chunk)

                # Record successful file entry
                extracted_files.append(
                    ExtractedFileEntry(
                        relative_path=str(rel_path).replace("\\", "/"),
                        size_bytes=file_bytes_written,
                        sha256=file_hasher.hexdigest(),
                        file_extension=ext,
                        is_supported=self._is_supported_extension(ext),
                    )
                )

            manifest.extracted_file_count = len(
                [f for f in extracted_files if not f.skip_reason]
            )
            manifest.total_uncompressed_bytes = cumulative_uncompressed
            manifest.files = extracted_files

    def _extract_tar(
        self,
        archive_path: Path,
        sandbox_dir: Path,
        manifest: ScanManifest,
        raw_size_bytes: int,
    ) -> None:
        """Safely extract a TAR / TAR.GZ / TAR.BZ2 archive with traversal and symlink guards."""
        try:
            tf = tarfile.open(archive_path, mode="r:*")
        except (tarfile.TarError, OSError) as e:
            raise MalformedArchiveError(
                "REJECTION_MALFORMED_TAR", f"Archive is corrupt or not a valid TAR: {e}"
            )

        with tf:
            members = tf.getmembers()
            manifest.total_files_in_archive = len(members)

            if len(members) > self.limits.max_file_count:
                raise DecompressionBombError(
                    "REJECTION_FILE_COUNT_EXCEEDED",
                    f"Archive member count ({len(members)}) exceeds maximum limit of {self.limits.max_file_count}",
                )

            declared_uncompressed_total = sum(m.size for m in members if m.isfile())
            if declared_uncompressed_total > self.limits.max_uncompressed_size_bytes:
                raise DecompressionBombError(
                    "REJECTION_UNCOMPRESSED_SIZE_EXCEEDED",
                    f"Declared uncompressed size {declared_uncompressed_total} exceeds limit {self.limits.max_uncompressed_size_bytes}",
                )

            ratio = declared_uncompressed_total / max(1, raw_size_bytes)
            if ratio > self.limits.max_compression_ratio:
                raise DecompressionBombError(
                    "REJECTION_ZIP_BOMB_DETECTED",
                    f"Compression ratio {ratio:.1f}:1 exceeds safety threshold of {self.limits.max_compression_ratio}:1",
                )

            cumulative_uncompressed = 0
            extracted_files: List[ExtractedFileEntry] = []

            for member in members:
                # Reject symlinks and hardlinks pointing anywhere
                if member.issym() or member.islnk():
                    raise SymlinkEscapeError(
                        "REJECTION_UNSAFE_SYMLINK",
                        f"Symlinks and hardlinks are disallowed in archive intake: {member.name}",
                    )

                # Skip non-regular files (directories, fifos, devices)
                if not member.isfile():
                    continue

                rel_path = sanitize_relative_path(
                    member.name, max_length=self.limits.max_path_length
                )
                dest_path = sandbox_dir / rel_path

                # Verify containment
                verify_sandbox_containment(sandbox_dir, dest_path)

                ext = rel_path.suffix.lower()
                if ext in self.limits.blocked_dangerous_extensions:
                    manifest.skipped_file_count += 1
                    extracted_files.append(
                        ExtractedFileEntry(
                            relative_path=str(rel_path).replace("\\", "/"),
                            size_bytes=member.size,
                            sha256="skipped-dangerous-extension",
                            file_extension=ext,
                            is_supported=False,
                            skip_reason=f"BLOCKED_DANGEROUS_EXTENSION_{ext}",
                        )
                    )
                    continue

                dest_path.parent.mkdir(parents=True, exist_ok=True)
                file_bytes_written = 0
                import hashlib

                file_hasher = hashlib.sha256()

                f_in = tf.extractfile(member)
                if f_in is None:
                    continue

                with f_in as source, open(dest_path, "wb") as target:
                    while chunk := source.read(65536):
                        file_bytes_written += len(chunk)
                        cumulative_uncompressed += len(chunk)

                        if file_bytes_written > self.limits.max_single_file_size_bytes:
                            raise DecompressionBombError(
                                "REJECTION_SINGLE_FILE_SIZE_EXCEEDED",
                                f"File {member.name} exceeded single-file size limit of {self.limits.max_single_file_size_bytes}",
                            )

                        if cumulative_uncompressed > self.limits.max_uncompressed_size_bytes:
                            raise DecompressionBombError(
                                "REJECTION_UNCOMPRESSED_SIZE_EXCEEDED",
                                f"Cumulative extraction exceeded limit of {self.limits.max_uncompressed_size_bytes}",
                            )

                        file_hasher.update(chunk)
                        target.write(chunk)

                extracted_files.append(
                    ExtractedFileEntry(
                        relative_path=str(rel_path).replace("\\", "/"),
                        size_bytes=file_bytes_written,
                        sha256=file_hasher.hexdigest(),
                        file_extension=ext,
                        is_supported=self._is_supported_extension(ext),
                    )
                )

            manifest.extracted_file_count = len(
                [f for f in extracted_files if not f.skip_reason]
            )
            manifest.total_uncompressed_bytes = cumulative_uncompressed
            manifest.files = extracted_files

    def _is_supported_extension(self, ext: str) -> bool:
        """Check if file extension corresponds to a supported source, manifest, config, or cert format."""
        supported = {
            # Source files
            ".py",
            ".java",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".go",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".rs",
            # Package / Dependency manifests
            ".json",
            ".xml",
            ".toml",
            ".txt",
            ".mod",
            ".sum",
            # Configuration
            ".yaml",
            ".yml",
            ".conf",
            ".cnf",
            ".ini",
            ".properties",
            # Certificates & Public Keys
            ".pem",
            ".crt",
            ".cer",
            ".der",
            ".pub",
            ".key",  # May contain public keys or key configs (private keys will be redacted/flagged)
        }
        return ext in supported
