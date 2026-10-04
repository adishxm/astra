import React from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import {
  Package,
  Cpu,
  FileCheck2,
  Download,
  Info,
  KeyRound,
} from 'lucide-react';
import './CbomSummary.css';

/**
 * Summary metrics header for Cryptographic Bill of Materials (CBOM).
 *
 * @param {Object} props
 * @param {Array} [props.components=[]]
 * @param {Object} [props.scan=null]
 * @param {() => void} [props.onExportClick]
 * @param {string} [props.className='']
 */
export default function CbomSummary({
  components = [],
  scan = null,
  onExportClick,
  className = '',
}) {
  const items = Array.isArray(components) ? components : [];
  const totalComponents = items.length;

  // Unique Algorithms
  const uniqueAlgorithms = new Set();
  const uniquePurposes = new Set();
  const surfaceCounts = {
    SOURCE_CODE: 0,
    CONFIG: 0,
    MANIFEST: 0,
    CERTIFICATE: 0,
    UNKNOWN: 0,
  };

  items.forEach((item) => {
    if (item.algorithm) uniqueAlgorithms.add(item.algorithm);
    if (item.purpose && item.purpose !== 'UNSPECIFIED') uniquePurposes.add(item.purpose);
    const surface = item.sourceKind ? String(item.sourceKind).toUpperCase() : 'UNKNOWN';
    if (surfaceCounts[surface] !== undefined) {
      surfaceCounts[surface] += 1;
    } else {
      surfaceCounts.UNKNOWN += 1;
    }
  });

  const archiveName = scan?.target_name || scan?.manifest?.archive_name || 'Software Repository';
  const specVersion = 'CycloneDX 1.6';

  return (
    <div className={`cbom-summary-wrapper ${className}`} data-testid="cbom-summary">
      {/* Overview Metrics Cards */}
      <div className="cbom-metrics-grid" role="region" aria-label="CBOM Inventory Overview">
        {/* Total Components */}
        <Card className="cbom-metric-card">
          <div className="cbom-metric-inner">
            <div className="cbom-metric-text">
              <span className="cbom-metric-label">Total Cryptographic Assets</span>
              <span className="cbom-metric-number" data-testid="total-cbom-components">
                {totalComponents}
              </span>
              <span className="cbom-metric-subtext">Components in scope</span>
            </div>
            <div className="cbom-metric-icon-box" aria-hidden="true">
              <Package size={28} className="cbom-icon-primary" />
            </div>
          </div>
        </Card>

        {/* Unique Algorithms */}
        <Card className="cbom-metric-card">
          <div className="cbom-metric-inner">
            <div className="cbom-metric-text">
              <span className="cbom-metric-label">Unique Algorithms</span>
              <span className="cbom-metric-number cbom-color-cyan" data-testid="unique-algos-count">
                {uniqueAlgorithms.size}
              </span>
              <span className="cbom-metric-subtext">Distinct primitives</span>
            </div>
            <div className="cbom-metric-icon-box" aria-hidden="true">
              <Cpu size={28} className="cbom-color-cyan" />
            </div>
          </div>
        </Card>

        {/* Cryptographic Functions */}
        <Card className="cbom-metric-card">
          <div className="cbom-metric-inner">
            <div className="cbom-metric-text">
              <span className="cbom-metric-label">Crypto Functions</span>
              <span className="cbom-metric-number cbom-color-purple" data-testid="unique-purposes-count">
                {uniquePurposes.size}
              </span>
              <span className="cbom-metric-subtext">Declared purposes</span>
            </div>
            <div className="cbom-metric-icon-box" aria-hidden="true">
              <KeyRound size={28} className="cbom-color-purple" />
            </div>
          </div>
        </Card>

        {/* Specification Standard */}
        <Card className="cbom-metric-card">
          <div className="cbom-metric-inner">
            <div className="cbom-metric-text">
              <span className="cbom-metric-label">CBOM Standard</span>
              <span className="cbom-spec-title">{specVersion}</span>
              <span className="cbom-metric-subtext">IEC / NIST PQC Aligned</span>
            </div>
            <div className="cbom-metric-icon-box" aria-hidden="true">
              <FileCheck2 size={28} className="cbom-color-emerald" />
            </div>
          </div>
        </Card>
      </div>

      {/* Surface Distribution & Export Action Bar */}
      <div className="cbom-surface-action-bar">
        <div className="cbom-surfaces-group">
          <span className="cbom-surface-label">Surface Breakdown:</span>
          <div className="cbom-surface-pills">
            <span className="surface-pill" title="Source code detections">
              Source: <strong>{surfaceCounts.SOURCE_CODE}</strong>
            </span>
            <span className="surface-pill" title="Config files detections">
              Configs: <strong>{surfaceCounts.CONFIG}</strong>
            </span>
            <span className="surface-pill" title="Package manifests detections">
              Manifests: <strong>{surfaceCounts.MANIFEST}</strong>
            </span>
            <span className="surface-pill" title="Certificates detections">
              Certificates: <strong>{surfaceCounts.CERTIFICATE}</strong>
            </span>
          </div>
        </div>

        {onExportClick && (
          <div className="cbom-export-btn-box">
            <Button
              variant="primary"
              size="sm"
              onClick={onExportClick}
              data-testid="export-cbom-btn"
              aria-label="Export CycloneDX 1.6 CBOM"
            >
              <Download size={15} aria-hidden="true" />
              <span>Export CycloneDX 1.6 CBOM</span>
            </Button>
          </div>
        )}
      </div>

      {/* Truthfulness Notice */}
      <div className="cbom-truthfulness-banner" role="region" aria-label="CBOM Truthfulness Notice">
        <Info size={16} className="cbom-banner-info-icon" aria-hidden="true" />
        <div className="cbom-banner-text">
          <strong>Cryptographic Inventory Integrity:</strong> The Cryptographic Bill of Materials (CBOM)
          provides a deterministic structural accounting of all cryptographic algorithms, parameters, and protocol
          instances detected in <em>{archiveName}</em>. Inventory inclusion does not indicate risk severity or
          migration urgency. For Mosca theorem timelines ($X + Y &gt; Z$) and risk scoring, inspect the Risk Assessment view.
        </div>
      </div>
    </div>
  );
}
