"""
Worker 04 Phase A Automated Test Suite: Frontend Semantics & Demo Data Transparency

Validates:
1. Category resolver fix: ASYMMETRIC checked before SYMMETRIC substring checks.
2. Direct mapping of ASYMMETRIC, ASYMMETRIC_KEY_EXCHANGE, ASYMMETRIC_ENCRYPTION, RSA -> "Asymmetric".
3. Direct mapping of SYMMETRIC, SYMMETRIC_ENCRYPTION, AES -> "Symmetric".
4. Direct mapping of HASH, HASH_FUNCTION, MD5, SHA-256 -> "Hash".
5. Demo workspace badging and banner transparency.
6. Stale test count elimination (replacing "88 tests" with "334+ Passing Automated Tests").
7. Exact synchronization between frontend/index.html and backend/app/static/index.html.
"""

import json
import re
import subprocess
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_INDEX = REPO_ROOT / "frontend" / "index.html"
BACKEND_STATIC_INDEX = REPO_ROOT / "backend" / "app" / "static" / "index.html"


def _extract_js_function(html_content: str, fn_name: str) -> str:
    """Extract a JavaScript function from inline <script> tags."""
    pattern = rf"(function\s+{fn_name}\s*\([^)]*\)\s*\{{(?:[^{{}}]*|\{{[^{{}}]*\}})*\}})"
    match = re.search(pattern, html_content)
    if not match:
        idx = html_content.find(f"function {fn_name}")
        assert idx != -1, f"Function {fn_name} not found in HTML"
        brace_count = 0
        start = False
        end_pos = idx
        for i in range(idx, len(html_content)):
            if html_content[i] == '{':
                brace_count += 1
                start = True
            elif html_content[i] == '}':
                brace_count -= 1
                if start and brace_count == 0:
                    end_pos = i + 1
                    break
        return html_content[idx:end_pos]
    return match.group(1)


def _run_node_script(js_code: str) -> str:
    """Execute a Node.js snippet and return stdout."""
    res = subprocess.run(
        ["node", "-e", js_code],
        capture_output=True,
        text=True,
        check=True
    )
    return res.stdout.strip()


