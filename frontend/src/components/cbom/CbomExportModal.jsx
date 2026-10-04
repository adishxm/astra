import React, { useState } from 'react';
import Modal from '../common/Modal';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorBanner from '../common/ErrorBanner';
import { useApi } from '../../hooks/useApi';
import { Download, Copy, Check, FileCheck2 } from 'lucide-react';
import './CbomExportModal.css';

/**
 * Modal to preview, copy, and download the CycloneDX 1.6 Cryptographic Bill of Materials (CBOM).
 *
 * @param {Object} props
 * @param {boolean} props.open
 * @param {() => void} props.onClose
 * @param {string} props.scanId
 * @param {string} [props.archiveName]
 */
export default function CbomExportModal({
  open = false,
  onClose,
  scanId,
  archiveName = 'software_repository',
}) {
  const [copied, setCopied] = useState(false);

  // Fetch CycloneDX export from documented endpoint: GET /api/v1/scans/{scanId}/export?format=cyclonedx
  const { data: exportData, loading, error, refetch } = useApi(
    open && scanId ? `/api/v1/scans/${scanId}/export?format=cyclonedx` : null
  );

  const jsonString = exportData ? JSON.stringify(exportData, null, 2) : '';

  const handleCopy = () => {
    if (navigator.clipboard && jsonString) {
      navigator.clipboard.writeText(jsonString).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  };

  const handleDownload = () => {
    if (!jsonString) return;
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `astra-cbom-${scanId || 'export'}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (!open) return null;

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Export CycloneDX 1.6 CBOM"
      size="lg"
      className="cbom-export-modal"
    >
      <div className="cbom-export-body" data-testid="cbom-export-modal-body">
        {/* Specification Info Header */}
        <div className="export-spec-banner">
          <FileCheck2 size={20} className="cbom-color-emerald" aria-hidden="true" />
          <div className="export-spec-text">
            <h4 className="export-spec-title">CycloneDX 1.6 Cryptographic Standard</h4>
            <span className="export-spec-subtext">
              Fully compliant schema with cryptographic asset properties, execution environment, and algorithm parameters.
            </span>
          </div>
        </div>

        {loading ? (
          <div className="export-loading-box" data-testid="export-loading">
            <LoadingSpinner label="Generating CycloneDX 1.6 CBOM payload..." />
          </div>
        ) : error ? (
          <ErrorBanner
            title="Unable to generate CBOM export"
            message={error}
            onRetry={refetch}
          />
        ) : (
          <div className="export-content-stack">
            <div className="export-meta-row">
              <span>Target: <strong>{archiveName}</strong></span>
              <span>•</span>
              <span>Scan ID: <code>{scanId}</code></span>
              <span>•</span>
              <span>Components: <strong>{exportData?.components?.length ?? 0}</strong></span>
            </div>

            <pre className="export-json-preview" data-testid="export-json-preview">
              <code>{jsonString}</code>
            </pre>
          </div>
        )}
      </div>

      <div className="cbom-export-footer">
        <Button variant="outline" onClick={onClose} aria-label="Close export dialog">
          Cancel
        </Button>

        <div className="export-actions-right">
          <Button
            variant="secondary"
            disabled={!exportData || loading}
            onClick={handleCopy}
            data-testid="copy-cbom-btn"
          >
            {copied ? <Check size={15} className="cbom-color-emerald" /> : <Copy size={15} />}
            <span>{copied ? 'Copied to Clipboard' : 'Copy JSON'}</span>
          </Button>

          <Button
            variant="primary"
            disabled={!exportData || loading}
            onClick={handleDownload}
            data-testid="download-cbom-btn"
          >
            <Download size={15} aria-hidden="true" />
            <span>Download CBOM JSON</span>
          </Button>
        </div>
      </div>
    </Modal>
  );
}
