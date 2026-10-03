import React from 'react';
import Badge from '../common/Badge';
import { sanitizeEvidenceContent } from '../findings/FindingDetailModal';
import './EvidenceViewer.css';

/**
 * EvidenceViewer Component providing clear distinction between Observed Raw Evidence and Derived System Interpretation.
 */
export default function EvidenceViewer({ observation }) {
  if (!observation) {
    return (
      <div className="evidence-viewer-container" data-testid="evidence-viewer-empty">
        <p style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>
          No observation or evidence selected.
        </p>
      </div>
    );
  }

  const rawExcerpt = sanitizeEvidenceContent(observation.sanitizedExcerpt || observation.sanitized_excerpt);
  const evidenceDigest = observation.evidenceDigest || observation.evidence_digest;
  const relativePath = observation.relativePath || observation.relative_path || 'Unknown';
  const startLine = observation.startLine ?? observation.start_line;
  const endLine = observation.endLine ?? observation.end_line;
  const sourceKind = observation.sourceKind || observation.source_kind || 'UNKNOWN';
  const algorithm = observation.algorithm || observation.primaryName || 'Unknown';
  const purpose = observation.purpose || 'UNSPECIFIED';
  const confidence = observation.confidence || 'UNASSESSED';
  const confidenceRationale = observation.confidenceRationale || observation.confidence_rationale;
  const detectorId = observation.detectorId || observation.detector_id || 'unknown-detector';
  const rulesetVersion = observation.rulesetVersion || observation.ruleset_version || '2026.10-nist-pqc';
  const observedAt = observation.observedAt || observation.observed_at;
  const rawParams = observation.rawParameters || observation.raw_parameters || {};

  const locText = relativePath !== 'Unknown'
    ? (startLine ? `${relativePath}:${startLine}${endLine && endLine !== startLine ? `-${endLine}` : ''}` : relativePath)
    : 'Unknown location';

  return (
    <div className="evidence-viewer-container" data-testid="evidence-viewer">
      <div className="evidence-comparison-grid">
        {/* Column 1: What the scanner actually observed (Raw Evidence) */}
        <div className="evidence-column-card raw-evidence">
          <div className="evidence-column-header">
            <span className="evidence-column-title">
              🔬 Observed Raw Evidence
            </span>
            <Badge variant="primary">RAW OBSERVATION</Badge>
          </div>

          <div className="evidence-items-list">
            <div className="evidence-property">
              <span className="evidence-prop-label">Physical Location</span>
              <code className="evidence-prop-code">{locText}</code>
            </div>

            <div className="evidence-property">
              <span className="evidence-prop-label">Surface Surface</span>
              <span className="evidence-prop-value">{sourceKind}</span>
            </div>

            <div className="evidence-property">
              <span className="evidence-prop-label">Sanitized Excerpt</span>
              <pre className="evidence-code-box">
                <code>{rawExcerpt}</code>
              </pre>
            </div>

            {evidenceDigest && (
              <div className="evidence-property">
                <span className="evidence-prop-label">SHA-256 Evidence Digest</span>
                <code className="evidence-prop-code" title={evidenceDigest}>
                  {evidenceDigest}
                </code>
              </div>
            )}

            {Object.keys(rawParams).length > 0 && (
              <div className="evidence-property">
                <span className="evidence-prop-label">Intake Parameters</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '2px' }}>
                  {Object.entries(rawParams).map(([k, v]) => (
                    <span key={k} className="evidence-prop-code">
                      {k}: {String(v)}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Column 2: What the system derives (Derived System Interpretation) */}
        <div className="evidence-column-card derived-interpretation">
          <div className="evidence-column-header">
            <span className="evidence-column-title">
              🧠 Derived Interpretation
            </span>
            <Badge variant="secondary">SYSTEM INFERENCE</Badge>
          </div>

          <div className="evidence-items-list">
            <div className="evidence-property">
              <span className="evidence-prop-label">Classified Primitive</span>
              <span className="evidence-prop-value" style={{ fontWeight: 600 }}>
                {algorithm}
              </span>
            </div>

            <div className="evidence-property">
              <span className="evidence-prop-label">Cryptographic Purpose</span>
              <span className="evidence-prop-value">{purpose}</span>
            </div>

            <div className="evidence-property">
              <span className="evidence-prop-label">Confidence Assessment</span>
              <div>
                <Badge
                  variant={
                    confidence === 'CONFIRMED'
                      ? 'high'
                      : confidence === 'HIGH' || confidence === 'INFERRED'
                      ? 'medium'
                      : 'neutral'
                  }
                >
                  {confidence}
                </Badge>
              </div>
            </div>

            {confidenceRationale && (
              <div className="evidence-property">
                <span className="evidence-prop-label">Confidence Rationale</span>
                <p style={{ margin: 0, fontSize: 'var(--font-size-xs)', color: 'var(--text-main)', lineHeight: 1.4 }}>
                  {confidenceRationale}
                </p>
              </div>
            )}

            <div className="evidence-property">
              <span className="evidence-prop-label">Detector Provenance</span>
              <span className="evidence-prop-value" style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--font-size-xs)' }}>
                {detectorId} ({rulesetVersion})
              </span>
            </div>

            {observedAt && (
              <div className="evidence-property">
                <span className="evidence-prop-label">Evaluation Timestamp</span>
                <span className="evidence-prop-value" style={{ fontSize: 'var(--font-size-xs)' }}>
                  {new Date(observedAt).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
