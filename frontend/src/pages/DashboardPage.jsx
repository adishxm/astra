import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, FileCode, Activity, ArrowRight, UploadCloud, RefreshCw } from 'lucide-react';
import { useScans } from '../hooks/useScans';
import { useHealth } from '../hooks/useHealth';
import { usePageTitle } from '../hooks/usePageTitle';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import ProgressRing from '../components/common/ProgressRing';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import EmptyState from '../components/common/EmptyState';
import './DashboardPage.css';

export default function DashboardPage() {
  usePageTitle('Dashboard');
  const navigate = useNavigate();

  const { scans, loading: scansLoading, error: scansError, refetch: refetchScans } = useScans();
  const { isHealthy, loading: healthLoading } = useHealth();

  const hasScans = Array.isArray(scans) && scans.length > 0;
  const latestScan = hasScans ? scans[0] : null;

  // Compute aggregate stats across real API scan data
  const totalAssetsDiscovered = hasScans
    ? scans.reduce((acc, scan) => acc + (scan.asset_count || 0), 0)
    : 0;

  const latestCoverage = latestScan?.coverage_percentage ?? null;

  return (
    <div className="dashboard">
      <div className="dashboard__header">
        <div>
          <h1 className="dashboard__title">Dashboard</h1>
          <p className="dashboard__subtitle">
            Cryptographic discovery, asset inventory, and Post-Quantum Cryptography (PQC) readiness.
          </p>
        </div>
        <div className="dashboard__header-actions">
          <Button
            variant="secondary"
            size="sm"
            onClick={refetchScans}
            icon={<RefreshCw size={14} />}
            aria-label="Refresh dashboard data"
          >
            Refresh
          </Button>
          <Button
            as={Link}
            to="/scan"
            variant="primary"
            size="sm"
            icon={<UploadCloud size={16} />}
          >
            New Scan
          </Button>
        </div>
      </div>

      {/* Loading State */}
      {scansLoading && !hasScans && !scansError && (
        <div className="dashboard__status-wrapper">
          <LoadingSpinner size="lg" label="Loading cryptographic inventory overview..." />
        </div>
      )}

      {/* Error State */}
      {scansError && !scansLoading && (
        <div className="dashboard__status-wrapper">
          <ErrorBanner
            title="Failed to Load Scans"
            message={scansError.message || 'Unable to retrieve scan list from ASTRA engine.'}
            onRetry={refetchScans}
          />
        </div>
      )}

      {/* Summary KPI Cards (Rendered for both Data and Empty states with honest values) */}
      {(!scansLoading || hasScans) && !scansError && (
        <>
          <div className="dashboard__stats-grid">
            {/* 1. Total Discovered Assets */}
            <Card variant="glass" className="dashboard__stat-card">
              <div className="dashboard__stat-header">
                <span className="dashboard__stat-label">Total Assets Discovered</span>
                <span className="dashboard__stat-icon" aria-hidden="true">
                  <FileCode size={20} />
                </span>
              </div>
              <div className="dashboard__stat-body">
                <span className="dashboard__stat-value">
                  {hasScans ? totalAssetsDiscovered : '0'}
                </span>
                <span className="dashboard__stat-meta">
                  {hasScans
                    ? `Across ${scans.length} completed scan${scans.length === 1 ? '' : 's'}`
                    : 'No archives scanned yet'}
                </span>
              </div>
            </Card>

            {/* 2. PQC Migration Coverage */}
            <Card variant="glass" className="dashboard__stat-card">
              <div className="dashboard__stat-header">
                <span className="dashboard__stat-label">Post-Quantum Coverage</span>
                <span className="dashboard__stat-icon" aria-hidden="true">
                  <Activity size={20} />
                </span>
              </div>
              <div className="dashboard__stat-body dashboard__stat-body--ring">
                {hasScans && latestCoverage !== null ? (
                  <ProgressRing
                    value={latestCoverage}
                    size={68}
                    strokeWidth={6}
                  />
                ) : (
                  <div className="dashboard__stat-unassessed">
                    <span className="dashboard__stat-value dashboard__stat-value--muted">—</span>
                    <Badge variant="unknown">Unassessed</Badge>
                  </div>
                )}
                <div className="dashboard__stat-ring-info">
                  <span className="dashboard__stat-meta">
                    {hasScans ? 'Latest scan coverage' : 'Requires codebase scan'}
                  </span>
                </div>
              </div>
            </Card>

            {/* 3. Engine Health Status */}
            <Card variant="glass" className="dashboard__stat-card">
              <div className="dashboard__stat-header">
                <span className="dashboard__stat-label">Engine Service</span>
                <span className="dashboard__stat-icon" aria-hidden="true">
                  <Shield size={20} />
                </span>
              </div>
              <div className="dashboard__stat-body">
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                  <Badge variant={isHealthy ? 'safe' : healthLoading ? 'unknown' : 'vulnerable'}>
                    {isHealthy ? 'Online' : healthLoading ? 'Checking...' : 'Unreachable'}
                  </Badge>
                </div>
                <span className="dashboard__stat-meta">
                  Local CPU intake &amp; NIST ruleset
                </span>
              </div>
            </Card>
          </div>

          {/* Actionable Scan Entry Card when empty */}
          {!hasScans ? (
            <div className="dashboard__empty-section">
              <EmptyState
                icon={<UploadCloud size={48} />}
                title="No Cryptographic Scans Yet"
                message="Upload a repository archive (.zip, .tar.gz) to discover algorithms, keys, certificates, and assess quantum migration risk."
                ctaLabel="Start Your First Scan"
                ctaTo="/scan"
              />
            </div>
          ) : (
            /* Recent Scans Table */
            <section className="dashboard__recent-scans">
              <div className="dashboard__section-header">
                <h2 className="dashboard__section-title">Recent Scans</h2>
                <Button
                  as={Link}
                  to="/scan"
                  variant="ghost"
                  size="sm"
                  icon={<ArrowRight size={14} />}
                >
                  Upload Another
                </Button>
              </div>

              <div className="dashboard__table-container">
                <table className="dashboard__table" aria-label="Recent scans table">
                  <thead>
                    <tr>
                      <th scope="col">Target Archive</th>
                      <th scope="col">Scan ID</th>
                      <th scope="col">Date</th>
                      <th scope="col">Assets</th>
                      <th scope="col">PQC Coverage</th>
                      <th scope="col" className="dashboard__table-action-col">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scans.map((scan) => (
                      <tr key={scan.scan_id} className="dashboard__table-row">
                        <td className="dashboard__table-target">
                          <strong>{scan.target_name}</strong>
                        </td>
                        <td>
                          <code className="dashboard__scan-id">{scan.scan_id}</code>
                        </td>
                        <td className="dashboard__table-date">
                          {new Date(scan.created_at).toLocaleString(undefined, {
                            dateStyle: 'medium',
                            timeStyle: 'short',
                          })}
                        </td>
                        <td>
                          <span className="dashboard__asset-count">
                            {scan.asset_count} asset{scan.asset_count === 1 ? '' : 's'}
                          </span>
                        </td>
                        <td>
                          <Badge
                            variant={
                              scan.coverage_percentage >= 80
                                ? 'safe'
                                : scan.coverage_percentage >= 50
                                ? 'medium'
                                : 'high'
                            }
                          >
                            {scan.coverage_percentage}%
                          </Badge>
                        </td>
                        <td className="dashboard__table-action-col">
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => navigate(`/scans/${scan.scan_id}`)}
                          >
                            View
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
