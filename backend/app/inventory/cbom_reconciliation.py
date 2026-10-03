"""ASTRA - CBOM Multi-Generator Reconciliation & Conformance Engine (Worker 02 - PROD-02).

Implements:
- CycloneDX 1.6 Cryptographic Bill of Materials (CBOM) specification validator
- Multi-generator reconciliation across independent scanners (e.g. ASTRA, IBM CBOM, CycloneDX CLI)
- Discrepancy Index measurement and consensus identification
- Preservation of scanner provenance without flattening minority findings
"""

import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class CBOMValidationResult(BaseModel):
    """Result of validating a CBOM against CycloneDX 1.6 / BF-CBOM specifications."""

    is_valid: bool
    spec_format: str = "CycloneDX-1.6-CBOM"
    component_count: int = 0
    crypto_components_count: int = 0
    validation_errors: List[str] = Field(default_factory=list)
    schema_version: str = "1.6"

    @property
    def valid(self) -> bool:
        return self.is_valid

    @property
    def errors(self) -> List[str]:
        return self.validation_errors

    @property
    def crypto_asset_count(self) -> int:
        return self.crypto_components_count

    def __getitem__(self, item: str) -> Any:
        alias_map = {
            "valid": "is_valid",
            "errors": "validation_errors",
            "crypto_asset_count": "crypto_components_count",
        }
        key = alias_map.get(item, item)
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(item)


class ReconciliationResult(BaseModel):
    """Discrepancy and consensus evaluation across multiple CBOM generators."""

    total_scanners: int
    scanners_compared: List[str]
    total_unique_assets: int
    consensus_assets_count: int
    discrepancy_index: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="0.0 = perfect agreement across generators, 1.0 = total divergence",
    )

    consensus_assets: List[Dict[str, Any]] = Field(default_factory=list)
    scanner_specific_assets: Dict[str, List[str]] = Field(default_factory=dict)
    conflicting_attributes: List[Dict[str, Any]] = Field(default_factory=list)
    reconciliation_summary: str
    unified_cbom: Optional[Dict[str, Any]] = None

    @property
    def total_generators(self) -> int:
        return self.total_scanners

    @property
    def unique_assets(self) -> int:
        return self.total_unique_assets

    @property
    def discrepancies(self) -> List[Dict[str, Any]]:
        # Count all assets where there is discrepancy (either conflict or scanner-specific)
        items = list(self.conflicting_attributes)
        for s_name, assets in self.scanner_specific_assets.items():
            for a in assets:
                items.append({"asset_key": a, "exclusive_to": s_name})
        return items

    def __getitem__(self, item: str) -> Any:
        alias_map = {
            "unique_assets": "total_unique_assets",
            "total_generators": "total_scanners",
        }
        key = alias_map.get(item, item)
        if key == "discrepancies":
            return self.discrepancies
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(item)


