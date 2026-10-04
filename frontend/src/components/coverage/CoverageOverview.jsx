import React from 'react';
import Card from '../common/Card';
import Badge from '../common/Badge';
import ProgressRing from '../common/ProgressRing';
import './CoverageOverview.css';

/**
 * Coverage Overview Component presenting truthful archive coverage statistics.
 */
export default function CoverageOverview({ coverage = {}, summary = {} }) {
  const overallPercentage = typeof coverage.overall_coverage_percentage === 'number'
    ? coverage.overall_coverage_percentage
    : typeof summary.coverage_percentage === 'number'
    ? summary.coverage_percentage
    : null;

  const totalFiles = coverage.total_files_in_archive ?? summary.total_files ?? 0;
  const assessedFiles = coverage.total_assessed_files ?? summary.assessed_files ?? 0;
  const unsupportedFiles = coverage.total_unsupported_files ?? 0;
  const skippedFiles = coverage.total_skipped_files ?? 0;
  const failedFiles = coverage.total_failed_files ?? 0;
  const totalObservations = coverage.total_observations_found ?? 0;
  const statusLabel = coverage.scan_status_label || summary.clean_state_label || 'UNASSESSED';
  const isPartial = Boolean(coverage.is_partial_scan);

  return (
    <div className="coverage-overview-container" data-testid="coverage-overview">
      {/* Honesty Reminder */}
      <div className="coverage-truth-banner" role="note">
        <span className="coverage-truth-icon" aria-hidden="true">ℹ️</span>
        <span>
          <strong>Truthful Accounting:</strong> Assessed coverage reflects file surfaces analyzed by ASTRA detectors. 100% surface coverage indicates complete assessment, not 0% risk.
        </span>
      </div>

      <div className="coverage-overview-grid">
        {/* Overall Percentage Card */}
        <Card>
          <div className="coverage-metric-card">
            <div className="coverage-metric-info">
              <span className="coverage-metric-title">Assessed Coverage</span>
              <span className="coverage-metric-value">
                {overallPercentage !== null ? `${overallPercentage.toFixed(1)}%` : 'N/A'}
              </span>
              <span className="coverage-metric-subtext">
                {assessedFiles} of {totalFiles} total files assessed
              </span>
            </div>
            {overallPercentage !== null && (
              <ProgressRing value={overallPercentage} size={64} strokeWidth={6} />
            )}
          </div>
        </Card>

        {/* Accounting & Integrity Card */}
        <Card>
          <div className="coverage-metric-card">
            <div className="coverage-metric-info">
              <span className="coverage-metric-title">Integrity & Completeness</span>
              <div style={{ marginTop: '4px' }}>
                <Badge variant={isPartial ? 'warning' : 'high'}>
                  {statusLabel}
                </Badge>
              </div>
              <span className="coverage-metric-subtext" style={{ marginTop: '4px' }}>
                {isPartial ? 'Partial scan with unassessed surfaces' : 'Complete with full coverage accounting'}
              </span>
            </div>
            <div style={{ fontSize: '2rem', opacity: 0.8 }} aria-hidden="true">
              🛡️
            </div>
          </div>
        </Card>

        {/* Discovered Observations Card */}
        <Card>
          <div className="coverage-metric-card">
            <div className="coverage-metric-info">
              <span className="coverage-metric-title">Discovered Observations</span>
              <span className="coverage-metric-value">{totalObservations}</span>
              <span className="coverage-metric-subtext">
                Evidence-backed cryptographic usages
              </span>
            </div>
            <div style={{ fontSize: '2rem', opacity: 0.8 }} aria-hidden="true">
              🔍
            </div>
          </div>
        </Card>

        {/* File Breakdown Matrix Card */}
        <Card>
          <div className="coverage-metric-info">
            <span className="coverage-metric-title">File Accounting Matrix</span>
            <div className="coverage-files-breakdown">
              <span className="file-stat-pill" title="Assessed files">
                Assessed: <strong>{assessedFiles}</strong>
              </span>
              <span className="file-stat-pill" title="Unsupported file extensions">
                Unsupported: <strong>{unsupportedFiles}</strong>
              </span>
              <span className="file-stat-pill" title="Skipped files">
                Skipped: <strong>{skippedFiles}</strong>
              </span>
              <span className="file-stat-pill" title="Failed extraction files">
                Failed: <strong>{failedFiles}</strong>
              </span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
