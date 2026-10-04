"""ASTRA - Durable File-Backed Cryptographic Audit Chain Store (Worker 04 - Phase B).

Provides:
- Persistent JSON-backed storage for SHA-256 Merkle-style chained audit blocks.
- On-load and runtime tamper-evidence verification.
- Tenant and scan-level isolation and query scoping.
- Automatic creation of data directories.
"""

import json
import os
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.web_workflow.hardening import ChainedAuditEvent, TamperEvidentAuditChainer


class AuditChainStore:
    """Thread-safe, file-persisted store for cryptographic audit hash chains."""

    def __init__(self, storage_path: Optional[str] = None):
        default_path = os.getenv("ASTRA_AUDIT_STORE_PATH")
        if not default_path:
            # Anchor relative to project root or workspace
            repo_root = Path(__file__).resolve().parent.parent.parent.parent
            default_path = str(repo_root / "data" / "audit" / "audit_chain.json")

        self.file_path = Path(storage_path or default_path).resolve()
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._chain: List[ChainedAuditEvent] = []
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Load and cryptographically verify existing audit chain from disk."""
        with self._lock:
            self._chain = []
            if not self.file_path.exists():
                return

            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        return
                    raw_list = json.loads(content)
                    
                if not isinstance(raw_list, list):
                    return

                for item in raw_list:
                    event = ChainedAuditEvent(**item)
                    self._chain.append(event)

                # Validate chain continuity upon load
                verification = TamperEvidentAuditChainer.verify_chain(self._chain)
                if not verification.get("valid"):
                    # Log integrity alert or raise error if corrupted
                    print(f"[AUDIT ALERT] Corrupted audit chain on disk: {verification.get('reason')}")
            except Exception as e:
                print(f"[AUDIT WARNING] Failed to load audit chain from {self.file_path}: {e}")

    def _save_to_disk(self) -> None:
        """Atomically persist current audit chain to disk as formatted JSON."""
        temp_path = self.file_path.with_suffix(".tmp")
        data = [event.model_dump() for event in self._chain]
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        temp_path.replace(self.file_path)

    def append_event(
        self,
        action: str,
        actor: str,
        asset_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> ChainedAuditEvent:
        """Append a new tamper-evident event, update hash chain, and persist to disk."""
        with self._lock:
            event_details = dict(details or {})
            if tenant_id:
                event_details["tenant_id"] = tenant_id
            if user_id:
                event_details["user_id"] = user_id

            event = TamperEvidentAuditChainer.append_event(
                chain=self._chain,
                action=action,
                actor=actor,
                asset_id=asset_id,
                details=event_details,
            )
            self._save_to_disk()
            return event

    def get_events(
        self,
        tenant_id: Optional[str] = None,
        scan_id: Optional[str] = None,
    ) -> List[ChainedAuditEvent]:
        """Query audit events with optional tenant and scan-level filtering."""
        with self._lock:
            events = list(self._chain)

        if tenant_id:
            events = [
                e for e in events
                if e.details.get("tenant_id") == tenant_id
            ]

        if scan_id:
            events = [
                e for e in events
                if e.asset_id == scan_id or e.details.get("scan_id") == scan_id
            ]

        return events

    def get_tip_hash(self) -> str:
        """Return the current head/tip SHA-256 digest of the chain."""
        with self._lock:
            if not self._chain:
                return TamperEvidentAuditChainer.GENESIS_HASH
            return self._chain[-1].event_hash

    def list_events(self) -> List[ChainedAuditEvent]:
        """Return a snapshot of all events in the chain."""
        with self._lock:
            return list(self._chain)

    def verify_chain(
        self,
        tenant_id: Optional[str] = None,
        scan_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Verify cryptographic chain continuity and return authoritative verification status."""
        with self._lock:
            chain_copy = list(self._chain)

        result = TamperEvidentAuditChainer.verify_chain(chain_copy)
        
        filtered_events = chain_copy
        if tenant_id:
            filtered_events = [
                e for e in filtered_events
                if e.details.get("tenant_id") == tenant_id
            ]

        if scan_id:
            filtered_events = [
                e for e in filtered_events
                if e.asset_id == scan_id or e.details.get("scan_id") == scan_id
            ]

        result["events"] = [e.model_dump() for e in filtered_events]
        result["events_count"] = len(filtered_events)
        result["stored_path"] = str(self.file_path)
        return result

    def clear(self) -> None:
        """Clear the store in-memory and on disk (used primarily for test isolation)."""
        with self._lock:
            self._chain = []
            if self.file_path.exists():
                try:
                    self.file_path.unlink()
                except OSError:
                    pass


# Singleton instance shared across the backend application
GLOBAL_AUDIT_STORE = AuditChainStore()
