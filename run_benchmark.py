import os
import shutil
import tempfile
import hashlib
import time
from pathlib import Path
from fastapi.testclient import TestClient
import json

from app.main import app
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
    base_temp = Path(tempfile.mkdtemp(prefix="astra_bench_"))
    proj_b = base_temp / "project_b_node"
    proj_b.mkdir()
    
    (proj_b / "index.js").write_text("const crypto = require('crypto');\nconst hash = crypto.createHash('sha1');\nhash.update('data');\nconsole.log(hash.digest('hex'));")
    (proj_b / "package.json").write_text('{"name": "test", "dependencies": {"crypto-js": "^4.0.0"}}')
    
    record = GLOBAL_SCAN_SERVICE.run_scan_on_directory(str(proj_b), target_name="Node/TS")
    
    print(f"Assets ({len(record.canonical_assets)}): {[a.asset_id for a in record.canonical_assets]}")
    components = record.cbom_data.get("components", [])
    print(f"Components ({len(components)}): {[c['name'] for c in components]}")
    
    shutil.rmtree(base_temp, ignore_errors=True)

if __name__ == "__main__":
    main()