class CBOMReconciliationEngine:
    """Validates CycloneDX 1.6 CBOM profiles and reconciles output from multiple generators."""

    @staticmethod
    def validate_cyclonedx_16(data: Dict[str, Any]) -> CBOMValidationResult:
        """Validate CBOM JSON conformity to CycloneDX 1.6 cryptographic profile."""
        errors: List[str] = []
        try:
            import jsonschema  # type: ignore
            from pathlib import Path
        except ImportError:
            errors.append("jsonschema is not installed, cannot validate schema")
            return CBOMValidationResult(
                is_valid=False,
                spec_format="CycloneDX-1.6-CBOM" if data.get("specVersion") == "1.6" else f"CycloneDX-{data.get('specVersion')}",
                component_count=0,
                crypto_components_count=0,
                validation_errors=errors,
                schema_version=str(data.get("specVersion", "")),
            )
            
        bom_format = data.get("bomFormat")
        if bom_format != "CycloneDX":
            errors.append(f"Invalid bomFormat: expected 'CycloneDX', got '{bom_format}'")

        spec_version = str(data.get("specVersion", ""))
        if spec_version != "1.6":
            errors.append(f"specVersion '{spec_version}' is not CycloneDX 1.6-aligned")

        schema_path = Path(__file__).parent / "bom-1.6.schema.json"
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            jsonschema.validate(instance=data, schema=schema)
        except Exception as e:
            errors.append(str(e))

        components = data.get("components", [])
        if not isinstance(components, list):
            errors.append("Invalid structure: 'components' must be a list")
            return CBOMValidationResult(
                is_valid=False,
                validation_errors=errors,
                schema_version=spec_version,
            )

        crypto_count = 0
        for idx, comp in enumerate(components):
            if not isinstance(comp, dict):
                continue
            comp_type = comp.get("type", "")
            if comp_type == "cryptographic-asset":
                crypto_count += 1
                crypto_prop = comp.get("cryptoProperties", {})
                if not crypto_prop:
                    errors.append(f"Component '{comp.get('name')}' marked cryptographic-asset lacks cryptoProperties")

        is_valid = len(errors) == 0
        return CBOMValidationResult(
            is_valid=is_valid,
            spec_format="CycloneDX-1.6-CBOM" if spec_version == "1.6" else f"CycloneDX-{spec_version}",
            component_count=len(components),
            crypto_components_count=crypto_count,
            validation_errors=errors,
            schema_version=spec_version,
        )

    def reconcile_generators(
        self,
        scanner_outputs: Union[Dict[str, Dict[str, Any]], List[Dict[str, Any]]],
    ) -> ReconciliationResult:
        """Compare outputs of multiple CBOM generators on the same target.

        Args:
            scanner_outputs: Map of scanner name (e.g. 'ASTRA', 'IBM_CBOM', 'CycloneDX_CLI')
                             to their respective CBOM JSON dictionary, or a list of CBOM dicts.
        """
        if isinstance(scanner_outputs, list):
            normalized = {}
            for idx, item in enumerate(scanner_outputs):
                name = item.get("generator") or item.get("scanner") or f"scanner_{idx}"
                normalized[name] = item
            scanner_outputs = normalized

        scanners = list(scanner_outputs.keys())
        if not scanners:
            return ReconciliationResult(
                total_scanners=0,
                scanners_compared=[],
                total_unique_assets=0,
                consensus_assets_count=0,
                discrepancy_index=0.0,
                reconciliation_summary="No scanner outputs supplied for reconciliation",
            )

        # Asset map: normalized_asset_key -> {scanner_name -> details}
        asset_claims: Dict[str, Dict[str, Dict[str, Any]]] = {}

        for s_name, cbom in scanner_outputs.items():
            components = cbom.get("components", [])
            for comp in components:
                crypto_prop = comp.get("cryptoProperties", {})
                algo = crypto_prop.get("algorithmProperties", {}).get("name") or comp.get("name", "UNKNOWN")
                norm_key = (comp.get("name") or algo).upper().replace("_", "-").replace(" ", "-")

                if norm_key not in asset_claims:
                    asset_claims[norm_key] = {}

                asset_claims[norm_key][s_name] = {
                    "raw_name": comp.get("name"),
                    "algorithm": algo,
                    "type": comp.get("type"),
                    "props": crypto_prop,
                }

        total_unique = len(asset_claims)
        consensus: List[Dict[str, Any]] = []
        scanner_specific: Dict[str, List[str]] = {s: [] for s in scanners}
        conflicting: List[Dict[str, Any]] = []
        unified_components: List[Dict[str, Any]] = []

        for key, claims in asset_claims.items():
            first_claim = list(claims.values())[0]
            unified_components.append({
                "type": first_claim.get("type", "cryptographic-asset"),
                "name": first_claim.get("raw_name") or key.lower(),
                "cryptoProperties": first_claim.get("props", {}),
                "_scanner_provenance": list(claims.keys()),
            })

            # Check if all scanners found this asset
            if len(claims) == len(scanners):
                consensus.append({
                    "name": first_claim.get("raw_name") or key.lower(),
                    "asset_key": key,
                    "detection_count": len(claims),
                    "claims": claims,
                })
            # Check if exclusive to one scanner
            elif len(claims) == 1:
                exclusive_scanner = list(claims.keys())[0]
                scanner_specific[exclusive_scanner].append(key)
            else:
                conflicting.append({
                    "asset_key": key,
                    "participating_scanners": list(claims.keys()),
                    "missing_scanners": list(set(scanners) - set(claims.keys())),
                })

        consensus_count = len(consensus)
        # Discrepancy index calculation: 0.0 = perfect consensus, >0 divergence
        discrepancy = (
            round(1.0 - (consensus_count / total_unique), 4)
            if total_unique > 0
            else 0.0
        )

        summary = (
            f"Reconciled {len(scanners)} CBOM generators across {total_unique} unique assets. "
            f"Consensus rate: {consensus_count}/{total_unique} ({round((1.0 - discrepancy)*100, 1)}%). "
            f"Discrepancy Index: {discrepancy}."
        )

        unified_cbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.6",
            "serialNumber": "urn:uuid:astra-unified-reconciliation",
            "version": 1,
            "components": unified_components,
        }

        return ReconciliationResult(
            total_scanners=len(scanners),
            scanners_compared=scanners,
            total_unique_assets=total_unique,
            consensus_assets_count=consensus_count,
            discrepancy_index=discrepancy,
            consensus_assets=consensus,
            scanner_specific_assets=scanner_specific,
            conflicting_attributes=conflicting,
            reconciliation_summary=summary,
            unified_cbom=unified_cbom,
        )
