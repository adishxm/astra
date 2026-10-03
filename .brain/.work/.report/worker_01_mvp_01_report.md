# Worker 01 MVP-01 Report: Safe Upload Intake and Scan Boundary

**Owner:** Discovery & Safe Intake (Worker 01)  
**Stage:** MVP  
**Phase:** MVP-01  
**Status:** IMPLEMENTED & VALIDATED  
**Traceability IDs:** R01, R02, R05, R10, R12  
**Acceptance Criteria:** AC-01, AC-02, AC-11, AC-13  
**Date:** 2026-10-03  

---

## 1. Objective & Scope
Implemented the authorized local archive intake, boundary security defenses, path normalization, decompression ratio limits, and sandboxed extraction lifecycle for ASTRA (SIH26164 ECDAT). The intake engine ensures that no uploaded content can execute, escape extraction boundaries, cause denial of service via decompression bombs, or access host files through symlinks.

---

## 2. Implemented Components
The following production-ready Python modules were implemented:

1. **`backend/app/core/config.py`**:
   - `IntakeLimits`: Configurable thresholds including:
     - `max_archive_size_bytes`: 100 MB
     - `max_uncompressed_size_bytes`: 500 MB
     - `max_file_count`: 10,000 files
     - `max_compression_ratio`: 100:1 (Zip bomb threshold)
     - `max_single_file_size_bytes`: 50 MB
     - `max_path_length`: 1024 characters
     - `allowed_archive_extensions`: `.zip`, `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2`, `.tbz2`
     - `blocked_dangerous_extensions`: `.exe`, `.dll`, `.so`, `.dylib`, `.bin`, `.elf`, `.bat`, `.cmd`, `.vbs`, `.ps1`
   - Active collector and rule versions: `COLLECTOR_VERSION = "0.1.0"`, `RULESET_VERSION = "2026.10-nist-pqc"`.

2. **`backend/app/core/security.py`**:
   - `compute_file_sha256`: Streaming chunk-based SHA-256 calculation for large archives.
   - `sanitize_relative_path`: Rejects null bytes, absolute paths, Windows drive specifiers, and parent backtracking (`..`).
   - `verify_sandbox_containment`: Canonical path resolution checking ensuring no path escapes sandbox root.
   - `make_tree_readonly`: Read-only permission application across the extracted sandbox directory.

3. **`backend/app/intake/models.py`**:
   - `ScanStatus`: Enum for `QUEUED`, `VALIDATING`, `RUNNING`, `COMPLETE`, `PARTIAL`, `FAILED`, `REJECTED`.
   - `ArchiveType`: Enum for `ZIP`, `TAR`, `TAR_GZ`, `TAR_BZ2`, `UNKNOWN`.
   - `ExtractedFileEntry`: Relative path, byte size, SHA-256 digest, extension, supported status, and skip reason.
   - `IntakeRequest`: Client ingestion parameters.
   - `ScanManifest`: Complete, reproducible manifest capturing scan ID (UUIDv4), archive SHA-256, byte sizes, file counts, compression ratio, engine/collector/ruleset versions, and extracted file records.

4. **`backend/app/intake/extractor.py`**:
   - `SafeArchiveExtractor`:
     - Magic byte format verification (no blind trust of user-supplied filename/MIME).
     - Streaming byte counters preventing single-file and cumulative expansion limit overruns.
     - Symlink and hard link blocking (`SymlinkEscapeError`).
     - Dangerous extension skipping with audit records.
     - Automatic cleanup on rejection.

5. **`backend/app/intake/sandbox.py`**:
   - `SandboxManager`: Ephemeral sandbox lifecycle, directory creation, read-only tree lockdown, `scan_manifest.json` generation, and cleanup handlers.

---

## 3. Phase Validation & Test Results
Executed 13 comprehensive unit tests via pytest covering all adversarial boundary scenarios:

| Test Case | Scenario Tested | Result |
|---|---|---|
| `test_valid_zip_extraction` | Valid ZIP extraction, SHA-256 hashes, manifest generation | **PASSED** |
| `test_valid_tar_gz_extraction` | Valid TAR.GZ extraction, containment, file accounting | **PASSED** |
| `test_path_traversal_zip_rejection` | Blocking `../../` traversal in ZIP | **PASSED** (`REJECTION_PATH_TRAVERSAL`) |
| `test_path_traversal_tar_rejection` | Blocking `../../` traversal in TAR | **PASSED** (`REJECTION_PATH_TRAVERSAL`) |
| `test_absolute_path_traversal_rejection` | Blocking `/var/data/...` absolute path escapes | **PASSED** (`REJECTION_PATH_TRAVERSAL`) |
| `test_null_byte_path_rejection` | Blocking null bytes (`\0`) in member paths | **PASSED** (`REJECTION_NULL_BYTE`) |
| `test_zip_bomb_compression_ratio_defense` | Blocking high-ratio decompression bombs | **PASSED** (`REJECTION_ZIP_BOMB_DETECTED`) |
| `test_archive_size_limit_exceeded` | Blocking raw upload exceeding byte size limit | **PASSED** (`REJECTION_ARCHIVE_SIZE_EXCEEDED`) |
| `test_file_count_limit_exceeded` | Blocking archive with excessive file counts | **PASSED** (`REJECTION_FILE_COUNT_EXCEEDED`) |
| `test_dangerous_extension_policy` | Safe skipping of `.exe` / `.ps1` without execution | **PASSED** |
| `test_symlink_rejection_in_tar` | Blocking symlinks pointing outside extraction sandbox | **PASSED** (`REJECTION_UNSAFE_SYMLINK`) |
| `test_malformed_archive_rejection` | Handling corrupted/truncated archive uploads | **PASSED** (`REJECTION_UNSUPPORTED_ARCHIVE_TYPE`) |
| `test_sandbox_manager_lifecycle` | End-to-end sandbox creation, read-only lock, manifest JSON, cleanup | **PASSED** |

**Summary**: 13/13 tests passed (100% pass rate).

---

## 4. Downstream Handoff
- **To Worker 02 (Evidence & Inventory)**: `ScanManifest` and isolated sandbox path containing immutable, sanitized extracted files. W02 can now consume `manifest.files` and parse cryptographic assets safely.
- **To Worker 04 (Workflow & UI)**: Clean status lifecycle (`QUEUED` $\to$ `VALIDATING` $\to$ `COMPLETE` / `REJECTED`) with structured rejection codes and denominator metrics.