class TestWorker04PhaseAFrontendSemantics:
    """Test suite for Worker 04 Phase A frontend semantics and transparency."""

    def test_frontend_and_backend_static_synced(self):
        """Test A.5: Assert backend static index.html is byte-for-byte identical to frontend/index.html."""
        assert FRONTEND_INDEX.exists(), "frontend/index.html must exist"
        assert BACKEND_STATIC_INDEX.exists(), "backend/app/static/index.html must exist"
        f_content = FRONTEND_INDEX.read_text(encoding="utf-8")
        b_content = BACKEND_STATIC_INDEX.read_text(encoding="utf-8")
        assert f_content == b_content, "backend/app/static/index.html must be kept exactly synchronized with frontend/index.html"

    def test_asymmetric_substring_bug_fixed(self):
        """Test A.1: Assert resolveCategory maps ASYMMETRIC without erroneously falling into Symmetric."""
        content = FRONTEND_INDEX.read_text(encoding="utf-8")
        fn_code = _extract_js_function(content, "resolveCategory")

        test_js = f"""
        {fn_code}
        const testCases = [
            // Exact finding 1 cases from reassessment
            {{ obs: {{ algorithm: 'RSA-2048' }}, riskEval: {{ purpose: 'ASYMMETRIC' }} }},
            {{ obs: {{ algorithm: 'RSA-2048', purpose: 'ASYMMETRIC' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'RSA-2048', purpose: 'ASYMMETRIC_ENCRYPTION' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'ECDH P-256', purpose: 'ASYMMETRIC_KEY_EXCHANGE' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'RSA-2048', purpose: 'KEY_EXCHANGE' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'RSA-4096' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'ECDH P-384' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'X25519' }}, riskEval: null }}
        ];

        const results = testCases.map(tc => resolveCategory(tc.obs, tc.riskEval));
        console.log(JSON.stringify(results));
        """
        output = _run_node_script(test_js)
        categories = json.loads(output)
        for idx, cat in enumerate(categories):
            assert cat == "Asymmetric", f"Case {idx} expected 'Asymmetric', got '{cat}'"

    def test_signature_categories_correct(self):
        """Assert resolveCategory maps ECDSA and DSA signatures to 'Signature'."""
        content = FRONTEND_INDEX.read_text(encoding="utf-8")
        fn_code = _extract_js_function(content, "resolveCategory")

        test_js = f"""
        {fn_code}
        const testCases = [
            {{ obs: {{ algorithm: 'ECDSA P-384' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'DSA-2048' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'Ed25519', purpose: 'SIGNATURE' }}, riskEval: null }}
        ];

        const results = testCases.map(tc => resolveCategory(tc.obs, tc.riskEval));
        console.log(JSON.stringify(results));
        """
        output = _run_node_script(test_js)
        categories = json.loads(output)
        for idx, cat in enumerate(categories):
            assert cat == "Signature", f"Case {idx} expected 'Signature', got '{cat}'"

    def test_symmetric_categories_correct(self):
        """Test A.2: Assert resolveCategory maps SYMMETRIC, SYMMETRIC_ENCRYPTION, and AES to 'Symmetric'."""
        content = FRONTEND_INDEX.read_text(encoding="utf-8")
        fn_code = _extract_js_function(content, "resolveCategory")

        test_js = f"""
        {fn_code}
        const testCases = [
            {{ obs: {{ algorithm: 'AES-128', purpose: 'SYMMETRIC' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'AES-256', purpose: 'SYMMETRIC_ENCRYPTION' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'AES-GCM' }}, riskEval: {{ purpose: 'SYMMETRIC' }} }},
            {{ obs: {{ algorithm: '3DES' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'CHACHA20' }}, riskEval: null }}
        ];

        const results = testCases.map(tc => resolveCategory(tc.obs, tc.riskEval));
        console.log(JSON.stringify(results));
        """
        output = _run_node_script(test_js)
        categories = json.loads(output)
        for idx, cat in enumerate(categories):
            assert cat == "Symmetric", f"Case {idx} expected 'Symmetric', got '{cat}'"

    def test_hash_categories_correct(self):
        """Test A.3: Assert resolveCategory maps HASH, HASH_FUNCTION, and MD5/SHA to 'Hash'."""
        content = FRONTEND_INDEX.read_text(encoding="utf-8")
        fn_code = _extract_js_function(content, "resolveCategory")

        test_js = f"""
        {fn_code}
        const testCases = [
            {{ obs: {{ algorithm: 'MD5' }}, riskEval: {{ purpose: 'HASH' }} }},
            {{ obs: {{ algorithm: 'SHA-256' }}, riskEval: {{ purpose: 'HASH_FUNCTION' }} }},
            {{ obs: {{ algorithm: 'SHA-1' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'BLAKE2b' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'RIPEMD-160' }}, riskEval: null }}
        ];

        const results = testCases.map(tc => resolveCategory(tc.obs, tc.riskEval));
        console.log(JSON.stringify(results));
        """
        output = _run_node_script(test_js)
        categories = json.loads(output)
        for idx, cat in enumerate(categories):
            assert cat == "Hash", f"Case {idx} expected 'Hash', got '{cat}'"

    def test_post_quantum_categories_correct(self):
        """Assert resolveCategory maps post-quantum primitives to 'Post-Quantum'."""
        content = FRONTEND_INDEX.read_text(encoding="utf-8")
        fn_code = _extract_js_function(content, "resolveCategory")

        test_js = f"""
        {fn_code}
        const testCases = [
            {{ obs: {{ algorithm: 'ML-KEM-768' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'ML-DSA-65' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'SLH-DSA-128s' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'Falcon-512' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'SPHINCS+' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'Kyber512' }}, riskEval: null }}
        ];

        const results = testCases.map(tc => resolveCategory(tc.obs, tc.riskEval));
        console.log(JSON.stringify(results));
        """
        output = _run_node_script(test_js)
        categories = json.loads(output)
        for idx, cat in enumerate(categories):
            assert cat == "Post-Quantum", f"Case {idx} expected 'Post-Quantum', got '{cat}'"

    def test_demo_badging_and_stale_count_removal(self):
        """Test A.4: Assert initial UI displays Synthetic Demo badge and removes stale 88 tests counter."""
        content = FRONTEND_INDEX.read_text(encoding="utf-8")
        
        # 1. No stale 88 tests passing
        assert "88 tests passing" not in content, "Stale '88 tests passing' must be eliminated"
        assert "88</b> tests in CI" not in content, "Stale '88 tests in CI' must be eliminated"

        # 2. Modern 357+ tests metrics
        assert ("357+ Passing Automated Tests" in content or "334+ Passing Automated Tests" in content), "Must display current Passing Automated Tests"
        assert ("357+</b> automated tests" in content or "334+</b> automated tests" in content), "Must display automated tests in hero facts"

        # 3. Demo badge and banner present
        assert 'id="scan-mode-badge"' in content, "Header must contain scan-mode-badge"
        assert "Synthetic Demo Workspace" in content, "Initial view must identify Synthetic Demo Workspace"
        assert 'id="demo-banner"' in content, "Tab-overview must contain demo-banner"
        assert "Pre-loaded for interface demonstration" in content, "Must disclose that demo data is pre-loaded"
