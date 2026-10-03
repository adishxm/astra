"""
ASTRA - Enterprise Cryptographic Discovery & Post-Quantum Governance Tool
Command-Line Interface (CLI)

Supports zero-dependency operation in air-gapped sovereign environments.
Commands:
  astra version                    Show system version, standards & operational profile
  astra scan <path> [--format]     Analyze a directory or archive (.zip, .tar.gz)
  astra show <scan_id>             Display inventory & coverage of a scan
  astra risk <scan_id>             Evaluate Mosca theorem & PQC migration backlog
  astra export <scan_id>           Export CycloneDX 1.6 Cryptographic BOM (CBOM)
  astra validate <scan_id>         Validate CBOM against CycloneDX 1.6 schema
  astra serve [--port] [--host]    Launch local FastAPI web server & Dashboard
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

from app.services.scan_service import GLOBAL_SCAN_SERVICE, GLOBAL_SCAN_STORE
from app.inventory.cbom_reconciliation import CBOMReconciliationEngine
from app.risk.models import ContextFactors, RiskScenario
from app.risk.scorer import RiskScorer

VERSION = "1.0.0"


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    """Render a clean ANSI-compatible terminal table."""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            if idx < len(col_widths):
                col_widths[idx] = max(col_widths[idx], len(str(val)))

    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_str = "| " + " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers)) + " |"

    lines = [sep, header_str, sep]
    for row in rows:
        line_str = "| " + " | ".join(f"{str(row[i]):<{col_widths[i]}}" for i in range(len(headers))) + " |"
        lines.append(line_str)
    lines.append(sep)
    return "\n".join(lines)


def cmd_version(args) -> int:
    """Print ASTRA version, standards, and operational profile."""
    print(f"ASTRA (Enterprise Cryptographic Discovery & Analysis Tool) v{VERSION}")
    print("NIST Post-Quantum Standards: FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA)")
    print("Operational Profile: AIR_GAPPED_SOVEREIGN_ENTERPRISE")
    print("CycloneDX CBOM Specification: 1.6 Conformance")
    return 0


def cmd_scan(args) -> int:
    """Execute cryptographic discovery and risk analysis on target path."""
    target_path = Path(args.path).resolve()
    if not target_path.exists():
        print(f"Error: Target path does not exist: {args.path}", file=sys.stderr)
        return 1

    print(f"[*] Initiating ASTRA scan on target: {target_path}")

    # Determine if archive or directory
    if target_path.is_file():
        record = GLOBAL_SCAN_SERVICE.run_scan_on_archive(str(target_path))
    else:
        record = GLOBAL_SCAN_SERVICE.run_scan_on_directory(str(target_path))

    rec_dict = record.to_dict()

    if args.format == "json":
        output_str = json.dumps(rec_dict, indent=2, default=str)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_str)
            print(f"[+] Scan report written to {args.output}")
        else:
            print(output_str)
        return 0

    # Table output format
    summary = rec_dict["summary"]
    print("\n" + "=" * 65)
    print(f" ASTRA SCAN COMPLETE — Scan ID: {record.scan_id}")
    print("=" * 65)
    print(f"Target Name:          {record.target_name}")
    print(f"Coverage Assessment:  {summary['assessed_files']} / {summary['total_files']} files ({summary['coverage_percentage']}%)")
    print(f"Clean State Status:   {summary['clean_state_label']}")
    print(f"Cryptographic Assets: {rec_dict['asset_count']} unique components identified")
    print(f"Cryptographic DNA:    {rec_dict['cryptographic_dna_hash'][:16]}...{rec_dict['cryptographic_dna_hash'][-8:]}")
    print(f"Urgency Breakdown:    CRITICAL: {summary['critical_urgency_count']} | HIGH: {summary['high_urgency_count']} | MEDIUM: {summary['medium_urgency_count']} | LOW: {summary['low_urgency_count']}")
    print("-" * 65)

    if record.canonical_assets:
        rows = []
        for asset in record.canonical_assets:
            for obs in asset.observations:
                loc = f"{obs.relative_path}:{obs.start_line or '?'}"
                rows.append([
                    obs.algorithm or "UNKNOWN",
                    str(obs.key_size_bits or "N/A"),
                    obs.source_kind.value if hasattr(obs.source_kind, 'value') else str(obs.source_kind),
                    loc,
                    obs.confidence.value if hasattr(obs.confidence, 'value') else str(obs.confidence),
                ])
        print("\nIdentified Cryptographic Inventory:")
        print(format_table(["Algorithm", "Key Bits", "Source Kind", "Location", "Confidence"], rows[:15]))
        if len(rows) > 15:
            print(f"... and {len(rows) - 15} more findings.")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(rec_dict, f, indent=2, default=str)
        print(f"\n[+] Full scan report written to: {args.output}")
    return 0


def cmd_show(args) -> int:
    """Show details of a previously executed scan."""
    data = GLOBAL_SCAN_STORE.get(args.scan_id)
    if not data:
        print(f"Error: Scan ID not found: {args.scan_id}", file=sys.stderr)
        return 1

    rec = data if isinstance(data, dict) else data.to_dict()
    print(f"Scan ID:             {rec['scan_id']}")
    print(f"Target:              {rec['target_name']}")
    print(f"Created At:          {rec['created_at']}")
    cov = rec.get("coverage", {})
    cov_pct = cov.get("overall_coverage_percentage", cov.get("coverage_percentage", 0.0))
    status_lbl = cov.get("scan_status_label", cov.get("clean_state_label", "UNKNOWN"))
    print(f"Coverage:            {cov_pct}%")
    print(f"Clean State Label:   {status_lbl}")
    print(f"Cryptographic DNA:   {rec.get('cryptographic_dna_hash', 'N/A')}")
    return 0


def cmd_risk(args) -> int:
    """Inspect Mosca theorem calculation and candidate PQC backlog."""
    data = GLOBAL_SCAN_STORE.get(args.scan_id)
    if not data:
        print(f"Error: Scan ID not found: {args.scan_id}", file=sys.stderr)
        return 1

    rec = data if isinstance(data, dict) else data.to_dict()
    evals = rec.get("risk_evaluations", [])

    print(f"[*] Risk & Mosca Horizon Analysis for Scan: {args.scan_id}")
    print(f"Active Scenario: Quantum Horizon Z = {args.horizon} yrs | Shelf-Life X = {args.shelf_life} yrs | Migration Y = {args.migration} yrs\n")

    rows = []
    for ev in evals:
        urgency = ev.get("urgency", "UNKNOWN")
        score = ev.get("risk_score", 0.0)
        algo = ev.get("algorithm", "UNKNOWN")
        viol = "YES (SNDL Risk)" if ev.get("mosca_condition_violated") else "No"
        rows.append([algo, str(score), urgency, viol])

    if rows:
        print(format_table(["Algorithm", "Risk Score", "Urgency Tier", "Mosca Violated"], rows))
    else:
        print("No cryptographic observations to evaluate.")
    return 0


def cmd_export(args) -> int:
    """Export CycloneDX 1.6 Cryptographic Bill of Materials (CBOM)."""
    data = GLOBAL_SCAN_STORE.get(args.scan_id)
    if not data:
        print(f"Error: Scan ID not found: {args.scan_id}", file=sys.stderr)
        return 1

    rec = data if isinstance(data, dict) else data.to_dict()
    cbom = rec.get("cbom_data", {})

    output_str = json.dumps(cbom, indent=2, default=str)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
        print(f"[+] CycloneDX 1.6 CBOM exported to: {args.output}")
    else:
        print(output_str)
    return 0


def cmd_validate(args) -> int:
    """Validate scan CBOM against CycloneDX 1.6 schema."""
    data = GLOBAL_SCAN_STORE.get(args.scan_id)
    if not data:
        print(f"Error: Scan ID not found: {args.scan_id}", file=sys.stderr)
        return 1

    rec = data if isinstance(data, dict) else data.to_dict()
    cbom = rec.get("cbom_data", {})

    engine = CBOMReconciliationEngine()
    res = engine.validate_cyclonedx_16(cbom)

    if res.is_valid:
        print(f"[SUCCESS] CBOM for scan {args.scan_id} is VALID under CycloneDX 1.6.")
        print(f"Cryptographic Components: {res.crypto_components_count}")
        return 0
    else:
        print(f"[FAILED] CBOM validation errors:")
        for err in res.validation_errors:
            print(f" - {err}")
        return 1


def cmd_serve(args) -> int:
    """Launch ASTRA FastAPI Web Service and Dashboard."""
    import uvicorn
    print(f"[*] Starting ASTRA Server at http://{args.host}:{args.port}")
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint parser."""
    parser = argparse.ArgumentParser(
        prog="astra",
        description="ASTRA — Enterprise Cryptographic Discovery & Post-Quantum Analysis Tool",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # astra version
    subparsers.add_parser("version", help="Show ASTRA system version and supported NIST PQC standards")

    # astra scan
    scan_parser = subparsers.add_parser("scan", help="Scan a directory or archive file")
    scan_parser.add_argument("path", help="Path to local folder or archive (.zip, .tar.gz)")
    scan_parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    scan_parser.add_argument("--output", "-o", help="Write report to specified file path")

    # astra show
    show_parser = subparsers.add_parser("show", help="Display details of a previous scan")
    show_parser.add_argument("scan_id", help="Scan ID to display")

    # astra risk
    risk_parser = subparsers.add_parser("risk", help="Inspect Mosca risk calculation & PQC backlog")
    risk_parser.add_argument("scan_id", help="Scan ID to inspect")
    risk_parser.add_argument("--horizon", type=float, default=10.0, help="Quantum threat horizon Z in years")
    risk_parser.add_argument("--shelf-life", type=float, default=5.0, help="Data shelf-life X in years")
    risk_parser.add_argument("--migration", type=float, default=3.0, help="Migration duration Y in years")

    # astra export
    export_parser = subparsers.add_parser("export", help="Export CycloneDX 1.6 CBOM")
    export_parser.add_argument("scan_id", help="Scan ID to export")
    export_parser.add_argument("--format", choices=["cbom", "json"], default="cbom", help="Export format")
    export_parser.add_argument("--output", "-o", help="Output file path")

    # astra validate
    val_parser = subparsers.add_parser("validate", help="Validate CBOM against CycloneDX 1.6")
    val_parser.add_argument("scan_id", help="Scan ID to validate")

    # astra serve
    serve_parser = subparsers.add_parser("serve", help="Start the ASTRA HTTP server & Dashboard")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    serve_parser.add_argument("--reload", action="store_true", help="Auto-reload on code change")

    parsed_args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if not parsed_args.command:
        parser.print_help()
        return 0

    dispatch = {
        "version": cmd_version,
        "scan": cmd_scan,
        "show": cmd_show,
        "risk": cmd_risk,
        "export": cmd_export,
        "validate": cmd_validate,
        "serve": cmd_serve,
    }

    cmd_fn = dispatch.get(parsed_args.command)
    if cmd_fn:
        res = cmd_fn(parsed_args)
        return res if isinstance(res, int) else 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
