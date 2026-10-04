import React from 'react';
import Badge from '../common/Badge';
import './SurfaceBreakdown.css';

/**
 * Returns surface badge variant.
 */
function getSurfaceBadgeVariant(surface) {
  const norm = String(surface).toUpperCase();
  if (norm === 'SOURCE_CODE') return 'primary';
  if (norm === 'PACKAGE_MANIFEST') return 'warning';
  if (norm === 'CONFIGURATION' || norm === 'CONFIG') return 'secondary';
  if (norm === 'CERTIFICATE_STORE' || norm === 'CERTIFICATE') return 'high';
  return 'neutral';
}

/**
 * Surface Breakdown Matrix displaying per-surface coverage metrics.
 */
export default function SurfaceBreakdown({ surfaceBreakdown = {}, onSelectSurface }) {
  const surfaces = Object.entries(surfaceBreakdown);

  if (surfaces.length === 0) {
    return (
      <div className="surface-breakdown-container" data-testid="surface-breakdown-empty">
        <p style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>
          No surface coverage breakdown available for this scan.
        </p>
      </div>
    );
  }

  return (
    <div className="surface-breakdown-container" data-testid="surface-breakdown">
      <div className="surface-breakdown-header">
        <h3 className="surface-breakdown-title">Discovery Surface Breakdown</h3>
        <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
          Assessed across {surfaces.length} cryptographic discovery surfaces
        </span>
      </div>

      <div className="surface-breakdown-grid">
        {surfaces.map(([surfaceKey, data]) => {
          const pct = typeof data.coverage_percentage === 'number' ? data.coverage_percentage : 0;
          const total = data.total_files ?? 0;
          const assessed = data.assessed_files ?? 0;
          const withFindings = data.files_with_findings ?? 0;
          const noFindings = data.files_with_no_findings ?? 0;
          const unsupported = data.unsupported_files ?? 0;

          return (
            <div
              key={surfaceKey}
              className={`surface-detail-card ${onSelectSurface ? 'clickable' : ''}`}
              onClick={() => onSelectSurface?.(surfaceKey)}
              tabIndex={onSelectSurface ? 0 : undefined}
              role={onSelectSurface ? 'button' : undefined}
              onKeyDown={(e) => {
                if (onSelectSurface && (e.key === 'Enter' || e.key === ' ')) {
                  e.preventDefault();
                  onSelectSurface(surfaceKey);
                }
              }}
              aria-label={`Surface ${surfaceKey}: ${pct.toFixed(0)}% coverage`}
            >
              <div className="surface-card-top">
                <Badge variant={getSurfaceBadgeVariant(surfaceKey)}>
                  {surfaceKey}
                </Badge>
                <span className="surface-pct">{pct.toFixed(1)}%</span>
              </div>

              {/* Progress Bar */}
              <div className="surface-bar-bg" aria-hidden="true">
                <div
                  className="surface-bar-fill"
                  style={{
                    width: `${Math.min(100, Math.max(0, pct))}%`,
                    background:
                      surfaceKey === 'UNSUPPORTED_SURFACE'
                        ? 'var(--text-dim)'
                        : 'var(--accent-primary)',
                  }}
                />
              </div>

              {/* Stats list */}
              <div className="surface-stats-list">
                <div className="surface-stat-row">
                  <span>Assessed Files:</span>
                  <strong>{assessed} / {total}</strong>
                </div>
                <div className="surface-stat-row">
                  <span>Files with Findings:</span>
                  <strong>{withFindings}</strong>
                </div>
                <div className="surface-stat-row">
                  <span>Files without Findings:</span>
                  <strong>{noFindings}</strong>
                </div>
                {unsupported > 0 && (
                  <div className="surface-stat-row">
                    <span>Unsupported Files:</span>
                    <strong>{unsupported}</strong>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
