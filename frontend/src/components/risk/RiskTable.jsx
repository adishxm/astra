import React, { useState, useMemo } from 'react';
import Badge from '../common/Badge';
import Button from '../common/Button';
import EmptyState from '../common/EmptyState';
import {
  Search,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Clock,
  AlertOctagon,
  ChevronLeft,
  ChevronRight,
  Filter,
} from 'lucide-react';
import './RiskTable.css';

const URGENCY_WEIGHTS = {
  CRITICAL: 4,
  HIGH: 3,
  MEDIUM: 2,
  LOW: 1,
  UNASSESSED: 0,
};

/**
 * Formats risk score accurately without modifying or recalculating.
 * @param {number|null|undefined} score
 * @returns {string}
 */
export function formatRiskScore(score) {
  if (typeof score !== 'number' || Number.isNaN(score)) {
    return 'Unassessed';
  }
  return score.toFixed(2);
}

/**
 * Formats a reason code into a human-readable tag.
 * @param {string} code
 * @returns {string}
 */
export function formatReasonCode(code) {
  if (!code) return 'Standard Evaluation';
  return String(code).replace(/^RC_/, '').replace(/_/g, ' ');
}

/**
 * Risk Assessment Table Component
 *
 * @param {Object} props
 * @param {Array} [props.riskEvaluations=[]]
 * @param {Array} [props.backlogItems=[]]
 * @param {(item: Object) => void} [props.onSelectRisk]
 * @param {boolean} [props.showSearch=true]
 * @param {boolean} [props.showFilters=true]
 * @param {string} [props.initialUrgencyFilter='ALL']
 * @param {string} [props.className='']
 */
