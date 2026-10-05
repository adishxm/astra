import React, { useState, useEffect } from 'react';
import Card from '../common/Card';
import Badge from '../common/Badge';
import Button from '../common/Button';
import ErrorBanner from '../common/ErrorBanner';
import LoadingSpinner from '../common/LoadingSpinner';
import { apiPut, getErrorMessage } from '../../api/client';
import { Save, CheckCircle2, ShieldAlert, Info } from 'lucide-react';
import './ContextEditor.css';

export const EXPOSURE_OPTIONS = [
  { value: 1, label: '1 - Build / Dev / Test Sandbox' },
  { value: 2, label: '2 - Localhost / Daemon Isolated' },
  { value: 3, label: '3 - Internal Shared Subnet / Mesh (Default)' },
  { value: 4, label: '4 - Partner Gateway / B2B' },
  { value: 5, label: '5 - Public Internet Facing' },
];

export const CRITICALITY_OPTIONS = [
  { value: 1, label: '1 - Scratchpad / Dev Test' },
  { value: 2, label: '2 - Low Impact / Non-sensitive' },
  { value: 3, label: '3 - Moderate / Standard (Default)' },
  { value: 4, label: '4 - High Impact / Billing / Identity' },
  { value: 5, label: '5 - Mission Critical / Core Banking / Telemetry' },
];

/**
 * Truthful Persistent Context Factors Editor Component.
 * Interacts directly with PUT /api/v1/scans/{scan_id}/context
 */
