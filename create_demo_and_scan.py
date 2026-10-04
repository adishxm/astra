import os
import tempfile
from pathlib import Path
import hashlib

from app.services.scan_service import GLOBAL_SCAN_SERVICE

def hash_dir(d: Path) -> dict:
    hashes = {}
    for root, _, files in os.walk(d):
        for file in files:
            p = Path(root) / file
            if p.is_symlink():
                continue
            with open(p, "rb") as f:
                hashes[str(p.relative_to(d))] = hashlib.sha256(f.read()).hexdigest()
    return hashes

def main():
    base_temp = Path(tempfile.mkdtemp(prefix="astra_golden_"))
    demo_dir = base_temp / "golden_demo"
    demo_dir.mkdir()
    
    # 1. Python cryptographic usage
    (demo_dir / "app.py").write_text("import hashlib\nh = hashlib.md5()\nh.update(b'test')\nimport rsa")
    
    # 2. Node/TS cryptographic usage
    (demo_dir / "index.ts").write_text("import crypto from 'crypto';\nconst hash = crypto.createHash('sha1');\nconst cipher = crypto.createCipheriv('aes-256-cbc', key, iv);")
    
    # 3. Package manifest dependency
    (demo_dir / "package.json").write_text('{"dependencies": {"crypto-js": "^4.1.1", "bcrypt": "^5.0.1"}}')
    
    # 4. Configuration example
    (demo_dir / "config.yaml").write_text("security:\n  algorithm: DES\n  key_size: 512")
    
    # 5. Certificate / PEM
    (demo_dir / "cert_test.pem").write_text("-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3a\n-----END PUBLIC KEY-----")
    
    # Save initial state
    state_before = hash_dir(demo_dir)
    
    # Run scan
    record = GLOBAL_SCAN_SERVICE.run_scan_on_directory(str(demo_dir), target_name="Golden_Demo")
    
    # Save post state
    state_after = hash_dir(demo_dir)
    
    print(f"Location: {demo_dir}")
    print(f"Files Created: {list(state_before.keys())}")
    print(f"Coverage: {record.coverage.overall_coverage_percentage}%")
    print(f"Total Findings: {len(record.observations)}")
    
    print("\nFindings Details:")
    for o in record.observations:
        print(f" - {o.algorithm} ({o.detector_id}) -> {o.relative_path}")
        
    print("\nRisk Analysis:")
    for r in record.risk_evaluations:
        print(f" - Asset {r.asset_id}: {r.urgency.value} / Mosca Viol: {r.mosca_condition_violated}")
        
    print("\nRoadmap / Backlog Items:")
    for b in record.backlog_items:
        print(f" - {b.get('task_title', 'No Title')} (Urgency: {b.get('urgency_level', 'UNKNOWN')})")
        
    print("\nCBOM Generation:")
    cbom = record.cbom_data
    if cbom.get("bomFormat") == "CycloneDX" and "components" in cbom:
        print(f" PASS. Components Generated: {len(cbom['components'])}")
    else:
        print(" FAIL")
        
    print("\nTarget Immutability:")
    if state_before == state_after:
        print(" PASS")
    else:
        print(" FAIL")

if __name__ == '__main__':
    main()