export default function RiskTable({
  riskEvaluations = [],
  backlogItems = [],
  onSelectRisk,
  showSearch = true,
  showFilters = true,
  initialUrgencyFilter = 'ALL',
  className = '',
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [urgencyFilter, setUrgencyFilter] = useState(initialUrgencyFilter);
  const [moscaFilter, setMoscaFilter] = useState('ALL');
  const [sortField, setSortField] = useState('risk_score');
  const [sortDir, setSortDir] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Map backlog recommendations by asset_id for quick cross-reference
  const backlogMap = useMemo(() => {
    const map = new Map();
    if (Array.isArray(backlogItems)) {
      backlogItems.forEach((b) => {
        if (b?.asset_id) {
          map.set(b.asset_id, b);
        }
      });
    }
    return map;
  }, [backlogItems]);

  // Filter evaluations
  const filteredItems = useMemo(() => {
    if (!Array.isArray(riskEvaluations)) return [];

    return riskEvaluations.filter((item) => {
      if (!item) return false;

      // 1. Urgency filter
      const itemUrgency = (item.urgency ? String(item.urgency).toUpperCase() : 'UNASSESSED');
      if (urgencyFilter !== 'ALL') {
        if (urgencyFilter === 'UNASSESSED') {
          const isUnassessed =
            itemUrgency === 'UNASSESSED' ||
            typeof item.risk_score !== 'number' ||
            Number.isNaN(item.risk_score);
          if (!isUnassessed) return false;
        } else if (itemUrgency !== urgencyFilter) {
          return false;
        }
      }

      // 2. Mosca filter
      if (moscaFilter === 'VIOLATED' && !item.mosca_condition_violated) {
        return false;
      }
      if (moscaFilter === 'COMPLIANT' && item.mosca_condition_violated) {
        return false;
      }

      // 3. Search query
      if (searchTerm.trim()) {
        const query = searchTerm.toLowerCase();
        const assetId = (item.asset_id || '').toLowerCase();
        const algorithm = (item.algorithm || '').toLowerCase();
        const purpose = (item.purpose || '').toLowerCase();
        const reasonCodes = Array.isArray(item.reason_codes)
          ? item.reason_codes.join(' ').toLowerCase()
          : '';

        const matches =
          assetId.includes(query) ||
          algorithm.includes(query) ||
          purpose.includes(query) ||
          reasonCodes.includes(query);

        if (!matches) return false;
      }

      return true;
    });
  }, [riskEvaluations, urgencyFilter, moscaFilter, searchTerm]);

  // Sort items
  const sortedItems = useMemo(() => {
    const items = [...filteredItems];
    items.sort((a, b) => {
      let comparison = 0;

      if (sortField === 'risk_score') {
        const scoreA = typeof a.risk_score === 'number' ? a.risk_score : -1;
        const scoreB = typeof b.risk_score === 'number' ? b.risk_score : -1;
        comparison = scoreA - scoreB;
      } else if (sortField === 'urgency') {
        const urgA = URGENCY_WEIGHTS[a.urgency?.toUpperCase()] ?? 0;
        const urgB = URGENCY_WEIGHTS[b.urgency?.toUpperCase()] ?? 0;
        comparison = urgA - urgB;
      } else if (sortField === 'algorithm') {
        const algA = a.algorithm || '';
        const algB = b.algorithm || '';
        comparison = algA.localeCompare(algB);
      } else if (sortField === 'mosca_slack') {
        const slackA = typeof a.mosca_slack_years === 'number' ? a.mosca_slack_years : 999;
        const slackB = typeof b.mosca_slack_years === 'number' ? b.mosca_slack_years : 999;
        comparison = slackA - slackB;
      }

      return sortDir === 'asc' ? comparison : -comparison;
    });
    return items;
  }, [filteredItems, sortField, sortDir]);

  // Pagination
  const totalPages = Math.max(1, Math.ceil(sortedItems.length / pageSize));
  const paginatedItems = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedItems.slice(start, start + pageSize);
  }, [sortedItems, currentPage, pageSize]);

  // Reset pagination when filter/search changes
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  const handleUrgencyChange = (val) => {
    setUrgencyFilter(val);
    setCurrentPage(1);
  };

  const handleMoscaChange = (val) => {
    setMoscaFilter(val);
    setCurrentPage(1);
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDir('desc');
    }
  };

  const handleResetFilters = () => {
    setSearchTerm('');
    setUrgencyFilter('ALL');
    setMoscaFilter('ALL');
    setCurrentPage(1);
  };

  const getSortIcon = (field) => {
    if (sortField !== field) {
      return <ArrowUpDown size={14} className="sort-icon sort-icon--inactive" aria-hidden="true" />;
    }
    return sortDir === 'asc' ? (
      <ArrowUp size={14} className="sort-icon sort-icon--active" aria-hidden="true" />
    ) : (
      <ArrowDown size={14} className="sort-icon sort-icon--active" aria-hidden="true" />
    );
  };

  return (
    <div className={`risk-table-container ${className}`} data-testid="risk-table-container">
      {/* Controls Bar: Search & Filters */}
      {(showSearch || showFilters) && (
        <div className="risk-table-controls">
          {showSearch && (
            <div className="risk-search-box">
              <Search size={16} className="risk-search-icon" aria-hidden="true" />
              <input
                type="text"
                placeholder="Filter by asset ID, algorithm, purpose, or reason code..."
                value={searchTerm}
                onChange={handleSearchChange}
                className="risk-search-input"
                aria-label="Filter risk evaluations"
                data-testid="risk-search-input"
              />
              {searchTerm && (
                <button
                  type="button"
                  className="risk-search-clear"
                  onClick={() => {
                    setSearchTerm('');
                    setCurrentPage(1);
                  }}
                  aria-label="Clear search query"
                >
                  ×
                </button>
              )}
            </div>
          )}

          {showFilters && (
            <div className="risk-filters-group">
              {/* Urgency Filter */}
              <div className="filter-select-wrapper">
                <Filter size={14} className="filter-select-icon" aria-hidden="true" />
                <select
                  value={urgencyFilter}
                  onChange={(e) => handleUrgencyChange(e.target.value)}
                  className="risk-select"
                  aria-label="Filter by Urgency"
                  data-testid="urgency-filter-select"
                >
                  <option value="ALL">All Urgencies</option>
                  <option value="CRITICAL">Critical</option>
                  <option value="HIGH">High</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="LOW">Low</option>
                  <option value="UNASSESSED">Unassessed / Missing</option>
                </select>
              </div>

              {/* Mosca Filter */}
              <div className="filter-select-wrapper">
                <Clock size={14} className="filter-select-icon" aria-hidden="true" />
                <select
                  value={moscaFilter}
                  onChange={(e) => handleMoscaChange(e.target.value)}
                  className="risk-select"
                  aria-label="Filter by Mosca Timeline Status"
                  data-testid="mosca-filter-select"
                >
                  <option value="ALL">All Mosca Timelines</option>
                  <option value="VIOLATED">Mosca Violated (SNDL Risk)</option>
                  <option value="COMPLIANT">Mosca Compliant</option>
                </select>
              </div>

              {(searchTerm || urgencyFilter !== 'ALL' || moscaFilter !== 'ALL') && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleResetFilters}
                  data-testid="reset-filters-button"
                >
                  Reset
                </Button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Table Content */}
      {paginatedItems.length === 0 ? (
        <div className="risk-table-empty">
          <EmptyState
            title="No Risk Evaluations Match Filters"
            message={
              riskEvaluations.length === 0
                ? 'No risk assessment records are available for this scan.'
                : 'Try adjusting your search query, urgency filter, or Mosca timeline criteria.'
            }
            ctaLabel={riskEvaluations.length > 0 ? 'Reset Filters' : undefined}
            onCta={riskEvaluations.length > 0 ? handleResetFilters : undefined}
          />
        </div>
      ) : (
        <div className="risk-table-scroll">
          <table className="risk-table" aria-label="Risk Assessment Evaluations">
            <thead>
              <tr>
                <th scope="col" className="col-asset">
                  <button
                    type="button"
                    className="th-sort-button"
                    onClick={() => handleSort('algorithm')}
                  >
                    <span>Asset & Algorithm</span>
                    {getSortIcon('algorithm')}
                  </button>
                </th>
                <th scope="col" className="col-score">
                  <button
                    type="button"
                    className="th-sort-button"
                    onClick={() => handleSort('risk_score')}
                  >
                    <span>Risk Score</span>
                    {getSortIcon('risk_score')}
                  </button>
                </th>
                <th scope="col" className="col-urgency">
                  <button
                    type="button"
                    className="th-sort-button"
                    onClick={() => handleSort('urgency')}
                  >
                    <span>Urgency</span>
                    {getSortIcon('urgency')}
                  </button>
                </th>
                <th scope="col" className="col-mosca">
                  <button
                    type="button"
                    className="th-sort-button"
                    onClick={() => handleSort('mosca_slack')}
                  >
                    <span>Mosca Slack</span>
                    {getSortIcon('mosca_slack')}
                  </button>
                </th>
                <th scope="col" className="col-reasons">
                  <span>Primary Reason</span>
                </th>
                <th scope="col" className="col-action">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {paginatedItems.map((item, idx) => {
                const hasScore = typeof item.risk_score === 'number' && !Number.isNaN(item.risk_score);
                const urgency = (item.urgency ? String(item.urgency).toUpperCase() : 'UNASSESSED');
                const isUnassessed = urgency === 'UNASSESSED' || !hasScore;
                const isViolated = item.mosca_condition_violated === true;
                const slack = item.mosca_slack_years;
                const primaryReason = Array.isArray(item.reason_codes) && item.reason_codes.length > 0
                  ? item.reason_codes[0]
                  : null;
                const matchingBacklog = backlogMap.get(item.asset_id);

                return (
                  <tr
                    key={item.asset_id || `risk-row-${idx}`}
                    className="risk-table-row"
                    data-testid={`risk-row-${item.asset_id || idx}`}
                    onClick={() => onSelectRisk && onSelectRisk({ ...item, backlogItem: matchingBacklog })}
                    tabIndex={0}
                    role="button"
                    aria-label={`Inspect risk for ${item.algorithm || item.asset_id}`}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        if (onSelectRisk) onSelectRisk({ ...item, backlogItem: matchingBacklog });
                      }
                    }}
                  >
                    <td className="col-asset">
                      <div className="asset-cell-content">
                        <span className="asset-algo-title">
                          {item.algorithm || 'Unknown Algorithm'}
                        </span>
                        <div className="asset-id-row">
                          <code className="asset-id-code" title={item.asset_id}>
                            {item.asset_id || 'unidentified-asset'}
                          </code>
                          {item.purpose && (
                            <span className="asset-purpose-tag">{item.purpose}</span>
                          )}
                        </div>
                      </div>
                    </td>

                    <td className="col-score">
                      <div className="score-cell-content">
                        {hasScore ? (
                          <span
                            className={`risk-score-pill ${
                              item.risk_score >= 70
                                ? 'score-pill--high'
                                : item.risk_score >= 40
                                ? 'score-pill--medium'
                                : 'score-pill--low'
                            }`}
                          >
                            {formatRiskScore(item.risk_score)}
                          </span>
                        ) : (
                          <span className="score-unassessed-tag">Unassessed</span>
                        )}
                      </div>
                    </td>

                    <td className="col-urgency">
                      <Badge
                        variant={
                          isUnassessed
                            ? 'unknown'
                            : urgency === 'CRITICAL'
                            ? 'critical'
                            : urgency === 'HIGH'
                            ? 'high'
                            : urgency === 'MEDIUM'
                            ? 'medium'
                            : 'low'
                        }
                      >
                        {isUnassessed ? 'Unassessed' : urgency}
                      </Badge>
                    </td>

                    <td className="col-mosca">
                      <div className="mosca-cell-content">
                        {isViolated ? (
                          <span className="mosca-status-violated" title="X + Y > Z condition violated">
                            <AlertOctagon size={13} aria-hidden="true" />
                            <span>{typeof slack === 'number' ? `${slack.toFixed(1)} yrs` : 'SNDL Risk'}</span>
                          </span>
                        ) : typeof slack === 'number' ? (
                          <span className="mosca-status-compliant" title="Mosca compliant buffer">
                            <span>+{slack.toFixed(1)} yrs</span>
                          </span>
                        ) : (
                          <span className="mosca-status-neutral">Standard</span>
                        )}
                      </div>
                    </td>

                    <td className="col-reasons">
                      {primaryReason ? (
                        <span className="reason-code-badge" title={primaryReason}>
                          {formatReasonCode(primaryReason)}
                        </span>
                      ) : (
                        <span className="text-dim-subtle">—</span>
                      )}
                    </td>

                    <td className="col-action">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onSelectRisk) onSelectRisk({ ...item, backlogItem: matchingBacklog });
                        }}
                        aria-label={`Inspect ${item.algorithm || item.asset_id} risk detail`}
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
      {filteredItems.length > 0 && (
        <div className="risk-pagination" role="navigation" aria-label="Risk Table Pagination">
          <div className="pagination-info">
            Showing <strong>{(currentPage - 1) * pageSize + 1}</strong> to{' '}
            <strong>{Math.min(currentPage * pageSize, filteredItems.length)}</strong> of{' '}
            <strong>{filteredItems.length}</strong> evaluations
          </div>

          <div className="pagination-controls">
            <div className="page-size-selector">
              <label htmlFor="risk-page-size-select" className="page-size-label">
                Per page:
              </label>
              <select
                id="risk-page-size-select"
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="page-size-select"
                aria-label="Evaluations per page"
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
              aria-label="Previous page"
            >
              <ChevronLeft size={16} aria-hidden="true" />
              <span>Prev</span>
            </Button>

            <span className="page-counter">
              Page <strong>{currentPage}</strong> of <strong>{totalPages}</strong>
            </span>

            <Button
              variant="outline"
              size="sm"
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              aria-label="Next page"
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
