import React from 'react';
import Badge from '../common/Badge';
import './CollectorHealth.css';

/**
 * Collector Health Status Grid indicating detector engine operational status.
 */
export default function CollectorHealth({ health = {}, evaluatedAt = null }) {
  const detectors = Object.entries(health);

  if (detectors.length === 0) {
    return (
      <div className="collector-health-container" data-testid="collector-health-empty">
        <p style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>
          No detector health status telemetry available.
        </p>
      </div>
    );
  }

  return (
    <div className="collector-health-container" data-testid="collector-health">
      <div className="collector-health-header">
        <h3 className="collector-health-title">Collector & Detector Engine Health</h3>
        {evaluatedAt && (
          <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
            Evaluated at: {new Date(evaluatedAt).toLocaleString()}
          </span>
        )}
      </div>

      <div className="collector-health-grid">
        {detectors.map(([detectorId, status]) => {
          const isOk = String(status).toUpperCase() === 'OK';
          return (
            <div key={detectorId} className="collector-card">
              <span className="collector-name" title={detectorId}>
                {detectorId}
              </span>
              <Badge variant={isOk ? 'high' : 'warning'}>
                {status}
              </Badge>
            </div>
          );
        })}
      </div>
    </div>
  );
}
