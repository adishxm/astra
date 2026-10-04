import React from 'react';
import Card from '../common/Card';
import Badge from '../common/Badge';
import {
  AlertOctagon,
  AlertTriangle,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  Clock,
  ShieldAlert,
  Info,
} from 'lucide-react';
import './RiskSummary.css';

/**
 * Normalizes urgency strings to a safe Badge variant.
 * Strictly adheres to truthfulness: unassessed/unknown is NEVER rendered as low or safe.
 * @param {string|null|undefined} urgency
 * @returns {'critical'|'high'|'medium'|'low'|'unknown'}
 */
export function getUrgencyBadgeVariant(urgency) {
  if (!urgency) return 'unknown';
  const u = String(urgency).toUpperCase();
  switch (u) {
    case 'CRITICAL':
      return 'critical';
    case 'HIGH':
      return 'high';
    case 'MEDIUM':
      return 'medium';
    case 'LOW':
      return 'low';
    case 'UNASSESSED':
    default:
      return 'unknown';
  }
}

/**
 * Risk Assessment Summary Header & Cards Component
 * @param {Object} props
 * @param {Array} [props.riskEvaluations=[]]
 * @param {Object} [props.scenario]
 * @param {Object} [props.context]
 * @param {Object} [props.summary]
 * @param {string} [props.className='']
 */
