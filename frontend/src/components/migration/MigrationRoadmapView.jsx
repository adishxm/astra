import React, { useMemo } from 'react';
import Card from '../common/Card';
import Badge from '../common/Badge';
import {
  Layers,
  Clock,
  ArrowRight,
  FileCode,
  Package,
  Network,
} from 'lucide-react';
import './MigrationRoadmapView.css';

/**
 * Categorize a task into an execution phase based on purpose and surface
 * @param {Object} task
 * @returns {number} 1, 2, or 3
 */
export function getTaskPhase(task) {
  const p = (task.purpose || '').toUpperCase();
  const algo = (task.current_algorithm || '').toUpperCase();
  const path = (task.relative_path || '').toLowerCase();

  // Phase 1: Foundational Libraries, Certificates, Hashing, Manifests
  if (
    p.includes('LIBRARY') ||
    p.includes('IDENTITY') ||
    p.includes('AUTHENTICATION') ||
    p.includes('HASH') ||
    algo.includes('MD5') ||
    algo.includes('SHA') ||
    path.endsWith('.pem') ||
    path.endsWith('.crt') ||
    path.includes('package.json')
  ) {
    return 1;
  }

  // Phase 2: Core Platform Services, KEX, TLS Configurations, Ciphers
  if (
    p.includes('KEY_EXCHANGE') ||
    p.includes('PROTOCOL') ||
    p.includes('CIPHER_SUITE') ||
    p.includes('SYMMETRIC') ||
    p.includes('ENCRYPTION') ||
    path.endsWith('.conf') ||
    path.endsWith('.yaml') ||
    path.endsWith('.yml')
  ) {
    return 2;
  }

  // Phase 3: Application-level code & remaining endpoints
  return 3;
}

const PHASE_METADATA = {
  1: {
    number: 1,
    title: 'Phase 1: Foundational Cryptographic Libraries & Trust Anchors',
    description: 'Upgrade root dependencies, replace broken hashing (MD5), and establish post-quantum PKI roots.',
    icon: <Package size={18} className="phase-header-icon phase-color-emerald" aria-hidden="true" />,
    badgeVariant: 'safe',
  },
  2: {
    number: 2,
    title: 'Phase 2: Core Platform Services & Internal Gateways',
    description: 'Transition TLS configurations, cipher suites, and key encapsulation (KEM) in ingress proxies.',
    icon: <Network size={18} className="phase-header-icon phase-color-cyan" aria-hidden="true" />,
    badgeVariant: 'primary',
  },
  3: {
    number: 3,
    title: 'Phase 3: Application-Level & Edge Cryptographic Endpoints',
    description: 'Migrate application-level asymmetric encryption, digital signatures (ML-DSA), and proprietary crypto calls.',
    icon: <FileCode size={18} className="phase-header-icon phase-color-purple" aria-hidden="true" />,
    badgeVariant: 'medium',
  },
};

/**
 * Dependency-Aware Phased Migration Roadmap View
 *
 * @param {Object} props
 * @param {Array} [props.tasks=[]]
 * @param {(task: Object) => void} [props.onSelectTask]
 * @param {string} [props.className='']
 */
export default function MigrationRoadmapView({
  tasks = [],
  onSelectTask,
  className = '',
}) {
  const phasedData = useMemo(() => {
    const map = { 1: [], 2: [], 3: [] };

    tasks.forEach((task) => {
      const phaseNum = getTaskPhase(task);
      map[phaseNum].push(task);
    });

    return [1, 2, 3].map((num) => ({
      ...PHASE_METADATA[num],
      tasks: map[num],
      totalEffortDays: (map[num].length * 3.5).toFixed(1),
    }));
  }, [tasks]);

  if (tasks.length === 0) {
    return null;
  }

  return (
    <Card className={`migration-roadmap-card ${className}`} data-testid="migration-roadmap-view">
      <div className="roadmap-header">
        <div className="roadmap-title-group">
          <Layers size={18} className="roadmap-title-icon" aria-hidden="true" />
          <h3 className="roadmap-title">Dependency-Aware Phased Migration Roadmap</h3>
        </div>
        <span className="roadmap-badge">Topological Scheduling</span>
      </div>

      <p className="roadmap-subtitle">
        Phased migration plan structured to eliminate prerequisite blocking dependencies before deploying application-level changes.
      </p>

      <div className="roadmap-phases-grid">
        {phasedData.map((phase) => (
          <div
            key={phase.number}
            className="phase-column"
            data-testid={`migration-phase-${phase.number}`}
          >
            <div className="phase-header">
              <div className="phase-title-row">
                {phase.icon}
                <span className="phase-title-text">{phase.title}</span>
              </div>
              <p className="phase-description">{phase.description}</p>
              <div className="phase-meta-tags">
                <span className="phase-items-count">
                  <strong>{phase.tasks.length}</strong> tasks
                </span>
                <span className="phase-effort-tag">
                  <Clock size={12} aria-hidden="true" />
                  ~{phase.totalEffortDays} engineer-days
                </span>
              </div>
            </div>

            <div className="phase-tasks-list">
              {phase.tasks.length === 0 ? (
                <div className="phase-empty-box">No components assigned to this phase.</div>
              ) : (
                phase.tasks.slice(0, 5).map((task) => {
                  const prio = task.priority ? String(task.priority).toUpperCase() : 'UNASSESSED';
                  const prioVariant =
                    prio === 'CRITICAL'
                      ? 'critical'
                      : prio === 'HIGH'
                      ? 'high'
                      : prio === 'MEDIUM'
                      ? 'medium'
                      : prio === 'LOW'
                      ? 'low'
                      : 'neutral';

                  return (
                    <div
                      key={task.task_id}
                      className="phase-task-card"
                      role="button"
                      tabIndex={0}
                      onClick={() => onSelectTask && onSelectTask(task)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          if (onSelectTask) onSelectTask(task);
                        }
                      }}
                      data-testid={`phase-task-${task.task_id}`}
                      aria-label={`Inspect migration task for ${task.current_algorithm}`}
                    >
                      <div className="phase-task-top">
                        <span className="phase-task-algo">{task.current_algorithm}</span>
                        <Badge variant={prioVariant}>{prio}</Badge>
                      </div>

                      <div className="phase-task-path" title={task.relative_path}>
                        <code>
                          {task.relative_path}
                          {task.start_line ? `:${task.start_line}` : ''}
                        </code>
                      </div>

                      <div className="phase-task-transition">
                        <ArrowRight size={12} className="transition-arrow" aria-hidden="true" />
                        <span className="phase-target-algo" title={task.target_pqc_algorithm}>
                          {task.target_pqc_algorithm || 'Review Architecture'}
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
              {phase.tasks.length > 5 && (
                <div className="phase-more-footer">
                  + {phase.tasks.length - 5} more components in {phase.title.split(':')[0]}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
