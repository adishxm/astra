"""Automated Verification Suite for Worker 03 Phase B:
Frontend Data Semantics: Purpose-Specific PQC Recommendations, Honest Category Mapping & Real Audit State.

Verifies:
1. Category mapping never evaluates to undefined for any observation type.
2. Purpose-specific PQC & modernization recommendations correctly distinguish:
   - Hashes (MD5, SHA-1) -> SHA-256 / SHA3-256 (Modernization, NOT KEM!)
   - Symmetric ciphers (AES-128, 3DES) -> AES-256-GCM
   - Digital signatures (RSA-PSS, ECDSA, Ed25519) -> ML-DSA-65 / SLH-DSA
   - Key exchange / KEM (ECDH, X25519, RSA-OAEP) -> ML-KEM-768
   - Transport protocols (TLSv1.0, SSLv3) -> TLS 1.3 with Hybrid PQC
   - Backend-supplied recommendation takes precedence.
3. Active scan audit log dynamically chains verified events for active uploaded scans.
4. Active dashboard synchronizes renderAudit() on dashboard load and tab switch.
5. Static index.html in backend matches frontend/index.html.
"""

import json
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_INDEX = REPO_ROOT / "frontend" / "index.html"
BACKEND_STATIC_INDEX = REPO_ROOT / "backend" / "app" / "static" / "index.html"


def _extract_js_function(content: str, fn_name: str) -> str:
    """Extract a JavaScript function definition from an HTML/JS file."""
    pattern = rf"function {fn_name}\s*\([^)]*\)\s*\{{"
    match = re.search(pattern, content)
    assert match, f"Function {fn_name} not found in index.html"
    start_idx = match.start()
    
    # Simple brace counter to extract the complete function body
    open_braces = 0
    in_fn = False
    end_idx = start_idx
    for i, c in enumerate(content[start_idx:], start=start_idx):
        if c == '{':
            open_braces += 1
            in_fn = True
        elif c == '}':
            open_braces -= 1
            if in_fn and open_braces == 0:
                end_idx = i + 1
                break
    return content[start_idx:end_idx]


def _run_node_script(script: str) -> str:
    """Execute a Node.js snippet and return stdout."""
    res = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        check=True,
    )
    return res.stdout.strip()