export default function RiskSummary({
  riskEvaluations = [],
  scenario = null,
  context = null,
  summary = null,
  className = '',
}) {
  const evaluations = Array.isArray(riskEvaluations) ? riskEvaluations : [];
  const totalEvaluations = evaluations.length;

  // Urgency Counts directly from backend risk_evaluations
  let critCount = 0;
  let highCount = 0;
  let medCount = 0;
  let lowCount = 0;
  let unassessedCount = 0;

  // Mosca condition tracking
  let moscaViolatedCount = 0;
  let sampleAssumptions = scenario || null;

  evaluations.forEach((item) => {
    if (!item || typeof item !== 'object') {
      unassessedCount += 1;
      return;
    }

    if (item.assumptions_applied && !sampleAssumptions) {
      sampleAssumptions = item.assumptions_applied;
    }

    if (item.mosca_condition_violated === true) {
      moscaViolatedCount += 1;
    }

    const urgency = item.urgency ? String(item.urgency).toUpperCase() : null;
    const hasValidScore = typeof item.risk_score === 'number' && !Number.isNaN(item.risk_score);

    if (!urgency || urgency === 'UNASSESSED' || !hasValidScore) {
      unassessedCount += 1;
    } else if (urgency === 'CRITICAL') {
      critCount += 1;
    } else if (urgency === 'HIGH') {
      highCount += 1;
    } else if (urgency === 'MEDIUM') {
      medCount += 1;
    } else if (urgency === 'LOW') {
      lowCount += 1;
    } else {
      unassessedCount += 1;
    }
  });

  // Fallback to summary object counts if evaluations array was empty but summary exists
  if (totalEvaluations === 0 && summary) {
    critCount = summary.critical_urgency_count ?? 0;
    highCount = summary.high_urgency_count ?? 0;
    medCount = summary.medium_urgency_count ?? 0;
    lowCount = summary.low_urgency_count ?? 0;
    unassessedCount = summary.unassessed_urgency_count ?? 0;
  }

  // Extract Mosca scenario parameters
  const horizonYears =
    sampleAssumptions?.quantum_threat_horizon_years ??
    scenario?.quantum_threat_horizon_years ??
    8.0;
  const shelfLifeYears =
    sampleAssumptions?.data_shelf_life_years ??
    context?.data_shelf_life_years ??
    5.0;
  const migrationYears =
    sampleAssumptions?.migration_duration_years ??
    context?.migration_duration_years ??
    2.0;
  const scenarioCaveat =
    sampleAssumptions?.scenario_caveat ??
    scenario?.horizon_rationale ??
    'Mosca urgency reflects scenario simulation assumptions (X + Y > Z) and baseline defaults until enriched by asset owner.';
  const rulesetVersion =
    sampleAssumptions?.ruleset_version ?? '2026.10-nist-pqc';

  const sumXY = shelfLifeYears + migrationYears;
  const isViolatedOverall = moscaViolatedCount > 0 || sumXY > horizonYears;
  const slackYears = horizonYears - sumXY;

  return (
    <div className={`risk-summary-wrapper ${className}`} data-testid="risk-summary">
      {/* Urgency Metrics Grid */}
      <div className="risk-metrics-grid" role="region" aria-label="Risk Urgency Breakdown">
        {/* Total Assessed Items */}
        <Card className="risk-metric-card">
          <div className="risk-metric-inner">
            <div className="risk-metric-text">
              <span className="risk-metric-label">Assessed Cryptography</span>
              <span className="risk-metric-number" data-testid="total-risk-items">
                {totalEvaluations}
              </span>
              <span className="risk-metric-subtext">Evaluated assets</span>
            </div>
            <div className="risk-metric-icon-box" aria-hidden="true">
              <ShieldAlert size={28} className="risk-icon-primary" />
            </div>
          </div>
        </Card>

        {/* Critical Urgency */}
        <Card className="risk-metric-card risk-metric-card--critical">
          <div className="risk-metric-inner">
            <div className="risk-metric-text">
              <span className="risk-metric-label">Critical Urgency</span>
              <span className="risk-metric-number risk-color-critical" data-testid="crit-count">
                {critCount}
              </span>
              <span className="risk-metric-subtext">Immediate action</span>
            </div>
            <div className="risk-metric-icon-box" aria-hidden="true">
              <AlertOctagon size={28} className="risk-color-critical" />
            </div>
          </div>
        </Card>

        {/* High Urgency */}
        <Card className="risk-metric-card risk-metric-card--high">
          <div className="risk-metric-inner">
            <div className="risk-metric-text">
              <span className="risk-metric-label">High Urgency</span>
              <span className="risk-metric-number risk-color-high" data-testid="high-count">
                {highCount}
              </span>
              <span className="risk-metric-subtext">Priority backlog</span>
            </div>
            <div className="risk-metric-icon-box" aria-hidden="true">
              <AlertTriangle size={28} className="risk-color-high" />
            </div>
          </div>
        </Card>

        {/* Medium Urgency */}
        <Card className="risk-metric-card risk-metric-card--medium">
          <div className="risk-metric-inner">
            <div className="risk-metric-text">
              <span className="risk-metric-label">Medium Urgency</span>
              <span className="risk-metric-number risk-color-medium" data-testid="med-count">
                {medCount}
              </span>
              <span className="risk-metric-subtext">Planned migration</span>
            </div>
            <div className="risk-metric-icon-box" aria-hidden="true">
              <AlertCircle size={28} className="risk-color-medium" />
            </div>
          </div>
        </Card>

        {/* Low Urgency */}
        <Card className="risk-metric-card risk-metric-card--low">
          <div className="risk-metric-inner">
            <div className="risk-metric-text">
              <span className="risk-metric-label">Low Urgency</span>
              <span className="risk-metric-number risk-color-low" data-testid="low-count">
                {lowCount}
              </span>
              <span className="risk-metric-subtext">Standard review</span>
            </div>
            <div className="risk-metric-icon-box" aria-hidden="true">
              <CheckCircle2 size={28} className="risk-color-low" />
            </div>
          </div>
        </Card>

        {/* Unassessed / Unknown (Truthfulness Guarantee) */}
        {unassessedCount > 0 && (
          <Card className="risk-metric-card risk-metric-card--unassessed">
            <div className="risk-metric-inner">
              <div className="risk-metric-text">
                <span className="risk-metric-label">Unassessed</span>
                <span className="risk-metric-number risk-color-unassessed" data-testid="unassessed-count">
                  {unassessedCount}
                </span>
                <span className="risk-metric-subtext">Missing score</span>
              </div>
              <div className="risk-metric-icon-box" aria-hidden="true">
                <HelpCircle size={28} className="risk-color-unassessed" />
              </div>
            </div>
          </Card>
        )}
      </div>

      {/* Mosca Theorem & Scenario Simulation Banner */}
      <div
        className={`mosca-banner ${isViolatedOverall ? 'mosca-banner--violation' : 'mosca-banner--compliant'}`}
        role="region"
        aria-label="Mosca Theorem Evaluation Status"
      >
        <div className="mosca-banner-header">
          <div className="mosca-banner-title-group">
            <Clock size={20} className="mosca-banner-icon" aria-hidden="true" />
            <h3 className="mosca-banner-title">
              Mosca Migration Timeline Analysis (X + Y vs Z)
            </h3>
            <Badge variant={isViolatedOverall ? 'critical' : 'low'}>
              {isViolatedOverall ? 'MOSCA VIOLATION: SNDL RISK' : 'MOSCA COMPLIANT'}
            </Badge>
          </div>

          <div className="mosca-slack-pill">
            <span className="mosca-slack-label">Calculated Slack:</span>
            <span
              className={`mosca-slack-value ${
                slackYears < 0 ? 'mosca-slack-negative' : 'mosca-slack-positive'
              }`}
            >
              {slackYears > 0 ? `+${slackYears.toFixed(1)} yrs` : `${slackYears.toFixed(1)} yrs`}
            </span>
          </div>
        </div>

        <div className="mosca-parameters-row">
          <div className="mosca-param-col">
            <span className="param-label">Data Shelf-Life (X):</span>
            <span className="param-value">{shelfLifeYears.toFixed(1)} Years</span>
          </div>
          <span className="param-operator">+</span>
          <div className="mosca-param-col">
            <span className="param-label">Migration Duration (Y):</span>
            <span className="param-value">{migrationYears.toFixed(1)} Years</span>
          </div>
          <span className="param-operator">=</span>
          <div className="mosca-param-col">
            <span className="param-label">Total Required (X + Y):</span>
            <span className={`param-value ${isViolatedOverall ? 'param-value--danger' : ''}`}>
              {sumXY.toFixed(1)} Years
            </span>
          </div>
          <span className="param-operator">vs</span>
          <div className="mosca-param-col">
            <span className="param-label">Quantum Threat Horizon (Z):</span>
            <span className="param-value">{horizonYears.toFixed(1)} Years</span>
          </div>
        </div>

        {isViolatedOverall && (
          <div className="mosca-warning-text" data-testid="mosca-violation-warning">
            <strong>Store Now, Decrypt Later (SNDL) Vulnerability Detected:</strong>{' '}
            Data security lifespan ({shelfLifeYears} yrs) plus migration lead time ({migrationYears} yrs) exceeds
            the projected CRQC quantum threat horizon ({horizonYears} yrs). Encrypted communications captured today may
            be decrypted retrospectively before deprecation is complete.
          </div>
        )}

        <div className="mosca-assumptions-footer">
          <div className="caveat-text">
            <Info size={14} aria-hidden="true" style={{ flexShrink: 0, marginTop: 2 }} />
            <span>{scenarioCaveat}</span>
          </div>
          <span className="ruleset-tag">Ruleset: {rulesetVersion}</span>
        </div>
      </div>
    </div>
  );
}
