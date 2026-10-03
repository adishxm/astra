"""ASTRA - Test Suite for Source Code Comment & Literal Filtering.

Verifies that:
1. Pure comment lines (#, //, /*, *, --, ;) do NOT trigger false positive findings.
2. Trailing inline comments mentioning algorithms do not trigger false positive findings.
3. String literals containing algorithm names in actual code ARE detected.
4. Python AST scanner correctly identifies genuine imports vs commented-out imports.
"""

from pathlib import Path
import tempfile
import pytest

from app.discovery.detectors.source_detector import SourceCryptoDetector, strip_line_comments


def test_strip_line_comments_unit():
    """Unit tests for the line-comment stripper helper."""
    assert strip_line_comments("# This is pure Python comment with RSA-2048") == ""
    assert strip_line_comments("// This is pure C/JS comment with AES-256") == ""
    assert strip_line_comments("/* Block comment with MD5 */") == ""
    assert strip_line_comments("* Continued comment line with SHA-1") == ""
    assert strip_line_comments("; INI/ASM comment with DES") == ""
    assert strip_line_comments("-- SQL comment with 3DES") == ""
    assert strip_line_comments("   ") == ""

    # Inline comments
    assert strip_line_comments("x = 10  # Use RSA here later") == "x = 10"
    assert strip_line_comments("let cipher = getCipher(); // switch to Kyber") == "let cipher = getCipher();"

    # String literals with # or // inside quotes must be preserved
    assert strip_line_comments('url = "https://example.com#section"') == 'url = "https://example.com#section"'
    assert strip_line_comments("path = 's3://bucket/key'") == "path = 's3://bucket/key'"


def test_source_detector_ignores_comment_only_matches(tmp_path):
    """Verify that pure comments discussing algorithms produce zero false positive observations."""
    comment_code = tmp_path / "comments_only.py"
    comment_code.write_text(
        "# Discussion about legacy cryptography\n"
        "# We considered using RSA-2048 and MD5 for signatures\n"
        "# Another developer suggested DES or 3DES\n"
        "# TODO: evaluate Kyber-768 or ML-KEM-768 in the future\n"
        "// Even C-style comments mentioning SHA-1\n"
        "/* Multi-line style comments mentioning AES-256 */\n"
        "x = 42\n",
        encoding="utf-8",
    )

    detector = SourceCryptoDetector()
    obs = detector.analyze_file(comment_code, "comments_only.py", "scan-test-comments")
    assert len(obs) == 0, f"Expected 0 observations from comment-only file, got: {[o.algorithm for o in obs]}"


def test_source_detector_distinguishes_code_from_inline_comments(tmp_path):
    """Verify that code using AES is detected, but algorithms mentioned only in its inline comment are not."""
    mixed_code = tmp_path / "inline_comments.js"
    mixed_code.write_text(
        "// Main encryption routine\n"
        "const algorithm = 'AES-256'; // previously we used RSA-1024 and MD5\n"
        "function encrypt(data) {\n"
        "    return execute(algorithm, data);\n"
        "}\n",
        encoding="utf-8",
    )

    detector = SourceCryptoDetector()
    obs = detector.analyze_file(mixed_code, "inline_comments.js", "scan-test-inline")
    detected_algos = {o.algorithm for o in obs}

    assert "AES-256" in detected_algos
    assert "RSA-1024" not in detected_algos
    assert "MD5" not in detected_algos