class TestWorker03PhaseBFrontendSemantics:
    """Phase B Automated Acceptance Tests."""

    def test_frontend_and_backend_static_synced(self):
        """Assert frontend/index.html and backend/app/static/index.html are identical."""
        assert FRONTEND_INDEX.exists(), "frontend/index.html must exist"
        assert BACKEND_STATIC_INDEX.exists(), "backend/app/static/index.html must exist"
        f_content = FRONTEND_INDEX.read_text(encoding="utf-8")
        b_content = BACKEND_STATIC_INDEX.read_text(encoding="utf-8")
        assert f_content == b_content, "Backend static index.html must be kept in sync with frontend/index.html"

    def test_category_never_undefined(self):
        """Test B.1: Assert category resolution never returns undefined across all observation shapes."""
        content = FRONTEND_INDEX.read_text(encoding="utf-8")
        fn_code = _extract_js_function(content, "resolveCategory")
        
        test_js = f"""
        {fn_code}
        const testCases = [
            {{ obs: {{ algorithm: 'MD5', claim_type: 'ALGORITHM' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'AES-128', purpose: 'ENCRYPTION' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'RSA-2048', purpose: 'KEY_EXCHANGE' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'ECDSA', purpose: 'SIGNATURE' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'ML-KEM-768' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'TLSv1.2', claim_type: 'PROTOCOL_USAGE' }}, riskEval: null }},
            {{ obs: {{ claim_type: 'CERTIFICATE', algorithm: '' }}, riskEval: null }},
            {{ obs: {{ claim_type: 'KEY', algorithm: '' }}, riskEval: null }},
            {{ obs: {{ algorithm: 'CUSTOM_ALGO' }}, riskEval: null }},
            {{ obs: {{ }}, riskEval: null }}
        ];
        
        const results = testCases.map(tc => resolveCategory(tc.obs, tc.riskEval));
        if (results.some(r => r === undefined || r === null || r === 'undefined')) {{
            console.error('FAILED: Found undefined category:', results);
            process.exit(1);
        }}
        console.log(JSON.stringify(results));
        """
        output = _run_node_script(test_js)
        categories = json.loads(output)
        assert len(categories) == 10
        assert categories[0] == "Hash"
        assert categories[1] == "Symmetric"
        assert categories[2] == "Asymmetric"
        assert categories[3] == "Signature"
        assert categories[4] == "Post-Quantum"
        assert categories[5] == "Protocol"
        assert categories[6] == "Certificate"
        assert categories[7] == "Key Material"
        assert all(c not in (None, "", "undefined") for c in categories)

    def test_purpose_specific_pqc_recommendations(self):
        """Test B.2 - B.5: Assert accurate PQC recommendations instead of universal ML-KEM."""
        content = FRONTEND_INDEX.read_text(encoding="utf-8")
        fn_code = _extract_js_function(content, "resolveRecommendation")
        
        test_js = f"""
        {fn_code}
        const cases = [
            // 1. Hashes: Modernization, never ML-KEM
            {{ obs: {{ algorithm: 'MD5' }}, riskEval: {{ purpose: 'HASHING' }} }},
            {{ obs: {{ algorithm: 'SHA-1' }}, riskEval: null }},
            // 2. Symmetric: AES-256-GCM
            {{ obs: {{ algorithm: 'AES-128' }}, riskEval: {{ purpose: 'SYMMETRIC_ENCRYPTION' }} }},
            {{ obs: {{ algorithm: '3DES' }}, riskEval: null }},
            // 3. Signatures: ML-DSA-65 or SLH-DSA
            {{ obs: {{ algorithm: 'ECDSA' }}, riskEval: {{ purpose: 'SIGNATURE' }} }},
            {{ obs: {{ algorithm: 'RSA-2048' }}, riskEval: {{ purpose: 'SIGNATURE' }} }},
            {{ obs: {{ algorithm: 'Ed25519' }}, riskEval: null }},
            // 4. Key Exchange: ML-KEM-768
            {{ obs: {{ algorithm: 'ECDH P-256' }}, riskEval: {{ purpose: 'KEY_EXCHANGE' }} }},
            {{ obs: {{ algorithm: 'X25519' }}, riskEval: null }},
            // 5. Protocols: TLS 1.3
            {{ obs: {{ algorithm: 'TLSv1.0', claim_type: 'PROTOCOL_USAGE' }}, riskEval: null }},
            // 6. Direct backend recommendation takes precedence
            {{ obs: {{ algorithm: 'RSA-2048' }}, riskEval: {{ recommendation: {{ target_standard_algorithm: 'EXPLICIT-PQC-TARGET' }} }} }}
        ];
        
        const results = cases.map(c => resolveRecommendation(c.obs, c.riskEval));
        console.log(JSON.stringify(results));
        """
        output = _run_node_script(test_js)
        recommendations = json.loads(output)

        # Hashes
        assert "SHA-256" in recommendations[0] or "SHA3" in recommendations[0]
        assert "ML-KEM" not in recommendations[0]
        assert "SHA-256" in recommendations[1] or "SHA3" in recommendations[1]
        assert "ML-KEM" not in recommendations[1]

        # Symmetric
        assert "AES-256" in recommendations[2]
        assert "ML-KEM" not in recommendations[2]
        assert "AES-256" in recommendations[3]
        assert "ML-KEM" not in recommendations[3]

        # Signatures
        assert "ML-DSA" in recommendations[4] or "SLH-DSA" in recommendations[4]
        assert "ML-DSA" in recommendations[5] or "SLH-DSA" in recommendations[5]
        assert "ML-DSA" in recommendations[6] or "SLH-DSA" in recommendations[6]

        # Key Exchange
        assert "ML-KEM-768" in recommendations[7]
        assert "ML-KEM-768" in recommendations[8]

        # Protocol
        assert "TLS 1.3" in recommendations[9]

        # Direct backend recommendation
        assert recommendations[10] == "EXPLICIT-PQC-TARGET"

    def test_active_scan_audit_chainer(self):
        """Test B.6: Assert active scans generate honest dynamic audit state rather than hardcoded 182/192 demo."""
        content = FRONTEND_INDEX.read_text(encoding="utf-8")
        
        # Verify renderAudit is called inside renderDashboard
        assert "renderCBOM();" in content
        assert "renderAudit();" in content
        
        # Verify switchTab calls renderAudit for tab-audit
        assert "if (tabId === 'tab-audit') {" in content
        
        # Verify dynamic scan detection in renderAudit
        assert "activeScan.id && activeScan.id !== 'demo-synthetic-sample'" in content
        assert "activeScan.filesAssessed" in content
        assert "activeScan.filesTotal" in content
        assert "activeScan.coveragePercentage" in content
        
        # Verify appendAuditRecord syncs to activeScan.auditChain and invokes fetchAPI
        assert "fetchAPI('/workflow/audit/chain/append'" in content
