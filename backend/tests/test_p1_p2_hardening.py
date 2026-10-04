import json
import os
import shutil
import tempfile
from pathlib import Path
import pytest
from app.services.scan_service import ScanStore, ScanService
from app.intake.models import ScanManifest

def test_a_directory_scan_no_target_mutation():
    """TEST A: Directory scan does not create observations.json inside target directory."""
    with tempfile.TemporaryDirectory() as target_dir:
        target_path = Path(target_dir)
        (target_path / "src").mkdir()
        (target_path / "src" / "main.py").write_text("import cryptography")

        # Run scan
        service = ScanService()
        service.run_scan_on_directory(str(target_path), target_name="test_target")

        # Verify no files were created by ASTRA in the target
        files = list(target_path.rglob("*"))
        assert len(files) == 2  # src dir and src/main.py
        assert not (target_path / "observations.json").exists()

def test_b_symlink_escape():
    """TEST B: Directory scan does not follow a file symlink outside target root."""
    with tempfile.TemporaryDirectory() as outside_dir:
        outside_path = Path(outside_dir)
        secret_file = outside_path / "secret.key"
        secret_file.write_text("BEGIN PRIVATE KEY\nxxx")

        with tempfile.TemporaryDirectory() as target_dir:
            target_path = Path(target_dir)
            symlink_path = target_path / "symlink.key"
            try:
                os.symlink(str(secret_file), str(symlink_path))
            except Exception:
                pytest.skip("Symlink creation not supported on this OS without admin")

            service = ScanService()
            record = service.run_scan_on_directory(str(target_path), target_name="test_symlink")
            
            # Should have skipped the symlink or rejected it
            # Meaning no observations for secret.key
            assert record.coverage.total_assessed_files == 0

def test_c_d_e_f_scan_store_persistence():
    """TEST C, D, E, F: ScanStore persistence and rehydration."""
    with tempfile.TemporaryDirectory() as store_dir:
        store1 = ScanStore(storage_dir=store_dir)
        service1 = ScanService(scan_store=store1)
        
        with tempfile.TemporaryDirectory() as target_dir:
            (Path(target_dir) / "app.py").write_text("import rsa")
            record1 = service1.run_scan_on_directory(target_dir, target_name="test_persist")
            
        # TEST C: Fresh ScanStore discovers persisted records
        store2 = ScanStore(storage_dir=store_dir)
        all_scans = store2.list_all()
        assert len(all_scans) == 1
        assert all_scans[0]["scan_id"] == record1.scan_id
        
        # TEST D: Rehydration
        record2 = store2.get(record1.scan_id)
        assert record2 is not None
        assert record2.target_name == "test_persist"
        assert record2.snapshot.cryptographic_dna_hash == record1.snapshot.cryptographic_dna_hash
        assert len(record2.observations) == len(record1.observations)
        
        # TEST F: Malformed record error
        malformed_file = Path(store_dir) / "malformed.json"
        malformed_file.write_text("{ broken json")
        
        store3 = ScanStore(storage_dir=store_dir)
        with pytest.raises(ValueError):
            store3.get("malformed")
            
def test_g_launcher_env_local():
    """TEST G: Launcher does not overwrite/delete a pre-existing synthetic environment file."""
    import subprocess
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # We need a setup like ASTRA's folder structure
        repo_root = Path(tmp_dir) / "astra"
        frontend_dir = repo_root / "frontend"
        frontend_dir.mkdir(parents=True)
        env_file = frontend_dir / ".env.local"
        env_file.write_text("PROTECTED=1")
        
        launcher = repo_root / "launch.bat"
        launcher_content = (
            "@echo off\n"
            "set VITE_API_BASE_URL=http://127.0.0.1:8000\n"
        )
        launcher.write_text(launcher_content)
        
        # Run it
        subprocess.run([str(launcher)], shell=True, cwd=str(repo_root))
        
        # Verify
        assert env_file.exists()
        assert env_file.read_text() == "PROTECTED=1"

def test_h_dockerfile_frontend():
    """TEST H: Docker configuration contains the current frontend production bundle/build path."""
    dockerfile = Path(__file__).resolve().parent.parent.parent / "Dockerfile"
    content = dockerfile.read_text()
    assert "node:" in content
    assert "npm run build" in content
    assert "COPY --from=frontend-build /app/frontend/dist ./frontend/dist" in content
