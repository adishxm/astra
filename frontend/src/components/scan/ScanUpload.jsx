import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileArchive, CheckCircle2, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import { apiPostFile, getErrorMessage } from '../../api/client';
import Button from '../common/Button';
import ErrorBanner from '../common/ErrorBanner';
import LoadingSpinner from '../common/LoadingSpinner';
import './ScanUpload.css';

/* eslint-disable react-refresh/only-export-components */

const MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024; // 100 MB
const ALLOWED_EXTENSIONS = ['.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2'];

/**
 * Validates selected file against API intake constraints
 * @param {File} file
 * @returns {string | null} Error message or null if valid
 */
export function validateScanFile(file) {
  if (!file) {
    return 'Please select a repository archive to scan.';
  }

  if (file.size === 0) {
    return 'Uploaded archive is zero bytes. Please upload a valid archive.';
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    return `Uploaded archive exceeds maximum limit of 100 MB (${(file.size / (1024 * 1024)).toFixed(1)} MB selected).`;
  }

  const fileNameLower = file.name.toLowerCase();
  const hasValidExt = ALLOWED_EXTENSIONS.some((ext) => fileNameLower.endsWith(ext));

  if (!hasValidExt) {
    return 'Unsupported archive format. Expected one of: .zip, .tar, .tar.gz, .tar.bz2';
  }

  return null;
}

/**
 * Formats byte count to readable string
 * @param {number} bytes
 * @returns {string}
 */
export function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * @typedef {Object} ScanUploadProps
 * @property {(result: any) => void} [onSuccess]
 * @property {boolean} [navigateOnSuccess=true]
 * @property {string} [className]
 */

