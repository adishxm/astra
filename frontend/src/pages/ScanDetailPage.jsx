import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { usePageTitle } from '../hooks/usePageTitle';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import ProgressRing from '../components/common/ProgressRing';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import EmptyState from '../components/common/EmptyState';
import { FindingsTable, FindingDetailModal } from '../components/findings';
import './ScanDetailPage.css';

/**
 * Scan Results & Findings Detail Page.
 */
export default function ScanDetailPage() {
  const { scanId } = useParams();
  usePageTitle(`Scan ${scanId || 'Details'}`);

  const { data: scan, loading, error, refetch } = useApi(scanId ? `/api/v1/scans/${scanId}` : null);
  const [selectedFinding, setSelectedFinding] = useState(null);

  if (loading) {
    return (
      <div className="scan-detail-page" data-testid="scan-detail-loading">
        <LoadingSpinner label="Loading scan results and cryptographic findings..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="scan-detail-page" data-testid="scan-detail-error">
        <ErrorBanner
          title="Unable to load scan results"
          message={error}
          onRetry={refetch}
        />
        <div style={{ marginTop: 'var(--space-md)' }}>
          <Link to="/">
            <Button variant="outline">← Back to Dashboard</Button>
          </Link>
        </div>
      </div>
    );
  }

  if (!scan) {
    return (
      <div className="scan-detail-page" data-testid="scan-detail-notfound">
        <EmptyState
          title="Scan Result Unavailable"
          message={`No scan record was found for identifier "${scanId}". It may have expired or been deleted.`}
          ctaLabel="Return to Dashboard"
          ctaTo="/"
        />
      </div>
    );
  }

  // Extract scan properties with truthfulness
  const targetName = scan.target_name || scan.manifest?.archive_name || 'Target Archive';
  const status = scan.status ? scan.status.toUpperCase() : 'UNKNOWN';
  const createdAt = scan.created_at ? new Date(scan.created_at).toLocaleString() : 'Date unrecorded';
  const assetCount = typeof scan.asset_count === 'number' ? scan.asset_count : (scan.canonical_assets?.length ?? 'N/A');
  const coveragePct = scan.coverage?.overall_coverage_percentage ?? scan.summary?.coverage_percentage ?? scan.coverage_percentage ?? null;
  const cleanStateLabel = scan.clean_state_label || scan.coverage?.scan_status_label || scan.summary?.clean_state_label || 'UNASSESSED';
  const dnaHash = scan.cryptographic_dna_hash || scan.dna_hash || null;
  const canonicalAssets = scan.canonical_assets || [];
  const riskEvaluations = scan.risk_evaluations || [];
  const summary = scan.summary || {};
  const surfaceBreakdown = scan.coverage?.surface_breakdown || {};

  // Urgency counts
  const critCount = summary.critical_urgency_count ?? 0;
  const highCount = summary.high_urgency_count ?? 0;
  const medCount = summary.medium_urgency_count ?? 0;
  const lowCount = summary.low_urgency_count ?? 0;

  return (
    <div className="scan-detail-page" data-testid="scan-detail-page">
      {/* Header Banner */}
      <header className="scan-detail-header">
        <div className="scan-title-group">
          <div className="scan-meta-row">
            <Link to="/" style={{ color: 'var(--accent-primary)', textDecoration: 'none' }}>
              ← Dashboard
            </Link>
            <span>/</span>
            <span>Scan Results</span>
          </div>

          <h1 className="scan-title">
            <span>{targetName}</span>
            <Badge
              variant={
                status === 'COMPLETED' || status === 'COMPLETE'
                  ? 'high'
                  : status === 'RUNNING'
                  ? 'primary'
                  : 'neutral'
              }
            >
              {status}
            </Badge>
          </h1>

          <div className="scan-meta-row">
            <span>Scan ID: <code>{scan.scan_id || scanId}</code></span>
            <span>•</span>
            <span>Recorded: {createdAt}</span>
            {dnaHash && (
              <>
                <span>•</span>
                <span className="scan-dna-pill" title={`DNA Hash: ${dnaHash}`}>
                  DNA: {dnaHash}
                </span>
              </>
            )}
          </div>
        </div>

        <div>
          <Button variant="outline" size="sm" onClick={refetch}>
            Refresh Results
          </Button>
        </div>
      </header>

      {/* Metrics Row */}
      <section className="scan-metrics-grid" aria-label="Scan Metrics Summary">
        <Card>
          <div className="metric-card-content">
            <div className="metric-text-group">
              <span className="metric-label-dim">Discovered Assets</span>
              <span className="metric-value-huge">{assetCount}</span>
              <span className="metric-subtext">Cryptographic primitives</span>
            </div>
            <div style={{ fontSize: '2rem', opacity: 0.8 }} aria-hidden="true">
              🔐
            </div>
          </div>
        </Card>

        <Card>
          <div className="metric-card-content">
            <div className="metric-text-group">
              <span className="metric-label-dim">Assessed Coverage</span>
              <span className="metric-value-huge">
                {coveragePct !== null ? `${coveragePct.toFixed(1)}%` : 'N/A'}
              </span>
              <span className="metric-subtext">
                {scan.coverage?.total_assessed_files ?? summary.assessed_files ?? 0} of{' '}
                {scan.coverage?.total_files_in_archive ?? summary.total_files ?? 0} files assessed
              </span>
            </div>
            {coveragePct !== null && (
              <ProgressRing value={coveragePct} size={54} strokeWidth={5} />
            )}
          </div>
        </Card>

        <Card>
          <div className="metric-card-content">
            <div className="metric-text-group">
              <span className="metric-label-dim">Integrity & State</span>
              <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--text-main)', marginTop: '4px' }}>
                {cleanStateLabel}
              </span>
              <span className="metric-subtext">NIST PQC Ruleset Aligned</span>
            </div>
            <div style={{ fontSize: '2rem', opacity: 0.8 }} aria-hidden="true">
              🛡️
            </div>
          </div>
        </Card>

        <Card>
          <div className="metric-card-content">
            <div className="metric-text-group">
              <span className="metric-label-dim">Migration Urgency</span>
              <div className="urgency-pills-row">
                <Badge variant={critCount > 0 ? 'critical' : 'neutral'}>
                  Crit: {critCount}
                </Badge>
                <Badge variant={highCount > 0 ? 'high' : 'neutral'}>
                  High: {highCount}
                </Badge>
                <Badge variant={medCount > 0 ? 'medium' : 'neutral'}>
                  Med: {medCount}
                </Badge>
                <Badge variant={lowCount > 0 ? 'low' : 'neutral'}>
                  Low: {lowCount}
                </Badge>
              </div>
              <span className="metric-subtext" style={{ marginTop: '4px' }}>
                Mosca migration queue
              </span>
            </div>
          </div>
        </Card>
      </section>

      {/* Surface Breakdown Section */}
      {Object.keys(surfaceBreakdown).length > 0 && (
        <section className="scan-surfaces-section" aria-label="Surface Coverage Breakdown">
          <h3 className="section-heading" style={{ fontSize: 'var(--font-size-md)' }}>
            Surface Assessment Breakdown
          </h3>
          <div className="surface-cards-grid">
            {Object.entries(surfaceBreakdown).map(([surfaceKey, surfaceData]) => (
              <div key={surfaceKey} className="surface-card">
                <div className="surface-name">
                  <span>{surfaceKey}</span>
                  <span style={{ fontFamily: 'var(--font-mono)' }}>
                    {surfaceData.coverage_percentage?.toFixed(0)}%
                  </span>
                </div>
                <div className="surface-stats">
                  <span>{surfaceData.assessed_files} / {surfaceData.total_files} files</span>
                  <span>{surfaceData.files_with_findings} with findings</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Cryptographic Findings Section */}
      <section className="scan-findings-section" aria-label="Discovered Findings">
        <div className="section-header-row">
          <h2 className="section-heading">Cryptographic Findings & Observations</h2>
          <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
            Select any row to inspect sanitized code evidence and detector provenance.
          </span>
        </div>

        <FindingsTable
          canonicalAssets={canonicalAssets}
          riskEvaluations={riskEvaluations}
          onSelectFinding={(finding) => setSelectedFinding(finding)}
        />
      </section>

      {/* Finding Detail Modal */}
      <FindingDetailModal
        finding={selectedFinding}
        open={Boolean(selectedFinding)}
        onClose={() => setSelectedFinding(null)}
      />
    </div>
  );
}
