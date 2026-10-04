import React, { useState } from 'react';
import Modal from '../common/Modal';
import Badge from '../common/Badge';
import Button from '../common/Button';
import { formatPurpose } from './CbomInventoryTable';
import {
  Package,
  Cpu,
  FileCode,
  KeyRound,
  Terminal,
  Copy,
  Check,
  Layers,
  Fingerprint,
} from 'lucide-react';
import './CbomDetailModal.css';

/**
 * CBOM Cryptographic Component Detail Modal
 *
 * @param {Object} props
 * @param {Object|null} props.component
 * @param {boolean} props.open
 * @param {() => void} props.onClose
 */
export default function CbomDetailModal({
  component = null,
  open = false,
  onClose,
}) {
  const [copied, setCopied] = useState(false);

  if (!component) return null;

  const {
    componentName,
    assetId,
    algorithm = 'Unknown Algorithm',
    purpose = 'UNSPECIFIED',
    assetType = 'algorithm',
    parameterSetIdentifier = 'standard',
    executionEnvironment = 'software-plain-ram',
    keySizeBits,
    curveName,
    sourceKind = 'UNKNOWN',
    claimType = 'ALGORITHM_USE',
    relativePath = 'Unknown location',
    startLine,
    endLine,
    confidence = 'UNASSESSED',
    confidenceRationale,
    sanitizedExcerpt,
    evidenceDigest,
    detectorId = 'unknown-detector',
    rulesetVersion,
    cycloneDxComponent,
  } = component;

  const confUpper = String(confidence).toUpperCase();
  const confVariant =
    confUpper === 'CONFIRMED'
      ? 'safe'
      : confUpper === 'INFERRED'
      ? 'medium'
      : confUpper === 'HEURISTIC'
      ? 'high'
      : 'unknown';

  // Format CycloneDX component JSON representation
  const componentJson = JSON.stringify(
    cycloneDxComponent || {
      type: 'cryptographic-asset',
      name: componentName || `${algorithm}-${assetId}`,
      cryptoProperties: {
        assetType,
        algorithmProperties: {
          name: algorithm,
          parameterSetIdentifier,
          executionEnvironment,
        },
      },
    },
    null,
    2
  );

  const handleCopyJson = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(componentJson).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`CBOM Component: ${algorithm}`}
      size="lg"
      className="cbom-detail-modal"
    >
      <div className="cbom-modal-body" data-testid="cbom-detail-modal-body">
        {/* Header Summary Banner */}
        <div className="cbom-modal-header-banner">
          <div className="cbom-header-meta">
            <div className="cbom-meta-title-row">
              <h3 className="cbom-algo-heading">{algorithm}</h3>
              <Badge variant="primary">{formatPurpose(purpose)}</Badge>
              <Badge variant={confVariant}>Confidence: {confUpper}</Badge>
            </div>

            <div className="cbom-component-id-row">
              <Package size={14} className="cbom-meta-icon" aria-hidden="true" />
              <span>CycloneDX Name:</span>
              <code className="cbom-component-code">{componentName || algorithm}</code>
            </div>

            <div className="cbom-asset-id-row">
              <FileCode size={14} className="cbom-meta-icon" aria-hidden="true" />
              <span>Canonical Asset ID:</span>
              <code className="cbom-asset-code">{assetId}</code>
            </div>
          </div>
        </div>

        {/* CycloneDX 1.6 Cryptographic Properties */}
        <section className="cbom-modal-section" aria-label="CycloneDX Cryptographic Properties">
          <div className="cbom-section-title-group">
            <KeyRound size={16} className="cbom-section-icon" aria-hidden="true" />
            <h4 className="cbom-section-title">CycloneDX 1.6 Cryptographic Properties</h4>
          </div>

          <div className="cbom-props-grid">
            <div className="cbom-prop-item">
              <span className="prop-label">Asset Type</span>
              <code className="prop-value">{assetType}</code>
            </div>
            <div className="cbom-prop-item">
              <span className="prop-label">Parameter Set Identifier</span>
              <code className="prop-value">{parameterSetIdentifier}</code>
            </div>
            <div className="cbom-prop-item">
              <span className="prop-label">Execution Environment</span>
              <code className="prop-value">{executionEnvironment}</code>
            </div>
            <div className="cbom-prop-item">
              <span className="prop-label">Key Size / Curve</span>
              <span className="prop-value">
                {keySizeBits ? `${keySizeBits} bits` : curveName || 'N/A (Standard Parameters)'}
              </span>
            </div>
          </div>
        </section>

        {/* Discovery Provenance & Source Location */}
        <section className="cbom-modal-section" aria-label="Discovery Provenance and Location">
          <div className="cbom-section-title-group">
            <Layers size={16} className="cbom-section-icon" aria-hidden="true" />
            <h4 className="cbom-section-title">Discovery Provenance & Evidence</h4>
          </div>

          <div className="cbom-provenance-box">
            <div className="provenance-row">
              <span className="prov-label">Discovery Surface:</span>
              <Badge variant="neutral">{sourceKind}</Badge>
              <span className="prov-claim-tag">Claim: {claimType}</span>
            </div>

            <div className="provenance-row">
              <span className="prov-label">Source File:</span>
              <code className="prov-path-code">
                {relativePath}
                {startLine !== null && startLine !== undefined && (
                  <span className="prov-line-highlight">
                    :{startLine}
                    {endLine && endLine !== startLine ? `-${endLine}` : ''}
                  </span>
                )}
              </code>
            </div>

            <div className="provenance-row">
              <span className="prov-label">Detector Engine:</span>
              <span className="prov-detector-text">{detectorId}</span>
              {rulesetVersion && (
                <span className="prov-ruleset-tag">Ruleset: {rulesetVersion}</span>
              )}
            </div>

            {confidenceRationale && (
              <div className="provenance-rationale">
                <span className="prov-label">Confidence Rationale:</span>
                <p className="rationale-text">{confidenceRationale}</p>
              </div>
            )}

            {evidenceDigest && (
              <div className="provenance-digest-row">
                <Fingerprint size={13} aria-hidden="true" />
                <span>Evidence Digest (SHA-256):</span>
                <code className="digest-code">{evidenceDigest}</code>
              </div>
            )}
          </div>
        </section>

        {/* Sanitized Evidence Snippet */}
        {sanitizedExcerpt && (
          <section className="cbom-modal-section" aria-label="Sanitized Source Evidence">
            <div className="cbom-section-title-group">
              <Terminal size={16} className="cbom-section-icon" aria-hidden="true" />
              <h4 className="cbom-section-title">Sanitized Source Evidence</h4>
            </div>

            <pre className="cbom-evidence-pre">
              <code>{sanitizedExcerpt}</code>
            </pre>
          </section>
        )}

        {/* CycloneDX 1.6 Component JSON Preview */}
        <section className="cbom-modal-section" aria-label="CycloneDX JSON Representation">
          <div className="cbom-section-header-row">
            <div className="cbom-section-title-group">
              <Cpu size={16} className="cbom-section-icon" aria-hidden="true" />
              <h4 className="cbom-section-title">CycloneDX 1.6 Component JSON</h4>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopyJson}
              aria-label="Copy component CycloneDX JSON"
            >
              {copied ? <Check size={14} className="cbom-color-emerald" /> : <Copy size={14} />}
              <span>{copied ? 'Copied' : 'Copy JSON'}</span>
            </Button>
          </div>

          <pre className="cbom-json-pre">
            <code>{componentJson}</code>
          </pre>
        </section>
      </div>

      <div className="cbom-modal-footer">
        <Button variant="outline" onClick={onClose} aria-label="Close component detail dialog">
          Close
        </Button>
      </div>
    </Modal>
  );
}
