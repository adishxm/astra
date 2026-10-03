"""ASTRA - Core Security Primitives.

Path sanitization, traversal validation, streaming hashing, and isolation checks.
"""

import hashlib
import os
from pathlib import Path
from typing import Tuple


class SecurityException(Exception):
    """Base exception for security boundary violations."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class PathTraversalError(SecurityException):
    """Raised when an archive member attempts directory traversal."""


class SymlinkEscapeError(SecurityException):
    """Raised when a symlink points outside the extraction sandbox."""


class DecompressionBombError(SecurityException):
    """Raised when an archive exceeds compression ratio or size thresholds."""


class MalformedArchiveError(SecurityException):
    """Raised when an archive format is corrupted or invalid."""


def compute_file_sha256(file_path: Path, chunk_size: int = 65536) -> Tuple[str, int]:
    """Compute SHA-256 digest and total byte count in streaming chunks.

    Returns:
        Tuple of (sha256_hex, total_bytes)
    """
    hasher = hashlib.sha256()
    total_bytes = 0
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
            total_bytes += len(chunk)
    return hasher.hexdigest(), total_bytes


def sanitize_relative_path(member_path: str, max_length: int = 1024) -> Path:
    r"""Validate and sanitize an archive member path against path traversal.

    Rejects:
    - Null bytes
    - Leading slashes or drive letters (e.g. /etc/passwd or C:\Windows)
    - Parent directory backtracking ('..')
    - Paths exceeding max_length

    Returns:
        Sanitized, relative Path object.
    """
    if "\0" in member_path:
        raise PathTraversalError("REJECTION_NULL_BYTE", "Archive path contains null byte")

    # Replace backslashes with forward slashes for universal handling
    normalized = member_path.replace("\\", "/").strip()

    if len(normalized) > max_length:
        raise PathTraversalError(
            "REJECTION_PATH_TOO_LONG",
            f"Archive path exceeds maximum length of {max_length} characters",
        )

    # Check for drive letters (e.g. C:)
    if len(normalized) >= 2 and normalized[1] == ":" and normalized[0].isalpha():
        raise PathTraversalError(
            "REJECTION_PATH_TRAVERSAL",
            "Archive path contains absolute drive specification",
        )

    # Convert to pure path and inspect components
    pure_path = Path(normalized)
    if pure_path.is_absolute():
        raise PathTraversalError(
            "REJECTION_PATH_TRAVERSAL",
            "Archive path must not be absolute",
        )

    # Verify no '..' component exists
    for part in pure_path.parts:
        if part in ("..", ""):
            if part == "..":
                raise PathTraversalError(
                    "REJECTION_PATH_TRAVERSAL",
                    "Directory traversal ('..') detected in archive path",
                )

    return pure_path


def verify_sandbox_containment(target_dir: Path, destination_path: Path) -> None:
    """Verify that destination_path resolves strictly within target_dir."""
    resolved_target = target_dir.resolve()
    try:
        resolved_destination = destination_path.resolve()
    except Exception as e:
        raise PathTraversalError(
            "REJECTION_PATH_RESOLUTION_FAILED",
            f"Failed to resolve target path: {e}",
        )

    # Check if resolved_destination is relative to resolved_target
    try:
        resolved_destination.relative_to(resolved_target)
    except ValueError:
        raise PathTraversalError(
            "REJECTION_PATH_TRAVERSAL",
            "Resolved file path escapes the sandbox extraction directory",
        )


def make_tree_readonly(directory: Path) -> None:
    """Recursively set files in directory to read-only permissions."""
    for root, dirs, files in os.walk(directory):
        for f in files:
            p = Path(root) / f
            try:
                # Remove write permission
                p.chmod(0o444)
            except OSError:
                pass
