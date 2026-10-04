"""ASTRA — Worker 04 Phase E Automated Test Suite.

Validates:
1. Dynamic, evidence-derived judging rehearsal runner execution (100/100 points, exit code 0).
2. Elimination of all stale test counters (no 88, 119, 141, 311, 333) in active documentation and UI.
3. Absolute byte-for-byte identity between frontend/index.html and backend/app/static/index.html.
4. Scope matrix alignment (Cloud KMS and PKCS#11 HSM as verified local prototype adapters) and NIST FIPS 203 errata notice.
"""

import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from scripts.run_judging_rehearsal import run_rehearsal


class TestWorker04PhaseERehearsalCloseout:
    """Automated verification suite for Worker 04 Phase E Closeout."""

    def test_dynamic_rehearsal_scorecard_100_points(self):
        """Test E.1: Assert python scripts/run_judging_rehearsal.py executes dynamically and returns exit code 0."""
        exit_code = run_rehearsal()
        assert exit_code == 0, f"Expected return code 0 (100/100 score), got {exit_code}"

    def test_readme_and_ui_no_stale_test_counters(self):
        """Test E.2 & E.3: Assert zero stale test counts (88, 119, 141, 311, 333) in README.md and UI."""
        readme_path = REPO_ROOT / "README.md"
        assert readme_path.exists(), "README.md missing"
        readme_text = readme_path.read_text(encoding="utf-8")

        # Stale test counts that must not appear in test counter badges or headings
        stale_phrases = [
            "141 passing",
            "141 Tests",
            "141 tests",
            "311 Passing Tests",
            "311 passing",
            "333 Passing Tests",
            "333 tests",
            "333 passing",
            "88 passing",
            "119 passing",
        ]
        for phrase in stale_phrases:
            assert phrase not in readme_text, f"Stale test phrase '{phrase}' found in README.md"

        # Check frontend/index.html and backend static index.html
        frontend_html = (REPO_ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
        for phrase in ["311+", "333+", "141 passing", "88 passing", "119 passing"]:
            assert phrase not in frontend_html, f"Stale phrase '{phrase}' found in frontend/index.html"

    def test_frontend_and_backend_static_byte_identical(self):
        """Test: frontend/index.html and backend/app/static/index.html are 100% byte-for-byte identical."""
        frontend_file = REPO_ROOT / "frontend" / "index.html"
        backend_file = REPO_ROOT / "backend" / "app" / "static" / "index.html"

        assert frontend_file.exists(), "frontend/index.html missing"
        assert backend_file.exists(), "backend/app/static/index.html missing"

        f_bytes = frontend_file.read_bytes()
        b_bytes = backend_file.read_bytes()

        assert len(f_bytes) == len(b_bytes), f"File size mismatch: frontend={len(f_bytes)} vs backend={len(b_bytes)}"
        assert f_bytes == b_bytes, "frontend/index.html and backend/app/static/index.html byte mismatch"

    def test_scope_matrix_and_errata_coverage(self):
        """Test: Scope matrix lists Cloud KMS and PKCS#11 HSM as verified local adapters and contains FIPS 203 errata."""
        readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        # Must document Cloud KMS and PKCS#11 HSM as verified local adapters
        assert "Cloud KMS" in readme_text, "Cloud KMS missing from README.md"
        assert "PKCS#11" in readme_text, "PKCS#11 missing from README.md"
        assert "Verified" in readme_text, "Verified status missing from README.md"

        # Must contextualize NIST FIPS 203 errata notice (17 November 2025)
        assert "17 November 2025" in readme_text, "NIST FIPS 203 errata date missing in README.md"
        assert "FIPS 203 errata" in readme_text or "FIPS 203 (ML-KEM)" in readme_text
