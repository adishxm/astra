"""ASTRA - Centralized Authentication, Access Control & Rate Limiting.

Enforces:
  1. API Key verification (X-ASTRA-API-KEY and Bearer token).
  2. Hosted mode fail-closed security.
  3. Upload rate limiting per client IP.
  4. Operational environment configuration queries.
"""

import os
import time
from typing import Dict, List, Optional
from fastapi import HTTPException, Request


def is_hosted_mode() -> bool:
    """Check if ASTRA is running in hosted demo mode."""
    return os.getenv("ASTRA_HOSTED_MODE", "false").lower() in ("1", "true", "yes")


def is_directory_scan_allowed() -> bool:
    """Determine whether arbitrary filesystem directory scans are permitted."""
    if is_hosted_mode():
        return os.getenv("ASTRA_ALLOW_DIRECTORY_SCAN", "false").lower() in ("1", "true", "yes")
    return os.getenv("ASTRA_ALLOW_DIRECTORY_SCAN", "true").lower() in ("1", "true", "yes")


def get_max_upload_size() -> int:
    """Return maximum permitted upload archive size in bytes (default 50 MB)."""
    return int(os.getenv("ASTRA_MAX_UPLOAD_SIZE_BYTES", str(50 * 1024 * 1024)))


# In-memory sliding-window upload rate limiter per client IP
_UPLOAD_RATE_LIMIT_STORE: Dict[str, List[float]] = {}


def check_upload_rate_limit(request: Request):
    """Enforce per-IP upload rate limits (default 30 uploads / minute)."""
    max_uploads = int(os.getenv("ASTRA_RATE_LIMIT_UPLOADS_PER_MINUTE", "30"))
    now = time.time()
    client_ip = request.client.host if request.client else "unknown"
    timestamps = _UPLOAD_RATE_LIMIT_STORE.setdefault(client_ip, [])
    # Prune timestamps older than 60 seconds
    timestamps = [t for t in timestamps if now - t < 60.0]
    _UPLOAD_RATE_LIMIT_STORE[client_ip] = timestamps
    if len(timestamps) >= max_uploads:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: maximum {max_uploads} uploads per minute allowed. Please wait before retrying.",
        )
    timestamps.append(now)


def verify_api_key(request: Request):
    """Enforce API token authentication when ASTRA_API_KEY is configured or running in hosted mode."""
    expected_key = os.getenv("ASTRA_API_KEY")

    if is_hosted_mode() and not expected_key:
        if request.url.path == "/api/v1/scans/directory":
            # Let scan_directory enforce directory scan policy (403 or 404)
            return
        raise HTTPException(
            status_code=401,
            detail="Hosted mode access denied: ASTRA_API_KEY must be configured and supplied.",
        )

    if not expected_key:
        return

    # Check X-ASTRA-API-KEY header
    header_key = request.headers.get("X-ASTRA-API-KEY")
    if header_key and header_key == expected_key:
        return

    # Check Authorization: Bearer <token>
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        if token == expected_key:
            return

    raise HTTPException(
        status_code=401,
        detail="Unauthorized: Missing or invalid API key. Supply X-ASTRA-API-KEY header or Bearer token.",
    )


def get_tenant_id(request: Request) -> Optional[str]:
    """Extract tenant identifier from X-Tenant-ID header or environment."""
    return (
        request.headers.get("X-Tenant-ID")
        or request.headers.get("X-TENANT-ID")
        or os.getenv("ASTRA_DEFAULT_TENANT_ID")
    )


def get_user_id(request: Request) -> Optional[str]:
    """Extract user identifier from X-User-ID header or environment."""
    return (
        request.headers.get("X-User-ID")
        or request.headers.get("X-USER-ID")
        or os.getenv("ASTRA_DEFAULT_USER_ID")
    )
