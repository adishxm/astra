import React from 'react';
import { Link } from 'react-router-dom';
import Modal from '../common/Modal';
import Badge from '../common/Badge';
import Button from '../common/Button';
import {
  ArrowRight,
  BookOpen,
  AlertTriangle,
  FileCode,
  ShieldCheck,
  Package,
  Layers,
  Sparkles,
  ExternalLink,
  Flame,
} from 'lucide-react';
import './MigrationDetailModal.css';

/**
 * Migration Recommendation Detail Modal
 *
 * @param {Object} props
 * @param {Object|null} props.task
 * @param {boolean} props.open
 * @param {() => void} props.onClose
 * @param {string} [props.scanId]
 */
export default function MigrationDetailModal({
  task = null,
  open = false,
  onClose,
  scanId = '',
}) {
  if (!task) return null;

  const {
    task_id,
    asset_id,
    relative_path,
    start_line,
    current_algorithm = 'Unknown Algorithm',
    purpose = 'CRYPTOGRAPHY',
    priority = 'UNASSESSED',
    composite_risk_score,
    target_pqc_algorithm = 'Advisory Review with Cryptographer',
    target_hybrid_algorithm,
    dated_standard_ref = 'Standard Authority Reference',
    compatibility_gaps = [],
    recommended_action = 'Review cryptographic architecture with security team.',
    review_owner = 'Security Architecture & Crypto Team',
    status = 'OPEN',
    operational_benchmarking_caveat,
    reason_codes = [],
  } = task;

  const prioUpper = String(priority).toUpperCase();
  const prioVariant =
    prioUpper === 'CRITICAL'
      ? 'critical'
      : prioUpper === 'HIGH'
      ? 'high'
      : prioUpper === 'MEDIUM'
      ? 'medium'
      : prioUpper === 'LOW'
      ? 'low'
      : 'neutral';

  const statusStr = String(status).toUpperCase();
  const statusVariant =
    statusStr === 'ACCEPTED' || statusStr === 'COMPLETED'
      ? 'safe'
      : statusStr === 'IN_REVIEW'
      ? 'medium'
      : 'primary';

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Migration Pathway: ${current_algorithm}`}
      size="lg"
      className="migration-detail-modal"
    >
      <div className="migration-modal-body" data-testid="migration-detail-modal-body">
        {/* Header Transition Banner */}
        <div className="mig-modal-header-banner">
          <div className="mig-header-transition-flow">
            <div className="mig-flow-box mig-flow-box--observed">
              <span className="flow-box-label">Observed Algorithm</span>
              <span className="flow-box-title">{current_algorithm}</span>
              <span className="flow-box-sub">{purpose}</span>
            </div>

            <div className="mig-flow-arrow-box">
              <ArrowRight size={22} className="flow-arrow" aria-hidden="true" />
              <span className="flow-arrow-label">PQC Migration</span>
            </div>

            <div className="mig-flow-box mig-flow-box--target">
              <span className="flow-box-label">Recommended Target</span>
              <span className="flow-box-title mig-color-cyan">{target_pqc_algorithm}</span>
              <span className="flow-box-sub">{dated_standard_ref}</span>
            </div>
          </div>

          <div className="mig-header-badges-row">
            <Badge variant={prioVariant}>Priority: {prioUpper}</Badge>
            <Badge variant={statusVariant}>Status: {statusStr.replace(/_/g, ' ')}</Badge>
            {typeof composite_risk_score === 'number' && (
              <Badge variant="neutral">Risk Score: {composite_risk_score.toFixed(1)}/100</Badge>
            )}
          </div>
        </div>

        {/* Actionable Recommendation Plan */}
        <section className="mig-modal-section" aria-label="Actionable Migration Step">
          <div className="mig-section-title-group">
            <Sparkles size={16} className="mig-section-icon mig-color-cyan" aria-hidden="true" />
            <h4 className="mig-section-title">Recommended Action Plan</h4>
          </div>

          <div className="mig-action-box">
            <p className="mig-action-text">{recommended_action}</p>
            {target_hybrid_algorithm && (
              <div className="mig-hybrid-notice">
                <strong>Interim Hybrid Pathway:</strong> <code>{target_hybrid_algorithm}</code>
              </div>
            )}
          </div>
        </section>

        {/* Compatibility Gaps & Operational Caveats */}
        {compatibility_gaps.length > 0 && (
          <section className="mig-modal-section" aria-label="Compatibility and Operational Gaps">
            <div className="mig-section-title-group">
              <AlertTriangle size={16} className="mig-section-icon mig-color-amber" aria-hidden="true" />
              <h4 className="mig-section-title">Operational Caveats & Engineering Constraints</h4>
            </div>

            <ul className="mig-gaps-list">
              {compatibility_gaps.map((gap, idx) => (
                <li key={idx} className="mig-gap-item">
                  {gap}
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Discovery Provenance & Asset Context */}
        <section className="mig-modal-section" aria-label="Target Asset Provenance">
          <div className="mig-section-title-group">
            <FileCode size={16} className="mig-section-icon" aria-hidden="true" />
            <h4 className="mig-section-title">Asset Provenance & Location</h4>
          </div>

          <div className="mig-provenance-grid">
            <div className="mig-prov-item">
              <span className="prov-label">Canonical Asset ID</span>
              <code className="prov-code">{asset_id}</code>
            </div>
            <div className="mig-prov-item">
              <span className="prov-label">Source Location</span>
              <code className="prov-code">
                {relative_path}
                {start_line && <span className="mig-line-highlight">:{start_line}</span>}
              </code>
            </div>
            <div className="mig-prov-item">
              <span className="prov-label">Review Owner</span>
              <span className="prov-value">{review_owner}</span>
            </div>
            <div className="mig-prov-item">
              <span className="prov-label">Task ID</span>
              <code className="prov-code">{task_id}</code>
            </div>
          </div>

          {reason_codes.length > 0 && (
            <div className="mig-reasons-row">
              <span className="prov-label">Assigned Reason Codes:</span>
              <div className="reasons-pills">
                {reason_codes.map((rc) => (
                  <span key={rc} className="reason-code-pill">
                    {rc}
                  </span>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* Benchmarking Caveat */}
        {operational_benchmarking_caveat && (
          <div className="mig-benchmarking-notice">
            <BookOpen size={14} className="mig-notice-icon" aria-hidden="true" />
            <p>{operational_benchmarking_caveat}</p>
          </div>
        )}

        {/* Cross-Cutting Navigation Links */}
        <section className="mig-modal-section" aria-label="Related Architectural Artifacts">
          <div className="mig-section-title-group">
            <Layers size={16} className="mig-section-icon" aria-hidden="true" />
            <h4 className="mig-section-title">Cross-Reference & Related Artifacts</h4>
          </div>

          <div className="mig-cross-links-grid">
            <Link
              to={scanId ? `/risk?scanId=${scanId}` : '/risk'}
              className="mig-cross-link-card"
              onClick={onClose}
            >
              <Flame size={16} className="cross-link-icon mig-color-amber" aria-hidden="true" />
              <div className="cross-link-text">
                <span className="cross-link-title">Risk Assessment</span>
                <span className="cross-link-sub">Inspect Mosca timelines ($X+Y&gt;Z$)</span>
              </div>
              <ExternalLink size={14} className="cross-link-ext" aria-hidden="true" />
            </Link>

            <Link
              to={scanId ? `/cbom?scanId=${scanId}` : '/cbom'}
              className="mig-cross-link-card"
              onClick={onClose}
            >
              <Package size={16} className="cross-link-icon mig-color-cyan" aria-hidden="true" />
              <div className="cross-link-text">
                <span className="cross-link-title">CBOM Inventory</span>
                <span className="cross-link-sub">CycloneDX 1.6 component spec</span>
              </div>
              <ExternalLink size={14} className="cross-link-ext" aria-hidden="true" />
            </Link>

            <Link
              to={scanId ? `/scans/${scanId}` : '/findings'}
              className="mig-cross-link-card"
              onClick={onClose}
            >
              <ShieldCheck size={16} className="cross-link-icon mig-color-emerald" aria-hidden="true" />
              <div className="cross-link-text">
                <span className="cross-link-title">Source Evidence</span>
                <span className="cross-link-sub">Inspect sanitized code snippet</span>
              </div>
              <ExternalLink size={14} className="cross-link-ext" aria-hidden="true" />
            </Link>
          </div>
        </section>
      </div>

      <div className="migration-modal-footer">
        <Button variant="outline" onClick={onClose} aria-label="Close migration recommendation modal">
          Close
        </Button>
      </div>
    </Modal>
  );
}
