import React, { useState, useMemo } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { usePageTitle } from '../hooks/usePageTitle';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import EmptyState from '../components/common/EmptyState';
import {
  CbomSummary,
  CbomInventoryTable,
  CbomAlgorithmMatrix,
  CbomDetailModal,
  CbomExportModal,
  normalizeCbomInventory,
} from '../components/cbom';
import { Download } from 'lucide-react';
import './CbomPage.css';

/**
 * Dedicated Cryptographic Bill of Materials (CBOM) Page
 */
export default function CbomPage() {
  usePageTitle('Cryptographic Bill of Materials (CBOM)');
  const [searchParams, setSearchParams] = useSearchParams();
  const requestedScanId = searchParams.get('scanId');

  // 1. Fetch available scans list
  const {
    data: scansData,
    loading: scansLoading,
    error: scansError,
    refetch: refetchScans,
  } = useApi('/api/v1/scans');

  const scans = Array.isArray(scansData?.scans)
    ? scansData.scans
    : Array.isArray(scansData)
    ? scansData
    : [];

  // Determine active scan ID
  const activeScanId =
    requestedScanId ||
    (scans.length > 0 ? scans[0].scan_id || scans[0].id : null);

  // 2. Fetch complete scan record
  const {
    data: scanData,
    loading: scanLoading,
    error: scanError,
    refetch: refetchScan,
  } = useApi(activeScanId ? `/api/v1/scans/${activeScanId}` : null, {
    enabled: Boolean(activeScanId),
  });

  const [selectedComponent, setSelectedComponent] = useState(null);
  const [isExportOpen, setIsExportOpen] = useState(false);

  // Normalize CBOM components from scan data
  const cbomComponents = useMemo(() => {
    if (!scanData) return [];
    return normalizeCbomInventory(
      scanData.canonical_assets || [],
      scanData.observations || []
    );
  }, [scanData]);

  const handleScanChange = (newScanId) => {
    setSearchParams(newScanId ? { scanId: newScanId } : {});
  };

  if (scansLoading && !scansData) {
    return (
      <div className="cbom-page" data-testid="cbom-page-loading">
        <LoadingSpinner label="Loading cryptographic inventory & CBOM records..." />
      </div>
    );
  }

  if (scansError && !scansData) {
    return (
      <div className="cbom-page" data-testid="cbom-page-error">
        <ErrorBanner
          title="Unable to load scans list"
          message={scansError}
          onRetry={refetchScans}
        />
      </div>
    );
  }

  if (scans.length === 0 && !activeScanId) {
    return (
      <div className="cbom-page" data-testid="cbom-page-empty">
        <EmptyState
          title="No Scans Available for CBOM Generation"
          message="Scan a repository to generate a full CycloneDX 1.6 Cryptographic Bill of Materials (CBOM)."
          ctaLabel="Initiate New Scan"
          ctaTo="/scan"
        />
      </div>
    );
  }

  const targetName = scanData?.target_name || scanData?.manifest?.archive_name || 'Software Target';

  return (
    <div className="cbom-page" data-testid="cbom-page">
      {/* Top Header */}
      <header className="cbom-page-header">
        <div className="cbom-page-title-group">
          <div className="cbom-page-meta-breadcrumbs">
            <Link to="/" style={{ color: 'var(--accent-primary)', textDecoration: 'none' }}>
              ← Dashboard
            </Link>
            <span>/</span>
            <span>Cryptographic Bill of Materials</span>
          </div>

          <h1 className="cbom-page-title">
            <span>Cryptographic Bill of Materials (CBOM)</span>
            <Badge variant="primary">CycloneDX 1.6</Badge>
          </h1>
          <p className="cbom-page-subtitle">
            Complete architectural inventory of cryptographic primitives, algorithm properties, parameters, and detection provenance in <em>{targetName}</em>.
          </p>
        </div>

        {/* Scan Selector & Export Trigger */}
        <div className="cbom-header-actions">
          {scans.length > 0 && (
            <div className="cbom-scan-selector-box">
              <label htmlFor="cbom-scan-picker" className="cbom-scan-picker-label">
                Active Scan:
              </label>
              <select
                id="cbom-scan-picker"
                value={activeScanId || ''}
                onChange={(e) => handleScanChange(e.target.value)}
                className="cbom-scan-picker-select"
                aria-label="Select scan for CBOM generation"
                data-testid="cbom-scan-picker"
              >
                {scans.map((s) => {
                  const id = s.scan_id || s.id;
                  const name = s.target_name || s.archive_name || id;
                  return (
                    <option key={id} value={id}>
                      {name} ({id.slice(0, 12)})
                    </option>
                  );
                })}
              </select>
            </div>
          )}

          <Button
            variant="primary"
            size="sm"
            onClick={() => setIsExportOpen(true)}
            data-testid="open-export-modal-btn"
          >
            <Download size={15} aria-hidden="true" />
            <span>Export CycloneDX 1.6</span>
          </Button>
        </div>
      </header>

      {/* Main Content Area */}
      {scanLoading && !scanData ? (
        <div className="cbom-loading-area" data-testid="cbom-loading-area">
          <LoadingSpinner label="Constructing CycloneDX cryptographic inventory..." />
        </div>
      ) : scanError ? (
        <ErrorBanner
          title="Failed to Load CBOM Records"
          message={scanError}
          onRetry={refetchScan}
        />
      ) : (
        <div className="cbom-content-stack">
          {/* Summary Overview */}
          <CbomSummary
            components={cbomComponents}
            scan={scanData}
            onExportClick={() => setIsExportOpen(true)}
          />

          {/* Algorithm Classification Matrix */}
          <CbomAlgorithmMatrix
            components={cbomComponents}
            onSelectAlgorithm={() => {}}
          />

          {/* Full Cryptographic Inventory Table */}
          <section className="cbom-inventory-section" aria-label="Cryptographic Components Table">
            <div className="cbom-section-header-row">
              <h2 className="cbom-section-heading">Cryptographic Component Inventory</h2>
              <span className="cbom-section-subtext">
                Inspect algorithm specifications, parameter sets, execution environments, and detection provenance.
              </span>
            </div>

            <CbomInventoryTable
              components={cbomComponents}
              onSelectComponent={(comp) => setSelectedComponent(comp)}
            />
          </section>
        </div>
      )}

      {/* Component Detail Modal */}
      <CbomDetailModal
        component={selectedComponent}
        open={Boolean(selectedComponent)}
        onClose={() => setSelectedComponent(null)}
      />

      {/* CycloneDX 1.6 Export Modal */}
      <CbomExportModal
        open={isExportOpen}
        onClose={() => setIsExportOpen(false)}
        scanId={activeScanId}
        archiveName={targetName}
      />
    </div>
  );
}
