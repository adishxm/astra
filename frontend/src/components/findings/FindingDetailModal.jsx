import React from 'react';
import Modal from '../common/Modal';
import Badge from '../common/Badge';
import Button from '../common/Button';
import './FindingDetailModal.css';

/**
 * Redaction safeguard to ensure no private keys or secrets are ever rendered.
 * @param {string} text
 * @returns {string}
 */
export function sanitizeEvidenceContent(text) {
  if (!text) return 'Evidence unavailable';
  let sanitized = String(text);

  // Redact private keys
  sanitized = sanitized.replace(
    /-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----/gi,
    '[REDACTED_PRIVATE_KEY_MATERIAL]'
  );

  // Redact common password / auth token patterns if present
  sanitized = sanitized.replace(
    /(password|secret|token|api_key|apikey|auth_token)\s*[:=]\s*["'][^"']+["']/gi,
    '$1: "[REDACTED_SECRET]"'
  );

  return sanitized;
}

/**
 * Finding Detail Modal presenting complete observation context and evidence.
 */
export default function FindingDetailModal({ finding, open, isOpen, onClose }) {
  const isModalOpen = Boolean(open ?? isOpen);
  if (!finding) return null;

  const locText = finding.relativePath !== 'Unknown'
    ? (finding.startLine
        ? `${finding.relativePath}:${finding.startLine}${finding.endLine && finding.endLine !== finding.startLine ? `-${finding.endLine}` : ''}`
        : finding.relativePath)
    : 'Unknown location';

  const sanitizedExcerpt = sanitizeEvidenceContent(finding.sanitizedExcerpt);

  // Urgency / Risk level if evaluated
  const riskUrgency = finding.riskEvaluation?.urgency;
  const riskScore = finding.riskEvaluation?.risk_score;

  return (
    <Modal
      open={isModalOpen}
      onClose={onClose}
      title={`Finding Details: ${finding.algorithm || finding.primaryName}`}
      data-testid="finding-detail-modal"
    >
      <div className="finding-detail-content">
        {/* Core Metadata Grid */}
        <div className="finding-detail-grid">
          <div className="detail-item">
            <span className="detail-label">Asset Identifier</span>
            <span className="detail-value detail-value-mono">{finding.assetId}</span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Algorithm / Primitive</span>
            <span className="detail-value" style={{ fontWeight: 600 }}>
              {finding.algorithm}
            </span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Source Surface</span>
            <span className="detail-value">
              <Badge variant="primary">{finding.sourceKind}</Badge>
            </span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Discovery Confidence</span>
            <span className="detail-value">
              <Badge
                variant={
                  finding.confidence === 'CONFIRMED'
                    ? 'high'
                    : finding.confidence === 'HIGH' || finding.confidence === 'INFERRED'
                    ? 'medium'
                    : 'neutral'
                }
              >
                {finding.confidence}
              </Badge>
            </span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Purpose / Usage</span>
            <span className="detail-value">{finding.purpose || 'UNSPECIFIED'}</span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Claim Type</span>
            <span className="detail-value">{finding.claimType || 'ALGORITHM_USE'}</span>
          </div>

          {finding.keySizeBits && (
            <div className="detail-item">
              <span className="detail-label">Key Size</span>
              <span className="detail-value">{finding.keySizeBits} bits</span>
            </div>
          )}

          {finding.curveName && (
            <div className="detail-item">
              <span className="detail-label">Elliptic Curve</span>
              <span className="detail-value">{finding.curveName}</span>
            </div>
          )}

          {riskUrgency && (
            <div className="detail-item">
              <span className="detail-label">Migration Urgency</span>
              <span className="detail-value">
                <Badge
                  variant={
                    riskUrgency === 'CRITICAL'
                      ? 'critical'
                      : riskUrgency === 'HIGH'
                      ? 'high'
                      : riskUrgency === 'MEDIUM'
                      ? 'medium'
                      : 'low'
                  }
                >
                  {riskUrgency} ({riskScore ? riskScore.toFixed(1) : 'N/A'})
                </Badge>
              </span>
            </div>
          )}
        </div>

        {/* Location & Detector Provenance */}
        <div className="detail-section">
          <h4 className="detail-section-title">📍 Source Location & Provenance</h4>
          <div className="finding-detail-grid">
            <div className="detail-item">
              <span className="detail-label">File & Line</span>
              <span className="detail-value detail-value-mono">{locText}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Detector ID</span>
              <span className="detail-value detail-value-mono">{finding.detectorId}</span>
            </div>
            {finding.rulesetVersion && (
              <div className="detail-item">
                <span className="detail-label">Ruleset Version</span>
                <span className="detail-value detail-value-mono">{finding.rulesetVersion}</span>
              </div>
            )}
            {finding.observedAt && (
              <div className="detail-item">
                <span className="detail-label">Observed Timestamp</span>
                <span className="detail-value">
                  {new Date(finding.observedAt).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Confidence Rationale */}
        {finding.confidenceRationale && (
          <div className="detail-section">
            <h4 className="detail-section-title">🔍 Confidence Rationale</h4>
            <p style={{ margin: 0, fontSize: 'var(--font-size-sm)', color: 'var(--text-main)' }}>
              {finding.confidenceRationale}
            </p>
          </div>
        )}

        {/* Sanitized Evidence Excerpt */}
        <div className="detail-section">
          <h4 className="detail-section-title">📄 Sanitized Evidence Excerpt</h4>
          <pre className="evidence-box">
            <code>{sanitizedExcerpt}</code>
          </pre>
          <div className="redaction-notice">
            🔒 Private keys and raw credentials are automatically redacted by ASTRA intake engine.
          </div>
        </div>

        {/* Evidence Digest */}
        {finding.evidenceDigest && (
          <div className="detail-section">
            <div className="evidence-digest-wrapper">
              <span>SHA-256 Digest:</span>
              <span className="evidence-digest-hash">{finding.evidenceDigest}</span>
            </div>
          </div>
        )}

        {/* Modal Actions */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-sm)' }}>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
}
