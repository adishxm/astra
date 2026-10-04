import React, { useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { usePageTitle } from '../hooks/usePageTitle';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import EmptyState from '../components/common/EmptyState';
import {
  MigrationSummary,
  MigrationRoadmapView,
  MigrationTable,
  MigrationDetailModal,
} from '../components/migration';
import { RefreshCw } from 'lucide-react';
import './MigrationPage.css';

/**
 * Migration Planning & Recommendations Page
 */
export default function MigrationPage() {
  usePageTitle('Migration Planning & Recommendations');
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

  const [selectedTask, setSelectedTask] = useState(null);

  const handleScanChange = (newScanId) => {
    setSearchParams(newScanId ? { scanId: newScanId } : {});
  };

  if (scansLoading && !scansData) {
    return (
      <div className="migration-page" data-testid="migration-page-loading">
        <LoadingSpinner label="Loading migration recommendations and roadmap..." />
      </div>
    );
  }

  if (scansError && !scansData) {
    return (
      <div className="migration-page" data-testid="migration-page-error">
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
      <div className="migration-page" data-testid="migration-page-empty">
        <EmptyState
          title="No Scans Available for Migration Planning"
          message="Execute a scan on a codebase to generate actionable post-quantum migration recommendations."
          ctaLabel="Start New Scan"
          ctaTo="/scan"
        />
      </div>
    );
  }

  const targetName = scanData?.target_name || scanData?.manifest?.archive_name || 'Software Target';
  const backlogItems = scanData?.backlog_items || [];

  return (
    <div className="migration-page" data-testid="migration-page">
      {/* Top Header */}
      <header className="migration-page-header">
        <div className="migration-page-title-group">
          <div className="migration-page-meta-breadcrumbs">
            <Link to="/" style={{ color: 'var(--accent-primary)', textDecoration: 'none' }}>
              ← Dashboard
            </Link>
            <span>/</span>
            <span>Migration Planning</span>
          </div>

          <h1 className="migration-page-title">
            <span>Migration Planning & Recommendations</span>
            <Badge variant="primary">NIST FIPS 203/204/205</Badge>
          </h1>
          <p className="migration-page-subtitle">
            Actionable, advisory post-quantum cryptographic upgrade pathways and dependency-ordered roadmap for <em>{targetName}</em>.
          </p>
        </div>

        {/* Scan Selector & Refresh Action */}
        <div className="migration-header-actions">
          {scans.length > 0 && (
            <div className="migration-scan-selector-box">
              <label htmlFor="migration-scan-picker" className="migration-scan-picker-label">
                Active Scan:
              </label>
              <select
                id="migration-scan-picker"
                value={activeScanId || ''}
                onChange={(e) => handleScanChange(e.target.value)}
                className="migration-scan-picker-select"
                aria-label="Select scan for migration planning"
                data-testid="migration-scan-picker"
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
            variant="outline"
            size="sm"
            onClick={refetchScan}
            aria-label="Refresh migration analysis"
          >
            <RefreshCw size={14} aria-hidden="true" />
            <span>Refresh</span>
          </Button>
        </div>
      </header>

      {/* Main Content Area */}
      {scanLoading && !scanData ? (
        <div className="migration-loading-area" data-testid="migration-loading-area">
          <LoadingSpinner label="Constructing phased post-quantum migration pathways..." />
        </div>
      ) : scanError ? (
        <ErrorBanner
          title="Failed to Load Migration Recommendations"
          message={scanError}
          onRetry={refetchScan}
        />
      ) : (
        <div className="migration-content-stack">
          {/* Summary Overview */}
          <MigrationSummary
            tasks={backlogItems}
            scan={scanData}
          />

          {/* Phased Roadmap View */}
          <MigrationRoadmapView
            tasks={backlogItems}
            onSelectTask={(task) => setSelectedTask(task)}
          />

          {/* Migration Recommendations Table */}
          <section className="migration-table-section" aria-label="Actionable Migration Recommendations">
            <div className="migration-section-header-row">
              <h2 className="migration-section-heading">Actionable Migration Work Items</h2>
              <span className="migration-section-subtext">
                Prioritized advisory queue mapping classical cryptographic primitives to standardized NIST post-quantum replacements.
              </span>
            </div>

            <MigrationTable
              tasks={backlogItems}
              onSelectTask={(task) => setSelectedTask(task)}
            />
          </section>
        </div>
      )}

      {/* Task Detail Modal */}
      <MigrationDetailModal
        task={selectedTask}
        open={Boolean(selectedTask)}
        onClose={() => setSelectedTask(null)}
        scanId={activeScanId}
      />
    </div>
  );
}