export default function ScanUpload({
  onSuccess,
  navigateOnSuccess = true,
  className = '',
}) {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const abortControllerRef = useRef(null);

  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [validationError, setValidationError] = useState(null);
  const [status, setStatus] = useState('idle'); // 'idle' | 'selected' | 'uploading' | 'analyzing' | 'success' | 'error'
  const [uploadPercent, setUploadPercent] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [apiError, setApiError] = useState(null);
  const [scanResult, setScanResult] = useState(null);

  // Elapsed timer while waiting for backend synchronous analysis response
  useEffect(() => {
    let timer;
    if (status === 'analyzing') {
      timer = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      setElapsedSeconds(0);
    }
    return () => clearInterval(timer);
  }, [status]);

  // Clean up abort controller on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const handleFileSelect = (selectedFile) => {
    setApiError(null);
    if (!selectedFile) return;

    const error = validateScanFile(selectedFile);
    if (error) {
      setValidationError(error);
      setFile(null);
      setStatus('error');
      return;
    }

    setValidationError(null);
    setFile(selectedFile);
    setStatus('selected');
  };

  const handleInputChange = (e) => {
    const selected = e.target.files?.[0];
    handleFileSelect(selected);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (status !== 'uploading' && status !== 'analyzing') {
      setDragOver(true);
    }
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);

    if (status === 'uploading' || status === 'analyzing') return;

    const droppedFile = e.dataTransfer.files?.[0];
    handleFileSelect(droppedFile);
  };

  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setStatus('selected');
    setUploadPercent(0);
    toast('Scan upload cancelled', { icon: 'ℹ️' });
  };

  const handleClear = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    setFile(null);
    setValidationError(null);
    setApiError(null);
    setStatus('idle');
    setUploadPercent(0);
    setScanResult(null);
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();

    if (!file) {
      setValidationError('Please select a file before submitting.');
      setStatus('error');
      return;
    }

    const valErr = validateScanFile(file);
    if (valErr) {
      setValidationError(valErr);
      setStatus('error');
      return;
    }

    setValidationError(null);
    setApiError(null);
    setStatus('uploading');
    setUploadPercent(0);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await apiPostFile(
        '/api/v1/scans/upload',
        file,
        (percent) => {
          setUploadPercent(percent);
          if (percent === 100) {
            setStatus('analyzing');
          }
        },
        { signal: controller.signal }
      );

      setStatus('success');
      setScanResult(response);
      toast.success(`Scan completed successfully! Discovered ${response.asset_count} cryptographic assets.`);

      if (onSuccess) {
        onSuccess(response);
      }

      if (navigateOnSuccess && response.scan_id) {
        setTimeout(() => {
          navigate(`/scans/${response.scan_id}`);
        }, 1200);
      }
    } catch (err) {
      if (err?.kind === 'aborted') {
        return;
      }
      setStatus('error');
      setApiError(err);
      toast.error(getErrorMessage(err));
    }
  };

  const isSubmitting = status === 'uploading' || status === 'analyzing';

  return (
    <div className={['scan-upload', className].filter(Boolean).join(' ')}>
      <input
        ref={fileInputRef}
        id="scan-file-input"
        type="file"
        accept=".zip,.tar,.tar.gz,.tgz,.tar.bz2,.tbz2"
        onChange={handleInputChange}
        disabled={isSubmitting}
        className="scan-upload__input-hidden"
        aria-describedby={validationError ? 'scan-upload-validation-error' : undefined}
      />

      {/* Upload Dropzone */}
      <div
        className={[
          'scan-upload__dropzone',
          dragOver ? 'scan-upload__dropzone--dragover' : '',
          isSubmitting ? 'scan-upload__dropzone--disabled' : '',
          file ? 'scan-upload__dropzone--has-file' : '',
        ]
          .filter(Boolean)
          .join(' ')}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isSubmitting && fileInputRef.current?.click()}
        onKeyDown={(e) => {
          if (!isSubmitting && (e.key === 'Enter' || e.key === ' ')) {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
        tabIndex={isSubmitting ? -1 : 0}
        role="button"
        aria-label="Upload repository archive dropzone"
      >
        <div className="scan-upload__icon" aria-hidden="true">
          {file ? <FileArchive size={40} /> : <UploadCloud size={40} />}
        </div>

        <div className="scan-upload__text-group">
          {file ? (
            <>
              <p className="scan-upload__filename">{file.name}</p>
              <p className="scan-upload__filesize">{formatBytes(file.size)}</p>
            </>
          ) : (
            <>
              <p className="scan-upload__prompt">
                <strong>Click to browse</strong> or drag and drop archive here
              </p>
              <p className="scan-upload__subtext">
                Supported formats: <code>.zip</code>, <code>.tar</code>, <code>.tar.gz</code>, <code>.tar.bz2</code> (Max 100 MB)
              </p>
            </>
          )}
        </div>
      </div>

      {/* Validation or API Error Banner */}
      {validationError && (
        <div id="scan-upload-validation-error" style={{ marginTop: 'var(--space-md)' }}>
          <ErrorBanner
            title="Invalid Archive"
            message={validationError}
            onDismiss={() => setValidationError(null)}
          />
        </div>
      )}

      {apiError && (
        <div style={{ marginTop: 'var(--space-md)' }}>
          <ErrorBanner
            title="Scan Failed"
            message={getErrorMessage(apiError)}
            onRetry={handleSubmit}
            onDismiss={() => setApiError(null)}
          />
        </div>
      )}

      {/* Uploading / Analyzing Progress Section */}
      {status === 'uploading' && (
        <div className="scan-upload__progress-panel" role="status" aria-live="polite">
          <div className="scan-upload__progress-info">
            <span className="scan-upload__progress-label">Uploading archive...</span>
            <span className="scan-upload__progress-percent">{uploadPercent}%</span>
          </div>
          <div className="scan-upload__progress-bar-track">
            <div
              className="scan-upload__progress-bar-fill"
              style={{ width: `${uploadPercent}%` }}
            />
          </div>
        </div>
      )}

      {status === 'analyzing' && (
        <div className="scan-upload__analyzing-panel" role="status" aria-live="polite">
          <LoadingSpinner
            size="md"
            label="Analyzing cryptographic inventory..."
            elapsedSeconds={elapsedSeconds}
          />
          <p className="scan-upload__analyzing-hint">
            Running NIST PQC ruleset and CBOM asset extractor on local CPU.
          </p>
        </div>
      )}

      {/* Success View */}
      {status === 'success' && scanResult && (
        <div className="scan-upload__success-panel" role="status" aria-live="polite">
          <div className="scan-upload__success-header">
            <CheckCircle2 size={24} className="scan-upload__success-icon" />
            <div>
              <strong className="scan-upload__success-title">Scan Complete: {scanResult.scan_id}</strong>
              <p className="scan-upload__success-meta">
                Discovered <strong>{scanResult.asset_count}</strong> cryptographic assets ({scanResult.coverage_percentage}% coverage).
              </p>
            </div>
          </div>
          <div className="scan-upload__actions">
            <Button
              variant="primary"
              onClick={() => navigate(`/scans/${scanResult.scan_id}`)}
            >
              View Findings
            </Button>
            <Button variant="ghost" onClick={handleClear}>
              Scan Another Archive
            </Button>
          </div>
        </div>
      )}

      {/* Action Buttons for Selected / Idle State */}
      {status !== 'success' && (
        <div className="scan-upload__actions">
          {isSubmitting ? (
            <Button variant="danger" size="md" onClick={handleCancel}>
              Cancel Scan
            </Button>
          ) : (
            <>
              <Button
                variant="primary"
                size="md"
                disabled={!file}
                onClick={handleSubmit}
                icon={<RefreshCw size={16} />}
              >
                Start Scan
              </Button>
              {file && (
                <Button variant="ghost" size="md" onClick={handleClear}>
                  Clear Selection
                </Button>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
