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
import TabBar, { TabPanel } from '../components/common/TabBar';
import { FindingsTable, FindingDetailModal } from '../components/findings';
import {
  CoverageOverview,
  SurfaceBreakdown,
  CoverageGapsTable,
  CollectorHealth,
} from '../components/coverage';
import {
  RiskSummary,
  RiskFactorBreakdown,
  RiskTable,
  RiskDetailModal,
} from '../components/risk';
import {
  CbomSummary,
  CbomInventoryTable,
  CbomAlgorithmMatrix,
  CbomDetailModal,
  CbomExportModal,
  normalizeCbomInventory,
} from '../components/cbom';
import './ScanDetailPage.css';

/**
 * Scan Results, Coverage & Findings Detail Page.
 */
export default function ScanDetailPage() {
  const { scanId } = useParams();
  usePageTitle(`Scan ${scanId || 'Details'}`);

  const { data: scan, loading, error, refetch } = useApi(scanId ? `/api/v1/scans/${scanId}` : null);
  const [activeTab, setActiveTab] = useState('findings');
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [selectedRiskItem, setSelectedRiskItem] = useState(null);
  const [selectedCbomItem, setSelectedCbomItem] = useState(null);
  const [isExportOpen, setIsExportOpen] = useState(false);

  if (loading) {
    return (
      <div className="scan-detail-page" data-testid="scan-detail-loading">
        <LoadingSpinner label="Loading scan results, coverage, and findings..." />
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
  const assetCount = typeof scan.asset_count === 'number' ? scan.asset_count : (scan.canonical_assets?.length ?? 0);
  const coveragePct = scan.coverage?.overall_coverage_percentage ?? scan.summary?.coverage_percentage ?? scan.coverage_percentage ?? null;
  const cleanStateLabel = scan.clean_state_label || scan.coverage?.scan_status_label || scan.summary?.clean_state_label || 'UNASSESSED';
  const dnaHash = scan.cryptographic_dna_hash || scan.dna_hash || null;
  const canonicalAssets = scan.canonical_assets || [];
  const riskEvaluations = scan.risk_evaluations || [];
  const backlogItems = scan.backlog_items || [];
  const summary = scan.summary || {};
  const coverage = scan.coverage || {};
  const manifest = scan.manifest || {};
  const surfaceBreakdown = coverage.surface_breakdown || {};
  const unsupportedExtensions = coverage.unsupported_extensions || [];
  const manifestFiles = manifest.files || [];
  const collectorHealth = coverage.collector_health || {};
  const scenario = scan.scenario || null;
  const context = scan.context || null;

  // Normalize CBOM items
  const cbomComponents = normalizeCbomInventory(canonicalAssets, scan.observations || []);

  // Urgency counts
  const critCount = summary.critical_urgency_count ?? 0;
  const highCount = summary.high_urgency_count ?? 0;
  const medCount = summary.medium_urgency_count ?? 0;
  const lowCount = summary.low_urgency_count ?? 0;

  // Gaps count
  const gapCount = manifestFiles.filter((f) => !f.is_supported || f.skip_reason).length;

  const tabs = [
    { id: 'findings', label: 'Findings & Primitives', badge: String(assetCount) },
    { id: 'cbom', label: 'CBOM', badge: cbomComponents.length > 0 ? String(cbomComponents.length) : undefined },
    { id: 'risk', label: 'Risk Assessment', badge: riskEvaluations.length > 0 ? String(riskEvaluations.length) : undefined },
    { id: 'coverage', label: 'Coverage & Accounting' },
    { id: 'surfaces', label: 'Discovery Surfaces' },
    { id: 'gaps', label: 'Coverage Gaps', badge: gapCount > 0 ? String(gapCount) : undefined },
    { id: 'health', label: 'Engine Health' },
  ];

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
            <span>Scan Results & Coverage</span>
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
            Refresh Analysis
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
                {coverage.total_assessed_files ?? summary.assessed_files ?? 0} of{' '}
                {coverage.total_files_in_archive ?? summary.total_files ?? 0} files assessed
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

      {/* Analysis Navigation Tabs */}
      <section aria-label="Scan Analysis Sections" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
        <TabBar
          tabs={tabs}
          value={activeTab}
          onChange={setActiveTab}
          ariaLabel="Scan detail view tabs"
        />

        {/* Tab 1: Findings Table */}
        <TabPanel id="findings" active={activeTab === 'findings'}>
          <div className="scan-findings-section">
            <div className="section-header-row">
              <h2 className="section-heading">Cryptographic Findings & Observations</h2>
              <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                Inspect detected primitives, source locations, confidence levels, and sanitized evidence.
              </span>
            </div>

            <FindingsTable
              canonicalAssets={canonicalAssets}
              riskEvaluations={riskEvaluations}
              onSelectFinding={(finding) => setSelectedFinding(finding)}
            />
          </div>
        </TabPanel>

        {/* Tab 2: CBOM (Cryptographic Bill of Materials) */}
        <TabPanel id="cbom" active={activeTab === 'cbom'}>
          <div className="scan-cbom-section" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            <CbomSummary
              components={cbomComponents}
              scan={scan}
              onExportClick={() => setIsExportOpen(true)}
            />

            <CbomAlgorithmMatrix
              components={cbomComponents}
            />

            <div style={{ marginTop: 'var(--space-md)' }}>
              <div className="section-header-row" style={{ marginBottom: 'var(--space-sm)' }}>
                <h3 className="section-heading">CycloneDX 1.6 Cryptographic Components</h3>
              </div>
              <CbomInventoryTable
                components={cbomComponents}
                onSelectComponent={(item) => setSelectedCbomItem(item)}
              />
            </div>
          </div>
        </TabPanel>

        {/* Tab 3: Risk Assessment */}
        <TabPanel id="risk" active={activeTab === 'risk'}>
          <div className="scan-risk-section" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            <RiskSummary
              riskEvaluations={riskEvaluations}
              scenario={scenario}
              context={context}
              summary={summary}
            />

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-lg)' }}>
              <RiskFactorBreakdown
                riskEvaluations={riskEvaluations}
                title="Scan Multi-Factor Risk Breakdown"
                subtitle="Composite weights across assessed algorithms"
              />

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                <Card style={{ padding: 'var(--space-lg)', background: 'var(--bg-card)' }}>
                  <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 600, marginBottom: 'var(--space-xs)' }}>
                    Dedicated Risk Prioritization
                  </h3>
                  <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginBottom: 'var(--space-md)', lineHeight: 1.5 }}>
                    Adjust quantum threat horizons, shelf-life assumptions, and simulate SNDL migration timelines on the full Risk Analysis view.
                  </p>
                  <Link to={`/risk?scanId=${scanId}`}>
                    <Button variant="outline" size="sm">
                      Open in Risk Prioritization Center →
                    </Button>
                  </Link>
                </Card>
              </div>
            </div>

            <div style={{ marginTop: 'var(--space-md)' }}>
              <div className="section-header-row" style={{ marginBottom: 'var(--space-sm)' }}>
                <h3 className="section-heading">Evaluated Primitive Risk Records</h3>
              </div>
              <RiskTable
                riskEvaluations={riskEvaluations}
                backlogItems={backlogItems}
                onSelectRisk={(item) => setSelectedRiskItem(item)}
              />
            </div>
          </div>
        </TabPanel>

        {/* Tab 4: Coverage & Accounting */}
        <TabPanel id="coverage" active={activeTab === 'coverage'}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            <CoverageOverview coverage={coverage} summary={summary} />
            <SurfaceBreakdown
              surfaceBreakdown={surfaceBreakdown}
              onSelectSurface={() => setActiveTab('findings')}
            />
          </div>
        </TabPanel>

        {/* Tab 5: Discovery Surfaces */}
        <TabPanel id="surfaces" active={activeTab === 'surfaces'}>
          <SurfaceBreakdown
            surfaceBreakdown={surfaceBreakdown}
            onSelectSurface={() => setActiveTab('findings')}
          />
        </TabPanel>

        {/* Tab 6: Coverage Gaps & Unsupported Files */}
        <TabPanel id="gaps" active={activeTab === 'gaps'}>
          <CoverageGapsTable
            manifestFiles={manifestFiles}
            unsupportedExtensions={unsupportedExtensions}
          />
        </TabPanel>

        {/* Tab 7: Collector Engine Diagnostic */}
        <TabPanel id="health" active={activeTab === 'health'}>
          <CollectorHealth
            health={collectorHealth}
            evaluatedAt={coverage.evaluated_at}
          />
        </TabPanel>
      </section>

      {/* Finding Detail Modal */}
      <FindingDetailModal
        finding={selectedFinding}
        open={Boolean(selectedFinding)}
        onClose={() => setSelectedFinding(null)}
      />

      {/* Risk Detail Modal */}
      <RiskDetailModal
        evaluation={selectedRiskItem}
        open={Boolean(selectedRiskItem)}
        onClose={() => setSelectedRiskItem(null)}
      />

      {/* CBOM Detail Modal */}
      <CbomDetailModal
        component={selectedCbomItem}
        open={Boolean(selectedCbomItem)}
        onClose={() => setSelectedCbomItem(null)}
      />

      {/* CycloneDX 1.6 Export Modal */}
      <CbomExportModal
        open={isExportOpen}
        onClose={() => setIsExportOpen(false)}
        scanId={scanId}
        archiveName={targetName}
      />
    </div>
  );
}

