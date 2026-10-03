import React, { useState, useEffect } from 'react';
import { useApi } from '../hooks/useApi';
import { usePageTitle } from '../hooks/usePageTitle';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import EmptyState from '../components/common/EmptyState';
import { FindingsTable, FindingDetailModal } from '../components/findings';
import './FindingsPage.css';

/**
 * Global Findings Explorer Page.
 */
export default function FindingsPage() {
  usePageTitle('Findings');

  // 1. Fetch all available scans
  const { data: scans, loading: scansLoading, error: scansError, refetch: refetchScans } = useApi('/api/v1/scans');
  const [selectedScanId, setSelectedScanId] = useState('');
  const [selectedFinding, setSelectedFinding] = useState(null);

  // Default selectedScanId to the first scan when loaded
  useEffect(() => {
    if (Array.isArray(scans) && scans.length > 0 && !selectedScanId) {
      setSelectedScanId(scans[0].scan_id);
    }
  }, [scans, selectedScanId]);

  // 2. Fetch findings for the selected scan
  const {
    data: findingsData,
    loading: findingsLoading,
    error: findingsError,
    refetch: refetchFindings,
  } = useApi(selectedScanId ? `/api/v1/scans/${selectedScanId}/findings` : null);

  if (scansLoading) {
    return (
      <div className="findings-page" data-testid="findings-page-loading">
        <LoadingSpinner label="Loading cryptographic scans..." />
      </div>
    );
  }

  if (scansError) {
    return (
      <div className="findings-page" data-testid="findings-page-error">
        <ErrorBanner
          title="Failed to load scans"
          message={scansError}
          onRetry={refetchScans}
        />
      </div>
    );
  }

  if (!Array.isArray(scans) || scans.length === 0) {
    return (
      <div className="findings-page" data-testid="findings-page-empty">
        <EmptyState
          title="No Cryptographic Scans Available"
          message="No discovery scans have been performed yet. Upload an archive or source repository to detect cryptographic algorithms, certificates, and keys."
          ctaLabel="Run First Scan"
          ctaTo="/scan"
        />
      </div>
    );
  }

  return (
    <div className="findings-page" data-testid="findings-page">
      {/* Page Header */}
      <header className="findings-page-header">
        <div className="findings-page-title-group">
          <h1 className="findings-page-title">Cryptographic Findings</h1>
          <p className="findings-page-description">
            Explore identified cryptographic algorithms, key lengths, certificates, configuration settings, and confidence rationales across scans.
          </p>
        </div>

        <div className="scan-selector-group">
          <label htmlFor="scan-picker" style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-dim)', fontWeight: 600 }}>
            TARGET SCAN:
          </label>
          <select
            id="scan-picker"
            className="scan-selector-select"
            value={selectedScanId}
            onChange={(e) => setSelectedScanId(e.target.value)}
            aria-label="Select target scan"
          >
            {scans.map((s) => (
              <option key={s.scan_id} value={s.scan_id}>
                {s.target_name || s.scan_id} ({s.asset_count ?? 0} assets)
              </option>
            ))}
          </select>
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              refetchScans();
              refetchFindings();
            }}
          >
            Refresh
          </Button>
        </div>
      </header>

      {/* Main Content Area */}
      {findingsLoading ? (
        <LoadingSpinner label="Loading findings for selected scan..." />
      ) : findingsError ? (
        <ErrorBanner
          title="Failed to load scan findings"
          message={findingsError}
          onRetry={refetchFindings}
        />
      ) : (
        <section aria-label="Findings Table Section">
          <FindingsTable
            canonicalAssets={findingsData?.canonical_assets || []}
            directObservations={findingsData?.observations || []}
            onSelectFinding={(finding) => setSelectedFinding(finding)}
          />
        </section>
      )}

      {/* Finding Detail Modal */}
      <FindingDetailModal
        finding={selectedFinding}
        open={Boolean(selectedFinding)}
        onClose={() => setSelectedFinding(null)}
      />
    </div>
  );
}
