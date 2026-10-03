import React, { useState, useMemo } from 'react';
import Badge from '../common/Badge';
import './CoverageGapsTable.css';

/**
 * Formats file size in bytes to human-readable string.
 * @param {number} bytes
 * @returns {string}
 */
export function formatBytes(bytes) {
  if (typeof bytes !== 'number' || isNaN(bytes) || bytes < 0) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

/**
 * Coverage Gaps Table disclosing unsupported and skipped files truthfully.
 */
export default function CoverageGapsTable({ manifestFiles = [], unsupportedExtensions = [] }) {
  const [filterQuery, setFilterQuery] = useState('');

  // Filter only files that are unsupported or skipped
  const gapFiles = useMemo(() => {
    return manifestFiles.filter((f) => !f.is_supported || f.skip_reason);
  }, [manifestFiles]);

  const filteredGaps = useMemo(() => {
    if (!filterQuery.trim()) return gapFiles;
    const q = filterQuery.toLowerCase();
    return gapFiles.filter((f) => {
      const pathMatch = f.relative_path?.toLowerCase().includes(q);
      const extMatch = f.file_extension?.toLowerCase().includes(q);
      const reasonMatch = f.skip_reason?.toLowerCase().includes(q);
      return pathMatch || extMatch || reasonMatch;
    });
  }, [gapFiles, filterQuery]);

  return (
    <div className="coverage-gaps-container" data-testid="coverage-gaps-table">
      <div className="coverage-gaps-header">
        <div>
          <h3 className="coverage-gaps-title">Coverage Gaps & Unsupported Files</h3>
          <p style={{ margin: '4px 0 0', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
            Transparent disclosure of unassessed file surfaces, binary assets, and skipped formats.
          </p>
        </div>

        {gapFiles.length > 0 && (
          <input
            type="text"
            className="findings-search-input"
            style={{ maxWidth: '240px', padding: '4px 8px', fontSize: 'var(--font-size-xs)' }}
            placeholder="Filter gap files..."
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            aria-label="Filter gap files"
          />
        )}
      </div>

      {/* Unsupported Extensions Bar */}
      {unsupportedExtensions.length > 0 && (
        <div className="unsupported-extensions-banner">
          <span style={{ color: 'var(--text-dim)', fontWeight: 600 }}>
            Unsupported File Extensions:
          </span>
          {unsupportedExtensions.map((ext) => (
            <span key={ext} className="unsupported-ext-pill">
              {ext}
            </span>
          ))}
        </div>
      )}

      {/* Gaps Table */}
      <div className="coverage-gaps-table-wrapper">
        <table className="coverage-gaps-table" aria-label="Coverage Gaps List">
          <thead>
            <tr>
              <th scope="col">File Path</th>
              <th scope="col">Extension</th>
              <th scope="col">Size</th>
              <th scope="col">Status</th>
              <th scope="col">Reason / Assessment Gap</th>
              <th scope="col">SHA-256 Digest</th>
            </tr>
          </thead>
          <tbody>
            {filteredGaps.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', padding: 'var(--space-lg)', color: 'var(--text-muted)' }}>
                  {gapFiles.length === 0
                    ? 'All files in the archive were supported and assessed by ASTRA detectors.'
                    : 'No gap files match your filter.'}
                </td>
              </tr>
            ) : (
              filteredGaps.map((file, idx) => {
                const isSkipped = Boolean(file.skip_reason);
                const statusText = isSkipped ? 'SKIPPED' : 'UNSUPPORTED';

                return (
                  <tr key={file.relative_path || idx}>
                    <td>
                      <code className="gap-path-code">{file.relative_path}</code>
                    </td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--font-size-xs)', color: 'var(--text-dim)' }}>
                        {file.file_extension || 'None'}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontSize: 'var(--font-size-xs)' }}>
                        {formatBytes(file.size_bytes)}
                      </span>
                    </td>
                    <td>
                      <Badge variant="neutral">{statusText}</Badge>
                    </td>
                    <td>
                      <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                        {file.skip_reason || 'File format not in NIST PQC ruleset scope (non-code / media)'}
                      </span>
                    </td>
                    <td>
                      <code className="gap-hash-code" title={file.sha256}>
                        {file.sha256 ? file.sha256 : 'N/A'}
                      </code>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
