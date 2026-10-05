import React, { useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { usePageTitle } from '../hooks/usePageTitle';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import EmptyState from '../components/common/EmptyState';
import {
  RiskSummary,
  RiskFactorBreakdown,
  RiskTable,
  RiskDetailModal,
  ContextEditor,
} from '../components/risk';
import {
  Sliders,
  RotateCcw,
  Play,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import './RiskPage.css';

/**
 * Dedicated Risk Assessment & Prioritization Page
 */
export default function RiskPage() {
  usePageTitle('Risk Assessment & Prioritization');
  const [searchParams, setSearchParams] = useSearchParams();
  const requestedScanId = searchParams.get('scanId');

  // 1. Fetch available scans list to allow picking a scan
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

  // Scenario Simulation State
  const [horizonYears, setHorizonYears] = useState(8.0);
  const [shelfLifeYears, setShelfLifeYears] = useState(5.0);
  const [migrationYears, setMigrationYears] = useState(2.0);
  const [appliedParams, setAppliedParams] = useState(null);
  const [showSimControls, setShowSimControls] = useState(false);
  const [selectedRiskItem, setSelectedRiskItem] = useState(null);

  // Construct Risk API URL
  const riskApiPath = activeScanId
    ? appliedParams
      ? `/api/v1/scans/${activeScanId}/risk?horizon=${appliedParams.horizon}&shelf_life=${appliedParams.shelfLife}&migration=${appliedParams.migration}`
      : `/api/v1/scans/${activeScanId}/risk`
    : null;

  const {
    data: riskData,
    loading: riskLoading,
    error: riskError,
    refetch: refetchRisk,
  } = useApi(riskApiPath, { enabled: Boolean(activeScanId) });

  // Handle Scenario Simulation Form Submit
  const handleSimulate = (e) => {
    e.preventDefault();
    setAppliedParams({
      horizon: Number(horizonYears),
      shelfLife: Number(shelfLifeYears),
      migration: Number(migrationYears),
    });
  };

  const handleResetSimulation = () => {
    setHorizonYears(8.0);
    setShelfLifeYears(5.0);
    setMigrationYears(2.0);
    setAppliedParams(null);
  };

  const handleScanChange = (newScanId) => {
    setSearchParams(newScanId ? { scanId: newScanId } : {});
    setAppliedParams(null);
  };

  if (scansLoading && !scansData) {
    return (
      <div className="risk-page" data-testid="risk-page-loading">
        <LoadingSpinner label="Loading cryptographic risk assessments..." />
      </div>
    );
  }

  if (scansError && !scansData) {
    return (
      <div className="risk-page" data-testid="risk-page-error">
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
      <div className="risk-page" data-testid="risk-page-empty">
        <EmptyState
          title="No Scans Available for Risk Assessment"
          message="Upload and analyze a software archive to generate cryptographic risk evaluations and migration prioritization."
          ctaLabel="Initiate New Scan"
          ctaTo="/scan"
        />
      </div>
    );
  }

  const riskEvaluations = Array.isArray(riskData?.risk_evaluations)
    ? riskData.risk_evaluations
    : [];
  const backlogItems = Array.isArray(riskData?.backlog_items)
    ? riskData.backlog_items
    : [];
  const scenario = riskData?.scenario || null;
  const context = riskData?.context || null;

  return (
    <div className="risk-page" data-testid="risk-page">
      {/* Top Header */}
      <header className="risk-page-header">
        <div className="risk-page-title-group">
          <div className="risk-page-meta-breadcrumbs">
            <Link to="/" style={{ color: 'var(--accent-primary)', textDecoration: 'none' }}>
              ← Dashboard
            </Link>
            <span>/</span>
            <span>Risk Prioritization</span>
          </div>

          <h1 className="risk-page-title">
            <span>Cryptographic Risk Assessment</span>
            <Badge variant="primary">NIST PQC 2026.10</Badge>
          </h1>
          <p className="risk-page-subtitle">
            Algorithm vulnerability scoring, Mosca migration timelines ($X + Y &gt; Z$), and candidate PQC alternatives.
          </p>
        </div>

        {/* Scan Selector & Simulation Trigger */}
        <div className="risk-header-actions">
          {scans.length > 0 && (
            <div className="scan-selector-box">
              <label htmlFor="scan-picker-select" className="scan-selector-label">
                Active Scan:
              </label>
              <select
                id="scan-picker-select"
                value={activeScanId || ''}
                onChange={(e) => handleScanChange(e.target.value)}
                className="scan-picker-select"
                aria-label="Select scan for risk assessment"
                data-testid="scan-picker-select"
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
            variant={showSimControls ? 'secondary' : 'outline'}
            size="sm"
            onClick={() => setShowSimControls((prev) => !prev)}
            data-testid="toggle-simulation-btn"
          >
            <Sliders size={15} aria-hidden="true" />
            <span>Simulate Mosca Horizon</span>
            {showSimControls ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </Button>
        </div>
      </header>

      {/* Interactive Mosca Scenario Simulation Drawer */}
      {showSimControls && (
        <Card className="simulation-controls-card" data-testid="simulation-controls-card">
          <div className="simulation-header">
            <div className="simulation-title-group">
              <Sliders size={18} className="sim-icon" aria-hidden="true" />
              <h3 className="sim-title">Dynamic Mosca Scenario Simulation</h3>
            </div>
            <span className="sim-disclaimer">
              Evaluates impact of varying threat horizons without altering underlying scan assets
            </span>
          </div>

          <form onSubmit={handleSimulate} className="sim-form">
            <div className="sim-inputs-grid">
              <div className="sim-input-group">
                <label htmlFor="horizon-input" className="sim-label">
                  Quantum Horizon (Z): <strong>{horizonYears} Years</strong>
                </label>
                <input
                  id="horizon-input"
                  type="range"
                  min="1"
                  max="20"
                  step="0.5"
                  value={horizonYears}
                  onChange={(e) => setHorizonYears(Number(e.target.value))}
                  className="sim-range-input"
                />
                <span className="sim-hint">Projected time to cryptanalytic quantum computer</span>
              </div>

              <div className="sim-input-group">
                <label htmlFor="shelflife-input" className="sim-label">
                  Data Shelf-Life (X): <strong>{shelfLifeYears} Years</strong>
                </label>
                <input
                  id="shelflife-input"
                  type="range"
                  min="1"
                  max="20"
                  step="0.5"
                  value={shelfLifeYears}
                  onChange={(e) => setShelfLifeYears(Number(e.target.value))}
                  className="sim-range-input"
                />
                <span className="sim-hint">Confidentiality retention obligation</span>
              </div>

              <div className="sim-input-group">
                <label htmlFor="migration-input" className="sim-label">
                  Migration Duration (Y): <strong>{migrationYears} Years</strong>
                </label>
                <input
                  id="migration-input"
                  type="range"
                  min="0.5"
                  max="10"
                  step="0.5"
                  value={migrationYears}
                  onChange={(e) => setMigrationYears(Number(e.target.value))}
                  className="sim-range-input"
                />
                <span className="sim-hint">Time needed to transition to PQC</span>
              </div>
            </div>

            <div className="sim-actions-row">
              <Button type="submit" variant="primary" size="sm" data-testid="apply-simulation-btn">
                <Play size={14} aria-hidden="true" />
                <span>Apply Scenario Simulation</span>
              </Button>
              {appliedParams && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={handleResetSimulation}
                  data-testid="reset-simulation-btn"
                >
                  <RotateCcw size={14} aria-hidden="true" />
                  <span>Reset to Scan Defaults</span>
                </Button>
              )}
            </div>
          </form>
        </Card>
      )}

      {/* Main Content Area */}
      {riskLoading ? (
        <div className="risk-loading-area" data-testid="risk-eval-loading">
          <LoadingSpinner label="Evaluating cryptographic risk & urgency metrics..." />
        </div>
      ) : riskError ? (
        <ErrorBanner
          title="Failed to Load Risk Assessment"
          message={riskError}
          onRetry={refetchRisk}
        />
      ) : (
        <div className="risk-content-stack">
          {/* Persistent Project Context Editor */}
          {activeScanId && (
            <ContextEditor
              scanId={activeScanId}
              context={context}
              onSaveSuccess={() => refetchRisk()}
            />
          )}

          {/* Summary Overview */}
          <RiskSummary
            riskEvaluations={riskEvaluations}
            scenario={scenario}
            context={context}
          />

          {/* 2-Column Grid: Factor Breakdown + Table */}
          <div className="risk-main-grid">
            <div className="risk-factors-column">
              <RiskFactorBreakdown
                riskEvaluations={riskEvaluations}
                title="Scan Multi-Factor Aggregate"
                subtitle="Mean factor contributions across all observed cryptographic assets"
              />
            </div>

            <div className="risk-table-column">
              <RiskTable
                riskEvaluations={riskEvaluations}
                backlogItems={backlogItems}
                onSelectRisk={(item) => setSelectedRiskItem(item)}
              />
            </div>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      <RiskDetailModal
        evaluation={selectedRiskItem}
        open={Boolean(selectedRiskItem)}
        onClose={() => setSelectedRiskItem(null)}
      />
    </div>
  );
}
