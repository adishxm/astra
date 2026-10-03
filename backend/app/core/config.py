"""ASTRA - Core Configuration & Security Limits.

Provides versioned limits and policies for safe intake, deterministic
discovery, and boundary enforcement.
"""

from dataclasses import dataclass
from typing import Set


@dataclass(frozen=True)
class IntakeLimits:
    """Security limits for archive intake and sandboxed extraction."""

    # Maximum raw upload archive size (100 MB)
    max_archive_size_bytes: int = 100 * 1024 * 1024

    # Maximum total uncompressed extraction size (500 MB)
    max_uncompressed_size_bytes: int = 500 * 1024 * 1024

    # Maximum number of files in an archive (10,000 files)
    max_file_count: int = 10_000

    # Maximum compression ratio (uncompressed / compressed) to block zip bombs (100:1)
    max_compression_ratio: float = 100.0

    # Maximum size of any single uncompressed file (50 MB)
    max_single_file_size_bytes: int = 50 * 1024 * 1024

    # Maximum path length inside archive (1024 characters)
    max_path_length: int = 1024

    # Supported archive extensions
    allowed_archive_extensions: Set[str] = frozenset(
        {".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2"}
    )

    # Disallowed executable / dangerous file extensions inside archive by policy
    blocked_dangerous_extensions: Set[str] = frozenset(
        {".exe", ".dll", ".so", ".dylib", ".bin", ".elf", ".bat", ".cmd", ".vbs", ".ps1"}
    )


# System-wide collector and rule versions
COLLECTOR_VERSION = "0.1.0"
RULESET_VERSION = "2026.10-nist-pqc"
INTAKE_ENGINE_VERSION = "1.0.0"
