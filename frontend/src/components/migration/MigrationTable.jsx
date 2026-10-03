import React, { useState, useMemo } from 'react';
import Badge from '../common/Badge';
import Button from '../common/Button';
import EmptyState from '../common/EmptyState';
import {
  Search,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  Key,
  ShieldAlert,
  CheckCircle2,
} from 'lucide-react';
import './MigrationTable.css';

const URGENCY_WEIGHTS = {
  CRITICAL: 4,
  HIGH: 3,
  MEDIUM: 2,
  LOW: 1,
  INFORMATIONAL: 1,
  UNASSESSED: 0,
};

/**
 * Reusable Migration Planning & Recommendations Table
 *
 * @param {Object} props
 * @param {Array} [props.tasks=[]]
 * @param {(task: Object) => void} [props.onSelectTask]
 * @param {string} [props.className='']
 */
export default function MigrationTable({
  tasks = [],
  onSelectTask,
  className = '',
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [urgencyFilter, setUrgencyFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [purposeFilter, setPurposeFilter] = useState('ALL');
  const [sortField, setSortField] = useState('urgency');
  const [sortDir, setSortDir] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Extract unique purpose options
  const purposeOptions = useMemo(() => {
    const set = new Set();
    tasks.forEach((t) => {
      if (t.purpose) set.add(t.purpose);
    });
    return Array.from(set).sort();
  }, [tasks]);

  // Extract unique status options
  const statusOptions = useMemo(() => {
    const set = new Set();
    tasks.forEach((t) => {
      if (t.status) set.add(t.status);
    });
    return Array.from(set).sort();
  }, [tasks]);

  // Filter tasks
  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      // 1. Urgency Filter
      if (urgencyFilter !== 'ALL') {
        const itemPrio = task.priority ? String(task.priority).toUpperCase() : 'UNASSESSED';
        if (itemPrio !== urgencyFilter) return false;
      }

      // 2. Status Filter
      if (statusFilter !== 'ALL') {
        const itemStatus = task.status ? String(task.status).toUpperCase() : 'OPEN';
        if (itemStatus !== statusFilter) return false;
      }

      // 3. Purpose Filter
      if (purposeFilter !== 'ALL' && task.purpose !== purposeFilter) {
        return false;
      }

      // 4. Search term
      if (searchTerm.trim()) {
        const q = searchTerm.toLowerCase();
        const currentAlgo = (task.current_algorithm || '').toLowerCase();
        const targetAlgo = (task.target_pqc_algorithm || '').toLowerCase();
        const hybridAlgo = (task.target_hybrid_algorithm || '').toLowerCase();
        const assetId = (task.asset_id || '').toLowerCase();
        const path = (task.relative_path || '').toLowerCase();
        const standard = (task.dated_standard_ref || '').toLowerCase();
        const action = (task.recommended_action || '').toLowerCase();
        const purpose = (task.purpose || '').toLowerCase();

        const matches =
          currentAlgo.includes(q) ||
          targetAlgo.includes(q) ||
          hybridAlgo.includes(q) ||
          assetId.includes(q) ||
          path.includes(q) ||
          standard.includes(q) ||
          action.includes(q) ||
          purpose.includes(q);

        if (!matches) return false;
      }

      return true;
    });
  }, [tasks, urgencyFilter, statusFilter, purposeFilter, searchTerm]);

  // Sort tasks
  const sortedTasks = useMemo(() => {
    const list = [...filteredTasks];
    list.sort((a, b) => {
      let comparison = 0;

      if (sortField === 'urgency') {
        const weightA = URGENCY_WEIGHTS[a.priority?.toUpperCase()] ?? 0;
        const weightB = URGENCY_WEIGHTS[b.priority?.toUpperCase()] ?? 0;
        comparison = weightA - weightB;
        if (comparison === 0) {
          comparison = (a.composite_risk_score || 0) - (b.composite_risk_score || 0);
        }
      } else if (sortField === 'currentAlgo') {
        comparison = (a.current_algorithm || '').localeCompare(b.current_algorithm || '');
      } else if (sortField === 'targetAlgo') {
        comparison = (a.target_pqc_algorithm || '').localeCompare(b.target_pqc_algorithm || '');
      } else if (sortField === 'location') {
        comparison = (a.relative_path || '').localeCompare(b.relative_path || '');
      } else if (sortField === 'riskScore') {
        comparison = (a.composite_risk_score || 0) - (b.composite_risk_score || 0);
      }

      return sortDir === 'asc' ? comparison : -comparison;
    });
    return list;
  }, [filteredTasks, sortField, sortDir]);

  // Pagination
  const totalPages = Math.max(1, Math.ceil(sortedTasks.length / pageSize));
  const paginatedTasks = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedTasks.slice(start, start + pageSize);
  }, [sortedTasks, currentPage, pageSize]);

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  const handleUrgencyChange = (val) => {
    setUrgencyFilter(val);
    setCurrentPage(1);
  };

  const handleStatusChange = (val) => {
    setStatusFilter(val);
    setCurrentPage(1);
  };

  const handlePurposeChange = (val) => {
    setPurposeFilter(val);
    setCurrentPage(1);
  };

  const handleResetFilters = () => {
    setSearchTerm('');
    setUrgencyFilter('ALL');
    setStatusFilter('ALL');
    setPurposeFilter('ALL');
    setCurrentPage(1);
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDir('asc');
    }
  };

  const getSortIcon = (field) => {
    if (sortField !== field) {
      return <ArrowUpDown size={14} className="mig-sort-icon mig-sort-icon--inactive" aria-hidden="true" />;
    }
    return sortDir === 'asc' ? (
      <ArrowUp size={14} className="mig-sort-icon mig-sort-icon--active" aria-hidden="true" />
    ) : (
      <ArrowDown size={14} className="mig-sort-icon mig-sort-icon--active" aria-hidden="true" />
    );
  };

  return (
    <div className={`migration-table-container ${className}`} data-testid="migration-table">
      {/* Search & Filter Controls */}
      <div className="migration-table-controls">
        <div className="migration-search-box">
          <Search size={16} className="migration-search-icon" aria-hidden="true" />
          <input
            type="text"
            placeholder="Search recommendations by algorithm, target, path, asset, or standard..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="migration-search-input"
            aria-label="Search migration recommendations"
            data-testid="migration-search-input"
          />
          {searchTerm && (
            <button
              type="button"
              className="migration-search-clear"
              onClick={() => {
                setSearchTerm('');
                setCurrentPage(1);
              }}
              aria-label="Clear migration search query"
            >
              ×
            </button>
          )}
        </div>

        <div className="migration-filters-group">
          {/* Urgency Filter */}
          <div className="migration-select-wrapper">
            <ShieldAlert size={14} className="migration-select-icon" aria-hidden="true" />
            <select
              value={urgencyFilter}
              onChange={(e) => handleUrgencyChange(e.target.value)}
              className="migration-select"
              aria-label="Filter by Migration Urgency"
              data-testid="migration-urgency-filter"
            >
              <option value="ALL">All Urgencies</option>
              <option value="CRITICAL">Critical Priority</option>
              <option value="HIGH">High Priority</option>
              <option value="MEDIUM">Medium Priority</option>
              <option value="LOW">Low Priority</option>
              <option value="INFORMATIONAL">Informational</option>
            </select>
          </div>

          {/* Status Filter */}
          <div className="migration-select-wrapper">
            <CheckCircle2 size={14} className="migration-select-icon" aria-hidden="true" />
            <select
              value={statusFilter}
              onChange={(e) => handleStatusChange(e.target.value)}
              className="migration-select"
              aria-label="Filter by Migration Status"
              data-testid="migration-status-filter"
            >
              <option value="ALL">All Statuses</option>
              {statusOptions.map((st) => (
                <option key={st} value={st}>
                  {st.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          {/* Purpose Filter */}
          <div className="migration-select-wrapper">
            <Key size={14} className="migration-select-icon" aria-hidden="true" />
            <select
              value={purposeFilter}
              onChange={(e) => handlePurposeChange(e.target.value)}
              className="migration-select"
              aria-label="Filter by Cryptographic Purpose"
              data-testid="migration-purpose-filter"
            >
              <option value="ALL">All Purposes</option>
              {purposeOptions.map((p) => (
                <option key={p} value={p}>
                  {p.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          {(searchTerm || urgencyFilter !== 'ALL' || statusFilter !== 'ALL' || purposeFilter !== 'ALL') && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleResetFilters}
              data-testid="migration-reset-filters-btn"
            >
              Reset
            </Button>
          )}
        </div>
      </div>

      {/* Table Content */}
      {paginatedTasks.length === 0 ? (
        <div className="migration-table-empty">
          <EmptyState
            title="No Migration Recommendations Match Criteria"
            message={
              tasks.length === 0
                ? 'No migration tasks or recommendations were generated for this scan.'
                : 'Try adjusting your search query, priority filter, or status filter.'
            }
            ctaLabel={tasks.length > 0 ? 'Reset Filters' : undefined}
            onCta={tasks.length > 0 ? handleResetFilters : undefined}
          />
        </div>
      ) : (
        <div className="migration-table-scroll">
          <table className="migration-table" aria-label="Cryptographic Migration Recommendations">
            <thead>
              <tr>
                <th scope="col" className="col-mig-pathway">
                  <button
                    type="button"
                    className="th-mig-button"
                    onClick={() => handleSort('currentAlgo')}
                  >
                    <span>Current Algorithm & Migration Target</span>
                    {getSortIcon('currentAlgo')}
                  </button>
                </th>
                <th scope="col" className="col-mig-location">
                  <button
                    type="button"
                    className="th-mig-button"
                    onClick={() => handleSort('location')}
                  >
                    <span>Location & Asset</span>
                    {getSortIcon('location')}
                  </button>
                </th>
                <th scope="col" className="col-mig-standard">
                  <span>Standard Reference</span>
                </th>
                <th scope="col" className="col-mig-urgency">
                  <button
                    type="button"
                    className="th-mig-button"
                    onClick={() => handleSort('urgency')}
                  >
                    <span>Urgency & Risk</span>
                    {getSortIcon('urgency')}
                  </button>
                </th>
                <th scope="col" className="col-mig-status">
                  <span>Status</span>
                </th>
                <th scope="col" className="col-mig-action">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {paginatedTasks.map((task, idx) => {
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

                const statusStr = task.status ? String(task.status).toUpperCase() : 'OPEN';
                const statusVariant =
                  statusStr === 'ACCEPTED' || statusStr === 'COMPLETED'
                    ? 'safe'
                    : statusStr === 'IN_REVIEW'
                    ? 'medium'
                    : 'primary';

                return (
                  <tr
                    key={task.task_id || `mig-row-${idx}`}
                    className="migration-table-row"
                    data-testid={`migration-row-${task.task_id || idx}`}
                    onClick={() => onSelectTask && onSelectTask(task)}
                    tabIndex={0}
                    role="button"
                    aria-label={`Inspect migration recommendation for ${task.current_algorithm}`}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        if (onSelectTask) onSelectTask(task);
                      }
                    }}
                  >
                    <td className="col-mig-pathway">
                      <div className="mig-pathway-cell">
                        <div className="mig-algo-transition-row">
                          <span className="mig-curr-algo">{task.current_algorithm}</span>
                          <ArrowRight size={14} className="mig-arrow-icon" aria-hidden="true" />
                          <span className="mig-target-algo" title={task.target_pqc_algorithm}>
                            {task.target_pqc_algorithm || 'Advisory Review'}
                          </span>
                        </div>
                        {task.target_hybrid_algorithm && (
                          <div className="mig-hybrid-row">
                            <span className="mig-hybrid-label">Hybrid:</span>
                            <span className="mig-hybrid-text">{task.target_hybrid_algorithm}</span>
                          </div>
                        )}
                        <span className="mig-purpose-tag">{task.purpose || 'CRYPTOGRAPHY'}</span>
                      </div>
                    </td>

                    <td className="col-mig-location">
                      <div className="mig-location-cell">
                        <span className="mig-path-text" title={task.relative_path}>
                          {task.relative_path || 'Unknown location'}
                          {task.start_line && <span className="mig-line-tag">:{task.start_line}</span>}
                        </span>
                        <code className="mig-asset-code" title={task.asset_id}>
                          {task.asset_id || 'unidentified-asset'}
                        </code>
                      </div>
                    </td>

                    <td className="col-mig-standard">
                      <div className="mig-standard-cell">
                        <span className="mig-standard-text" title={task.dated_standard_ref}>
                          {task.dated_standard_ref || 'N/A (Standard Authority)'}
                        </span>
                        {task.compatibility_gaps?.length > 0 && (
                          <span className="mig-gaps-badge">
                            {task.compatibility_gaps.length} Caveat{task.compatibility_gaps.length > 1 ? 's' : ''}
                          </span>
                        )}
                      </div>
                    </td>

                    <td className="col-mig-urgency">
                      <div className="mig-urgency-cell">
                        <Badge variant={prioVariant}>{prio}</Badge>
                        {typeof task.composite_risk_score === 'number' && (
                          <span className="mig-score-subtext">
                            Score: <strong>{task.composite_risk_score.toFixed(1)}</strong>
                          </span>
                        )}
                      </div>
                    </td>

                    <td className="col-mig-status">
                      <Badge variant={statusVariant}>{statusStr.replace(/_/g, ' ')}</Badge>
                    </td>

                    <td className="col-mig-action">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onSelectTask) onSelectTask(task);
                        }}
                        aria-label={`Inspect recommendation for ${task.current_algorithm}`}
                      >
                        Inspect
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination Footer */}
      {filteredTasks.length > 0 && (
        <div className="migration-pagination" role="navigation" aria-label="Migration Recommendations Pagination">
          <div className="migration-pagination-info">
            Showing <strong>{(currentPage - 1) * pageSize + 1}</strong> to{' '}
            <strong>{Math.min(currentPage * pageSize, filteredTasks.length)}</strong> of{' '}
            <strong>{filteredTasks.length}</strong> recommendations
          </div>

          <div className="migration-pagination-controls">
            <div className="migration-page-size-selector">
              <label htmlFor="mig-page-size-select" className="migration-page-size-label">
                Per page:
              </label>
              <select
                id="mig-page-size-select"
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="migration-page-size-select"
                aria-label="Recommendations per page"
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </div>

            <Button
              variant="outline"
              size="sm"
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              aria-label="Previous recommendations page"
            >
              <ChevronLeft size={16} aria-hidden="true" />
              <span>Prev</span>
            </Button>

            <span className="migration-page-counter">
              Page <strong>{currentPage}</strong> of <strong>{totalPages}</strong>
            </span>

            <Button
              variant="outline"
              size="sm"
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              aria-label="Next recommendations page"
            >
              <span>Next</span>
              <ChevronRight size={16} aria-hidden="true" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
