# ASTRA Frontend — P02 "Project Scaffold & Tooling" Notes

> **Document Status:** Complete & Verified on `feat/frontend-p01-p02-clean`  
> **Environment:** Node `v24.16.0`, npm `11.13.0`, Windows 10/11 x64  
> **Backend Compatibility:** 88/88 backend pytest tests passing

---

## 1. Installed Package Versions & Runtime Environment

### Environment Versions
- **Node.js:** `v24.16.0`
- **npm:** `11.13.0`
- **Python:** `3.11.9` (FastAPI / Uvicorn backend)

### Production Dependencies (`frontend/package.json`)
```json
{
  "dependencies": {
    "@fontsource/jetbrains-mono": "^5.3.0",
    "@fontsource/outfit": "^5.3.0",
    "lucide-react": "^1.51.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-hot-toast": "^2.6.1",
    "react-router-dom": "^6.30.6",
    "recharts": "^3.10.1"
  }
}
```

### Dev Dependencies & Tooling (`frontend/package.json`)
```json
{
  "devDependencies": {
    "@eslint/js": "^9.10.0",
    "@testing-library/jest-dom": "^6.5.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/user-event": "^14.5.0",
    "@vitejs/plugin-react": "^4.3.4",
    "@vitest/coverage-v8": "^2.1.0",
    "eslint": "^9.10.0",
    "eslint-plugin-jsx-a11y": "^6.10.0",
    "eslint-plugin-react": "^7.35.0",
    "eslint-plugin-react-hooks": "^5.1.0",
    "eslint-plugin-react-refresh": "^0.4.12",
    "globals": "^15.9.0",
    "jsdom": "^24.1.0",
    "vite": "^5.0.0",
    "vitest": "^2.1.0"
  }
}
```

---

## 2. Backend Static Serving Architecture & Verification

### How does the backend serve `/` today?
In `backend/app/main.py` (lines 348–360):
```python
STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if not STATIC_DIR.exists():
    STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

if (STATIC_DIR / "index.html").exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    def serve_dashboard():
        """Serve the interactive ASTRA Web Dashboard."""
        return FileResponse(STATIC_DIR / "index.html")
```

### Discovery & Impact:
1. **Prior to Vite Build:** `frontend/dist/` did not exist, so FastAPI fell back to `backend/app/static/index.html` (the legacy prototype).
2. **After Vite Build (`npm run build`):** FastAPI locates `frontend/dist/index.html` and serves the compiled React production bundle at `GET /`.
3. **Backend Test Compatibility:** `backend/tests/test_e2e_product.py` line 175 asserts `assert "CycloneDX" in resp.text` when querying `GET /`. By including the standardized meta description referencing CycloneDX 1.6 CBOM in `frontend/index.html`, the compiled `dist/index.html` satisfies this assertion and passes all 88/88 backend tests with zero modifications to `backend/`.
4. **Legacy Preservation:** The original prototype has been copied to `frontend/legacy/index.static.html` for reference.

---

## 3. Security Audit & Offline Sovereignty Check

### `npm audit --omit=dev` Findings
Running `npm audit --omit=dev` reported 2 moderate vulnerabilities in `react-router` / `react-router-dom` 6.x (CVE-2025-68470 regarding open redirect in SSR/hydration). Per specification requirements, React Router is pinned to v6 (`^6.30.6`) without upgrading to v7 breaking changes. No critical runtime vulnerabilities exist in the client-side SPA bundle.

### Offline & Sovereign Principle Verification
- All fonts are self-hosted via `@fontsource/outfit` and `@fontsource/jetbrains-mono`, bundled locally as WOFF2 assets into `dist/assets/`.
- No Google Fonts, external CDNs, or tracking scripts are referenced in `index.html` or the bundle.
- Searching the compiled distribution for external URLs confirmed that only internal namespace strings (`http://www.w3.org/2000/svg`) and React's offline error decoder URL exist. **Zero external network requests are made at runtime.**

---

## 4. Deviations & Technical Adjustments

| Target | Spec Mention | Adjustment Made | Rationale |
|---|---|---|---|
| `@vitejs/plugin-react` | `@vitejs/plugin-react` (latest) | Pinned to `^4.3.4` | `@vitejs/plugin-react` v6+ requires Vite 8; Vite 5.x requires plugin v4.x. |
| `vitest` / `@vitest/coverage-v8` | `vitest` | Installed `^2.1.0` | Compatible with Vite 5.x and Node 20/24. |
| `react-hot-toast` | Phase Ab list | Installed in P02 | Required in Phase Aa for 404 scan redirect notifications. |
| `index.html` metadata | Minimal head | Added CycloneDX description meta tag | Required to satisfy backend test `test_e2e_product.py:test_web_dashboard_html_served` without editing `backend/`. |

---

## 5. Architectural Invariants for Subsequent Phases (P03–P06)

Decisions carried forward from P01 and P02 that all future implementation phases must follow:

1. **Truthful Upload Progress:** Show real network upload percentage via `XMLHttpRequest.upload.onprogress` (0–100%), followed by an "Analyzing Cryptographic Primitives..." spinner with an elapsed timer. Do **not** invent mock stage names that the server does not report.
2. **Authentic Audit Event Log:** The `/audit` page must render only real events appended during the session (cached in `localStorage`), with a visible note that the backend does not provide an historical event list. Do **not** seed fake historical audit records.
3. **Evidence Drilldown Data Source:** Use `findings.observations[]` for evidence inspection. Do not rely on `GET /api/v1/workflow/evidence/{asset_id}` due to the backend router route collision identified in P01.
4. **Explicit Labels for Derived Data:** The Migration Roadmap, Temporal Drift comparison, and Multi-Scanner Reconciliation views must clearly indicate when calculations are derived client-side or use simulation models.
