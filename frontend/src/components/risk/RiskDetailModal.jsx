import React from 'react';
import Modal from '../common/Modal';
import Badge from '../common/Badge';
import Button from '../common/Button';
import RiskFactorBreakdown from './RiskFactorBreakdown';
import { formatRiskScore, formatReasonCode } from './RiskTable';
import {
  Clock,
  Layers,
  AlertTriangle,
  FileCode,
  Tag,
  Info,
  CheckCircle2,
} from 'lucide-react';
import './RiskDetailModal.css';

/**
 * Risk Assessment Detail Modal
 * Detailed inspection of an individual cryptographic asset's risk evaluation.
 *
 * @param {Object} props
 * @param {Object|null} props.evaluation
 * @param {boolean} props.open
 * @param {() => void} props.onClose
 */
export default function RiskDetailModal({
  evaluation = null,
  open = false,
  onClose,
}) {
  if (!evaluation) return null;

  const {
    asset_id,
    algorithm = 'Unknown Algorithm',
    purpose = 'UNSPECIFIED',
    risk_score,
    urgency,
    mosca_condition_violated = false,
    mosca_slack_years,
    factor_contributions,
    reason_codes = [],
    assumptions_applied = {},
    evaluated_at,
    backlogItem = null,
  } = evaluation;

  const hasScore = typeof risk_score === 'number' && !Number.isNaN(risk_score);
  const urgencyUpper = urgency ? String(urgency).toUpperCase() : 'UNASSESSED';
  const isUnassessed = urgencyUpper === 'UNASSESSED' || !hasScore;

  // Scenario parameters
  const horizonZ = assumptions_applied?.quantum_threat_horizon_years;
  const shelfLifeX = assumptions_applied?.data_shelf_life_years;
  const migrationY = assumptions_applied?.migration_duration_years;
  const contextSource = assumptions_applied?.context_source || 'DEFAULT_ASSUMPTION';
  const rulesetVersion = assumptions_applied?.ruleset_version || '2026.10-nist-pqc';
  const scenarioCaveat = assumptions_applied?.scenario_caveat;
  const scenarioId = assumptions_applied?.scenario_id || 'standard-2034-horizon';

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Risk Assessment: ${algorithm}`}
      size="lg"
      className="risk-detail-modal"
    >
      <div className="risk-modal-body" data-testid="risk-detail-modal-body">
        {/* Header Summary Banner */}
        <div className="risk-modal-header-banner">
          <div className="risk-header-meta">
            <div className="asset-meta-title-row">
              <h3 className="modal-algo-name">{algorithm}</h3>
              <Badge
                variant={
                  isUnassessed
                    ? 'unknown'
                    : urgencyUpper === 'CRITICAL'
                    ? 'critical'
                    : urgencyUpper === 'HIGH'
                    ? 'high'
                    : urgencyUpper === 'MEDIUM'
                    ? 'medium'
                    : 'low'
                }
              >
                {isUnassessed ? 'Unassessed' : urgencyUpper}
              </Badge>
              {mosca_condition_violated && (
                <Badge variant="critical">SNDL VIOLATION</Badge>
              )}
            </div>

            <div className="asset-id-display">
              <FileCode size={14} className="meta-icon" aria-hidden="true" />
              <span>Asset ID:</span>
              <code className="asset-id-full">{asset_id || 'unidentified-asset'}</code>
            </div>

            <div className="asset-details-inline">
              <span>Purpose: <strong>{purpose}</strong></span>
              {evaluated_at && (
                <>
                  <span>•</span>
                  <span>Evaluated: {new Date(evaluated_at).toLocaleString()}</span>
                </>
              )}
            </div>
          </div>

          {/* Risk Score Pill Card */}
          <div className="modal-score-box">
            <span className="modal-score-label">Composite Risk</span>
            <div className="modal-score-value-row">
              <span
                className={`modal-score-huge ${
                  !hasScore
                    ? 'score--unassessed'
                    : risk_score >= 70
                    ? 'score--critical'
                    : risk_score >= 40
                    ? 'score--high'
                    : 'score--low'
                }`}
              >
                {formatRiskScore(risk_score)}
              </span>
              {hasScore && <span className="modal-score-scale">/ 100</span>}
            </div>
            <span className="modal-score-subtext">
              {isUnassessed ? 'Score unavailable' : 'NIST PQC weighted'}
            </span>
          </div>
        </div>

        {/* Mosca Theorem Evaluation Breakdown */}
        <section className="modal-section" aria-label="Mosca Theorem Timeline Details">
          <div className="section-title-group">
            <Clock size={16} className="section-title-icon" aria-hidden="true" />
            <h4 className="section-title">Mosca Migration Timeline Analysis</h4>
          </div>

          <div
            className={`modal-mosca-box ${
              mosca_condition_violated ? 'modal-mosca-box--violation' : 'modal-mosca-box--compliant'
            }`}
          >
            <div className="mosca-calc-row">
              <div className="mosca-calc-item">
                <span className="calc-label">Data Shelf-Life (X)</span>
                <span className="calc-val">
                  {typeof shelfLifeX === 'number' ? `${shelfLifeX.toFixed(1)} yrs` : 'Unspecified'}
                </span>
              </div>
              <span className="calc-sym">+</span>
              <div className="mosca-calc-item">
                <span className="calc-label">Migration Time (Y)</span>
                <span className="calc-val">
                  {typeof migrationY === 'number' ? `${migrationY.toFixed(1)} yrs` : 'Unspecified'}
                </span>
              </div>
              <span className="calc-sym">vs</span>
              <div className="mosca-calc-item">
                <span className="calc-label">Threat Horizon (Z)</span>
                <span className="calc-val">
                  {typeof horizonZ === 'number' ? `${horizonZ.toFixed(1)} yrs` : 'Unspecified'}
                </span>
              </div>
              <span className="calc-sym">=</span>
              <div className="mosca-calc-item">
                <span className="calc-label">Calculated Slack</span>
                <span
                  className={`calc-val ${
                    typeof mosca_slack_years === 'number' && mosca_slack_years < 0
                      ? 'calc-val--negative'
                      : 'calc-val--positive'
                  }`}
                >
                  {typeof mosca_slack_years === 'number'
                    ? mosca_slack_years > 0
                      ? `+${mosca_slack_years.toFixed(1)} yrs`
                      : `${mosca_slack_years.toFixed(1)} yrs`
                    : 'Unassessed'}
                </span>
              </div>
            </div>

            {mosca_condition_violated && (
              <div className="modal-mosca-alert">
                <AlertTriangle size={16} aria-hidden="true" />
                <span>
                  <strong>Store Now, Decrypt Later (SNDL) Critical Warning:</strong> Data retention
                  exceeds migration buffer before quantum cryptanalysis is projected to break this primitive.
                </span>
              </div>
            )}
          </div>
        </section>

        {/* 4-Factor Breakdown Component */}
        <section className="modal-section" aria-label="Risk Factors">
          <RiskFactorBreakdown
            factors={factor_contributions}
            title="Component Factor Contributions"
            subtitle="Normalized percentage contribution to composite risk score"
          />
        </section>

        {/* Applied Assumptions & Scenario Context */}
        <section className="modal-section" aria-label="Applied Scenario Assumptions">
          <div className="section-title-group">
            <Layers size={16} className="section-title-icon" aria-hidden="true" />
            <h4 className="section-title">Applied Scenario & Context Assumptions</h4>
          </div>

          <div className="modal-assumptions-grid">
            <div className="assumption-item">
              <span className="assumption-label">Scenario ID</span>
              <code className="assumption-val">{scenarioId}</code>
            </div>
            <div className="assumption-item">
              <span className="assumption-label">Context Source</span>
              <span className="assumption-val">{contextSource}</span>
            </div>
            <div className="assumption-item">
              <span className="assumption-label">Ruleset Version</span>
              <span className="assumption-val">{rulesetVersion}</span>
            </div>
            <div className="assumption-item">
              <span className="assumption-label">Evaluated Horizon</span>
              <span className="assumption-val">
                {typeof horizonZ === 'number' ? `${horizonZ} Years` : 'Standard'}
              </span>
            </div>
          </div>

          {scenarioCaveat && (
            <div className="modal-caveat-box">
              <Info size={14} aria-hidden="true" style={{ flexShrink: 0, marginTop: 2 }} />
              <span className="modal-caveat-text">{scenarioCaveat}</span>
            </div>
          )}
        </section>

        {/* Reason Codes */}
        {Array.isArray(reason_codes) && reason_codes.length > 0 && (
          <section className="modal-section" aria-label="Reason Codes">
            <div className="section-title-group">
              <Tag size={16} className="section-title-icon" aria-hidden="true" />
              <h4 className="section-title">Assigned Reason Codes</h4>
            </div>

            <div className="modal-reasons-list">
              {reason_codes.map((code) => (
                <div key={code} className="reason-code-item" data-testid={`reason-code-${code}`}>
                  <code className="reason-code-name">{code}</code>
                  <span className="reason-code-desc">{formatReasonCode(code)}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Associated Migration Recommendation */}
        {backlogItem && (
          <section className="modal-section" aria-label="Migration Recommendation Candidate">
            <div className="section-title-group">
              <CheckCircle2 size={16} className="section-title-icon" aria-hidden="true" />
              <h4 className="section-title">Candidate Migration Option</h4>
            </div>

            <div className="backlog-card">
              <div className="backlog-header">
                <div>
                  <span className="backlog-label">Target PQC Replacement:</span>
                  <div className="backlog-algo-target">
                    {backlogItem.target_pqc_algorithm || 'Cryptographic Review Required'}
                  </div>
                </div>
                <Badge variant={backlogItem.priority === 'CRITICAL' ? 'critical' : 'medium'}>
                  Priority: {backlogItem.priority || 'NORMAL'}
                </Badge>
              </div>

              {backlogItem.dated_standard_ref && (
                <div className="backlog-meta-row">
                  <span className="meta-label">Standard Reference:</span>
                  <span className="meta-val">{backlogItem.dated_standard_ref}</span>
                </div>
              )}

              {backlogItem.recommended_action && (
                <div className="backlog-meta-row">
                  <span className="meta-label">Action:</span>
                  <span className="meta-val">{backlogItem.recommended_action}</span>
                </div>
              )}

              {Array.isArray(backlogItem.compatibility_gaps) && backlogItem.compatibility_gaps.length > 0 && (
                <div className="backlog-gaps-group">
                  <span className="meta-label">Compatibility & Migration Gaps:</span>
                  <ul className="backlog-gaps-list">
                    {backlogItem.compatibility_gaps.map((gap, idx) => (
                      <li key={idx}>{gap}</li>
                    ))}
                  </ul>
                </div>
              )}

              {backlogItem.operational_benchmarking_caveat && (
                <div className="backlog-caveat">
                  <Info size={13} aria-hidden="true" style={{ flexShrink: 0, marginTop: 1 }} />
                  <span>{backlogItem.operational_benchmarking_caveat}</span>
                </div>
              )}
            </div>
          </section>
        )}
      </div>

      <div className="risk-modal-footer">
        <Button variant="outline" onClick={onClose} aria-label="Close risk detail dialog">
          Close
        </Button>
      </div>
    </Modal>
  );
}