export default function ContextEditor({ scanId, context, scenario, onSaveSuccess }) {
  const isEnriched = Boolean(context?.is_user_enriched);
  const contextSource = context?.context_source || (isEnriched ? 'OWNER_SUPPLIED' : 'DEFAULT_ASSUMPTION');

  // Form State
  const [shelfLife, setShelfLife] = useState(
    context?.data_shelf_life_years !== undefined && context?.data_shelf_life_years !== null
      ? String(context.data_shelf_life_years)
      : '5.0'
  );
  const [migrationDuration, setMigrationDuration] = useState(
    context?.migration_duration_years !== undefined && context?.migration_duration_years !== null
      ? String(context.migration_duration_years)
      : '2.0'
  );
  const [exposure, setExposure] = useState(
    context?.exposure !== undefined && context?.exposure !== null
      ? String(context.exposure)
      : '3'
  );
  const [criticality, setCriticality] = useState(
    context?.criticality !== undefined && context?.criticality !== null
      ? String(context.criticality)
      : '3'
  );
  const [dependencyReach, setDependencyReach] = useState(
    context?.dependency_reach !== undefined && context?.dependency_reach !== null
      ? String(context.dependency_reach)
      : '1'
  );
  const [threatHorizon, setThreatHorizon] = useState(
    context?.quantum_threat_horizon_years !== undefined && context?.quantum_threat_horizon_years !== null
      ? String(context.quantum_threat_horizon_years)
      : scenario?.quantum_threat_horizon_years !== undefined && scenario?.quantum_threat_horizon_years !== null
      ? String(scenario.quantum_threat_horizon_years)
      : '8.0'
  );

  // Status & Messaging State
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  useEffect(() => {
    if (context) {
      setShelfLife(context.data_shelf_life_years !== undefined && context.data_shelf_life_years !== null ? String(context.data_shelf_life_years) : '5.0');
      setMigrationDuration(context.migration_duration_years !== undefined && context.migration_duration_years !== null ? String(context.migration_duration_years) : '2.0');
      setExposure(context.exposure !== undefined && context.exposure !== null ? String(context.exposure) : '3');
      setCriticality(context.criticality !== undefined && context.criticality !== null ? String(context.criticality) : '3');
      setDependencyReach(context.dependency_reach !== undefined && context.dependency_reach !== null ? String(context.dependency_reach) : '1');
      if (context.quantum_threat_horizon_years !== undefined && context.quantum_threat_horizon_years !== null) {
        setThreatHorizon(String(context.quantum_threat_horizon_years));
      }
    } else if (scenario?.quantum_threat_horizon_years !== undefined && scenario?.quantum_threat_horizon_years !== null) {
      setThreatHorizon(String(scenario.quantum_threat_horizon_years));
    }
  }, [context, scenario]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    // Client-side numerical validation
    const numShelf = parseFloat(shelfLife);
    const numMig = parseFloat(migrationDuration);
    const numExp = parseInt(exposure, 10);
    const numCrit = parseInt(criticality, 10);
    const numReach = parseInt(dependencyReach, 10);
    const numHorizon = parseFloat(threatHorizon);

    if (isNaN(numShelf) || numShelf < 0) {
      setErrorMsg('Data shelf life (X) must be a non-negative number of years.');
      return;
    }
    if (isNaN(numMig) || numMig < 0) {
      setErrorMsg('Migration duration (Y) must be a non-negative number of years.');
      return;
    }
    if (isNaN(numExp) || numExp < 1 || numExp > 5) {
      setErrorMsg('Operational exposure must be an integer between 1 and 5.');
      return;
    }
    if (isNaN(numCrit) || numCrit < 1 || numCrit > 5) {
      setErrorMsg('Business criticality must be an integer between 1 and 5.');
      return;
    }
    if (isNaN(numReach) || numReach < 1) {
      setErrorMsg('Dependency reach must be a positive integer (minimum 1).');
      return;
    }
    if (isNaN(numHorizon) || numHorizon < 1.0) {
      setErrorMsg('Quantum threat horizon (Z) must be at least 1.0 year.');
      return;
    }

    const payload = {
      data_shelf_life_years: numShelf,
      migration_duration_years: numMig,
      exposure: numExp,
      criticality: numCrit,
      dependency_reach: numReach,
      quantum_threat_horizon_years: numHorizon,
    };

    setSaving(true);
    try {
      const res = await apiPut(`/api/v1/scans/${scanId}/context`, payload);
      setSuccessMsg('Project context factors saved to server successfully.');
      if (onSaveSuccess && typeof onSaveSuccess === 'function') {
        onSaveSuccess(res);
      }
    } catch (err) {
      setErrorMsg(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card className="context-editor-card" data-testid="context-editor">
      <div className="context-editor-header">
        <div className="context-title-group">
          <h3 className="context-editor-title">Project Context & Owner Risk Factors</h3>
          <p className="context-editor-subtitle">
            Persistent owner-supplied factors governing risk score calculations for this project.
          </p>
        </div>
        <div className="context-badge-group">
          {isEnriched ? (
            <Badge variant="info" icon={<Info size={13} className="badge__icon" />} data-testid="context-status-badge">
              Owner-Provided Context
            </Badge>
          ) : (
            <Badge variant="warning" icon={<ShieldAlert size={13} className="badge__icon" />} data-testid="context-status-badge">
              Unverified / Default Assumption
            </Badge>
          )}
        </div>
      </div>

      <div className="context-distinction-banner" data-testid="context-distinction-banner">
        <Info className="info-icon" size={16} />
        <span>
          <strong>Provenance Note:</strong> Context source is labeled <em>{contextSource}</em>. Owner-supplied input reflects factor origin, not safety or risk validation. Local <strong>Mosca scenario sliders</strong> remain temporary sensitivity controls.
        </span>
      </div>

      {errorMsg && (
        <div style={{ marginBottom: 'var(--space-md)' }}>
          <ErrorBanner title="Context Update Rejected" message={errorMsg} onDismiss={() => setErrorMsg(null)} />
        </div>
      )}

      {successMsg && (
        <div className="context-success-banner" data-testid="context-success-banner">
          <CheckCircle2 size={16} />
          <span>{successMsg}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="context-editor-form" data-testid="context-editor-form">
        <div className="context-grid">
          {/* Data Shelf Life X */}
          <div className="form-group">
            <label htmlFor="shelf-life-input">
              Data Shelf Life (X, years)
            </label>
            <input
              id="shelf-life-input"
              type="number"
              step="0.5"
              min="0"
              value={shelfLife}
              onChange={(e) => setShelfLife(e.target.value)}
              className="context-input"
              data-testid="input-shelf-life"
              disabled={saving}
              required
            />
            <span className="input-hint">Required secrecy duration for protected data</span>
          </div>

          {/* Migration Duration Y */}
          <div className="form-group">
            <label htmlFor="migration-duration-input">
              PQC Migration Duration (Y, years)
            </label>
            <input
              id="migration-duration-input"
              type="number"
              step="0.5"
              min="0"
              value={migrationDuration}
              onChange={(e) => setMigrationDuration(e.target.value)}
              className="context-input"
              data-testid="input-migration-duration"
              disabled={saving}
              required
            />
            <span className="input-hint">Estimated engineering migration lead time</span>
          </div>

          {/* Quantum Threat Horizon Z */}
          <div className="form-group">
            <label htmlFor="threat-horizon-input">
              Quantum Threat Horizon (Z, years)
            </label>
            <input
              id="threat-horizon-input"
              type="number"
              step="0.5"
              min="1.0"
              value={threatHorizon}
              onChange={(e) => setThreatHorizon(e.target.value)}
              className="context-input"
              data-testid="input-threat-horizon"
              disabled={saving}
              required
            />
            <span className="input-hint">Persisted CRQC emergence horizon (min: 1.0)</span>
          </div>

          {/* Exposure Scope */}
          <div className="form-group">
            <label htmlFor="exposure-select">
              Operational Exposure Scope
            </label>
            <select
              id="exposure-select"
              value={exposure}
              onChange={(e) => setExposure(e.target.value)}
              className="context-select"
              data-testid="select-exposure"
              disabled={saving}
            >
              {EXPOSURE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <span className="input-hint">Network & architectural exposure</span>
          </div>

          {/* Criticality Level */}
          <div className="form-group">
            <label htmlFor="criticality-select">
              Business Criticality Level
            </label>
            <select
              id="criticality-select"
              value={criticality}
              onChange={(e) => setCriticality(e.target.value)}
              className="context-select"
              data-testid="select-criticality"
              disabled={saving}
            >
              {CRITICALITY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <span className="input-hint">Impact of cryptographic compromise</span>
          </div>

          {/* Dependency Reach */}
          <div className="form-group">
            <label htmlFor="reach-input">
              Dependency Reach / Blast Radius
            </label>
            <input
              id="reach-input"
              type="number"
              step="1"
              min="1"
              value={dependencyReach}
              onChange={(e) => setDependencyReach(e.target.value)}
              className="context-input"
              data-testid="input-dependency-reach"
              disabled={saving}
              required
            />
            <span className="input-hint">Count of dependent systems / callers</span>
          </div>
        </div>

        <div className="context-actions">
          <Button
            type="submit"
            variant="primary"
            disabled={saving}
            data-testid="save-context-btn"
          >
            {saving ? (
              <>
                <LoadingSpinner size="sm" inline /> Saving Context...
              </>
            ) : (
              <>
                <Save size={16} /> Save Persistent Context
              </>
            )}
          </Button>
        </div>
      </form>
    </Card>
  );
}
