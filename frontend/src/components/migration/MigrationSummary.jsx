import React from 'react';
import Card from '../common/Card';
import Badge from '../common/Badge';
import {
  GitFork,
  AlertTriangle,
  CheckCircle2,
  Info,
  Sparkles,
} from 'lucide-react';
import './MigrationSummary.css';

/**
 * Migration Planning Summary & Metrics Overview
 *
 * @param {Object} props
 * @param {Array} [props.tasks=[]]
 * @param {Object} [props.scan=null]
 * @param {string} [props.className='']
 */
export default function MigrationSummary({
  tasks = [],
  scan = null,
  className = '',
}) {
  const items = Array.isArray(tasks) ? tasks : [];
  const totalTasks = items.length;

  // Counts by priority / urgency
  let criticalCount = 0;
  let highCount = 0;

  // PQC target identified count
  let pqcTargetIdentifiedCount = 0;

  // Status counts
  let openCount = 0;
  let inReviewCount = 0;
  let acceptedCount = 0;

  const affectedAssets = new Set();

  items.forEach((task) => {
    if (task.asset_id) affectedAssets.add(task.asset_id);

    const prio = task.priority ? String(task.priority).toUpperCase() : 'UNASSESSED';
    if (prio === 'CRITICAL') criticalCount += 1;
    else if (prio === 'HIGH') highCount += 1;

    if (
      task.target_pqc_algorithm &&
      !task.target_pqc_algorithm.toLowerCase().includes('n/a') &&
      !task.target_pqc_algorithm.toLowerCase().includes('unknown')
    ) {
      pqcTargetIdentifiedCount += 1;
    }

    const st = task.status ? String(task.status).toUpperCase() : 'OPEN';
    if (st === 'OPEN') openCount += 1;
    else if (st === 'IN_REVIEW') inReviewCount += 1;
    else if (st === 'ACCEPTED') acceptedCount += 1;
  });

  const targetName = scan?.target_name || scan?.manifest?.archive_name || 'Software Target';

  return (
    <div className={`migration-summary-container ${className}`} data-testid="migration-summary">
      {/* Metrics Row */}
      <div className="migration-metrics-grid" role="region" aria-label="Migration Planning Overview">
        {/* Total Actionable Tasks */}
        <Card className="migration-metric-card">
          <div className="migration-metric-inner">
            <div className="migration-metric-text">
              <span className="migration-metric-label">Migration Recommendations</span>
              <span className="migration-metric-number" data-testid="total-migration-tasks">
                {totalTasks}
              </span>
              <span className="migration-metric-subtext" data-testid="affected-assets-subtext">
                Across <strong>{affectedAssets.size}</strong> affected assets
              </span>
            </div>
            <div className="migration-metric-icon-box" aria-hidden="true">
              <GitFork size={28} className="migration-icon-primary" />
            </div>
          </div>
        </Card>

        {/* High & Critical Urgency */}
        <Card className="migration-metric-card">
          <div className="migration-metric-inner">
            <div className="migration-metric-text">
              <span className="migration-metric-label">Urgent Pathways</span>
              <span className="migration-metric-number migration-color-rose" data-testid="urgent-migration-tasks">
                {criticalCount + highCount}
              </span>
              <span className="migration-metric-subtext">
                {criticalCount} Critical • {highCount} High priority
              </span>
            </div>
            <div className="migration-metric-icon-box" aria-hidden="true">
              <AlertTriangle size={28} className="migration-color-rose" />
            </div>
          </div>
        </Card>

        {/* PQC Target Candidates */}
        <Card className="migration-metric-card">
          <div className="migration-metric-inner">
            <div className="migration-metric-text">
              <span className="migration-metric-label">Standardized PQC Targets</span>
              <span className="migration-metric-number migration-color-cyan" data-testid="pqc-targets-count">
                {pqcTargetIdentifiedCount}
              </span>
              <span className="migration-metric-subtext">
                NIST FIPS 203/204/205 & Hybrid
              </span>
            </div>
            <div className="migration-metric-icon-box" aria-hidden="true">
              <Sparkles size={28} className="migration-color-cyan" />
            </div>
          </div>
        </Card>

        {/* Workflow State */}
        <Card className="migration-metric-card">
          <div className="migration-metric-inner">
            <div className="migration-metric-text">
              <span className="migration-metric-label">Review Status</span>
              <div className="migration-status-mini-row">
                <Badge variant="primary">Open: {openCount}</Badge>
                {inReviewCount > 0 && <Badge variant="medium">In Review: {inReviewCount}</Badge>}
                {acceptedCount > 0 && <Badge variant="safe">Accepted: {acceptedCount}</Badge>}
              </div>
              <span className="migration-metric-subtext" style={{ marginTop: '4px' }}>
                Architecture team queue
              </span>
            </div>
            <div className="migration-metric-icon-box" aria-hidden="true">
              <CheckCircle2 size={28} className="migration-color-emerald" />
            </div>
          </div>
        </Card>
      </div>

      {/* Critical Truthfulness & No-Remediation Notice */}
      <div className="migration-remediation-banner" role="region" aria-label="Advisory Notice">
        <Info size={18} className="migration-banner-icon" aria-hidden="true" />
        <div className="migration-banner-content">
          <strong>Advisory Candidate Recommendations Only (No Automatic Code Remediation):</strong>{' '}
          All migration pathways and target replacement algorithms displayed for <em>{targetName}</em> represent
          advisory technical options derived from official dated standards (NIST FIPS 203, FIPS 204, FIPS 205, FIPS 180-4).
          ASTRA performs analysis and planning only; it does <strong>NOT</strong> execute code modifications, key rotations, or certificate swaps automatically.
          Environmental benchmarking for latency, memory overhead, and packet fragmentation (MTU) must be validated by engineering teams prior to deployment.
        </div>
      </div>
    </div>
  );
}
