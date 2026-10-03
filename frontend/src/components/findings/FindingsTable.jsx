import React, { useState, useMemo } from 'react';
import Badge from '../common/Badge';
import Button from '../common/Button';
import './FindingsTable.css';

/**
 * Normalizes observations and canonical assets into flat tabular finding records.
 * @param {Array} canonicalAssets
 * @param {Array} directObservations
 * @param {Array} riskEvaluations
 * @returns {Array}
 */
export function normalizeFindings(canonicalAssets = [], directObservations = [], riskEvaluations = []) {
  const riskMap = new Map();
  if (Array.isArray(riskEvaluations)) {
    riskEvaluations.forEach((evalItem) => {
      if (evalItem?.asset_id) {
        riskMap.set(evalItem.asset_id, evalItem);
      }
    });
  }

  const items = [];

  if (Array.isArray(canonicalAssets) && canonicalAssets.length > 0) {
    canonicalAssets.forEach((asset) => {
      const assetId = asset.asset_id || asset.id || 'unknown-asset';
      const primaryName = asset.primary_name || asset.name || 'Unknown';
      const riskInfo = riskMap.get(assetId);

      if (Array.isArray(asset.observations) && asset.observations.length > 0) {
        asset.observations.forEach((obs, idx) => {
          items.push({
            id: obs.canonical_id || obs.observation_id || `${assetId}-obs-${idx}`,
            assetId,
            primaryName,
            algorithm: obs.algorithm || primaryName,
            sourceKind: obs.source_kind || 'UNKNOWN',
            claimType: obs.claim_type || 'ALGORITHM_USE',
            purpose: obs.purpose || 'UNSPECIFIED',
            keySizeBits: obs.key_size_bits || null,
            curveName: obs.curve_name || null,
            relativePath: obs.relative_path || 'Unknown',
            startLine: obs.start_line,
            endLine: obs.end_line,
            confidence: obs.confidence || 'UNASSESSED',
            confidenceRationale: obs.confidence_rationale || null,
            sanitizedExcerpt: obs.sanitized_excerpt || '',
            evidenceDigest: obs.evidence_digest || null,
            state: obs.state || 'OBSERVED',
            detectorId: obs.detector_id || 'unknown-detector',
            rulesetVersion: obs.ruleset_version || null,
            observedAt: obs.observed_at || null,
            rawParameters: obs.raw_parameters || {},
            riskEvaluation: riskInfo || null,
          });
        });
      } else {
        items.push({
          id: assetId,
          assetId,
          primaryName,
          algorithm: primaryName,
          sourceKind: 'UNKNOWN',
          claimType: 'ALGORITHM_USE',
          purpose: 'UNSPECIFIED',
          keySizeBits: null,
          curveName: null,
          relativePath: 'Unknown',
          startLine: null,
          endLine: null,
          confidence: 'UNASSESSED',
          confidenceRationale: null,
          sanitizedExcerpt: '',
          evidenceDigest: null,
          state: 'OBSERVED',
          detectorId: 'unknown-detector',
          rulesetVersion: null,
          observedAt: null,
          rawParameters: {},
          riskEvaluation: riskInfo || null,
        });
      }
    });
  } else if (Array.isArray(directObservations) && directObservations.length > 0) {
    directObservations.forEach((obs, idx) => {
      const assetId = obs.candidate_asset_id || obs.asset_id || `obs-${idx}`;
      const riskInfo = riskMap.get(assetId);

      items.push({
        id: obs.canonical_id || obs.observation_id || `obs-${idx}`,
        assetId,
        primaryName: obs.algorithm || 'Unknown',
        algorithm: obs.algorithm || 'Unknown',
        sourceKind: obs.source_kind || 'UNKNOWN',
        claimType: obs.claim_type || 'ALGORITHM_USE',
        purpose: obs.purpose || 'UNSPECIFIED',
        keySizeBits: obs.key_size_bits || null,
        curveName: obs.curve_name || null,
        relativePath: obs.relative_path || 'Unknown',
        startLine: obs.start_line,
        endLine: obs.end_line,
        confidence: obs.confidence || 'UNASSESSED',
        confidenceRationale: obs.confidence_rationale || null,
        sanitizedExcerpt: obs.sanitized_excerpt || '',
        evidenceDigest: obs.evidence_digest || null,
        state: obs.state || 'OBSERVED',
        detectorId: obs.detector_id || 'unknown-detector',
        rulesetVersion: obs.ruleset_version || null,
        observedAt: obs.observed_at || null,
        rawParameters: obs.raw_parameters || {},
        riskEvaluation: riskInfo || null,
      });
    });
  }

  return items;
}

/**
 * Returns badge variant for confidence level.
 * Security honesty: UNASSESSED / UNVERIFIED are neutral, never positive.
 */
function getConfidenceVariant(confidence) {
  const norm = String(confidence).toUpperCase();
  if (norm === 'CONFIRMED') return 'high'; // verified discovery
  if (norm === 'HIGH' || norm === 'INFERRED') return 'medium';
  if (norm === 'HEURISTIC') return 'low';
  return 'neutral'; // unassessed / unverified
}

/**
 * Returns badge variant for source kind.
 */
function getSourceKindVariant(sourceKind) {
  const norm = String(sourceKind).toUpperCase();
  if (norm === 'SOURCE_CODE') return 'primary';
  if (norm === 'CONFIG') return 'secondary';
  if (norm === 'MANIFEST' || norm === 'PACKAGE_MANIFEST') return 'warning';
  if (norm === 'CERTIFICATE' || norm === 'CERTIFICATE_STORE') return 'high';
  return 'neutral';
}

/**
 * Reusable Findings Table with client-side search, filtering, sorting, and pagination.
 */
export default function FindingsTable({
  canonicalAssets = [],
  directObservations = [],
  riskEvaluations = [],
  onSelectFinding,
  searchPlaceholder = 'Search algorithms, paths, detectors, or excerpts...',
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [sourceFilter, setSourceFilter] = useState('ALL');
  const [confidenceFilter, setConfidenceFilter] = useState('ALL');
  const [purposeFilter, setPurposeFilter] = useState('ALL');
  const [sortField, setSortField] = useState('algorithm');
  const [sortOrder, setSortOrder] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Flatten raw input
  const allFindings = useMemo(
    () => normalizeFindings(canonicalAssets, directObservations, riskEvaluations),
    [canonicalAssets, directObservations, riskEvaluations]
  );

  // Extract distinct source kinds and purposes for filter dropdowns
  const availableSources = useMemo(() => {
    const set = new Set();
    allFindings.forEach((f) => {
      if (f.sourceKind) set.add(f.sourceKind);
    });
    return Array.from(set).sort();
  }, [allFindings]);

  const availablePurposes = useMemo(() => {
    const set = new Set();
    allFindings.forEach((f) => {
      if (f.purpose && f.purpose !== 'UNSPECIFIED') set.add(f.purpose);
    });
    return Array.from(set).sort();
  }, [allFindings]);

  // Client-side filtering & search
  const filteredFindings = useMemo(() => {
    return allFindings.filter((item) => {
      // Source kind filter
      if (sourceFilter !== 'ALL' && item.sourceKind !== sourceFilter) {
        return false;
      }
      // Confidence filter
      if (confidenceFilter !== 'ALL' && item.confidence.toUpperCase() !== confidenceFilter) {
        return false;
      }
      // Purpose filter
      if (purposeFilter !== 'ALL' && item.purpose !== purposeFilter) {
        return false;
      }
      // Text search
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchAlgo = item.algorithm.toLowerCase().includes(query);
        const matchAsset = item.assetId.toLowerCase().includes(query);
        const matchPath = item.relativePath.toLowerCase().includes(query);
        const matchDetector = item.detectorId.toLowerCase().includes(query);
        const matchExcerpt = item.sanitizedExcerpt.toLowerCase().includes(query);
        const matchPurpose = item.purpose.toLowerCase().includes(query);

        if (!matchAlgo && !matchAsset && !matchPath && !matchDetector && !matchExcerpt && !matchPurpose) {
          return false;
        }
      }
      return true;
    });
  }, [allFindings, sourceFilter, confidenceFilter, purposeFilter, searchQuery]);

  // Client-side sorting
  const sortedFindings = useMemo(() => {
    const items = [...filteredFindings];
    items.sort((a, b) => {
      let valA = a[sortField] || '';
      let valB = b[sortField] || '';

      if (typeof valA === 'string') valA = valA.toLowerCase();
      if (typeof valB === 'string') valB = valB.toLowerCase();

      if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
      if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
    return items;
  }, [filteredFindings, sortField, sortOrder]);

  // Pagination calculation
  const totalItems = sortedFindings.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const validPage = Math.min(Math.max(1, currentPage), totalPages);

  const paginatedFindings = useMemo(() => {
    const start = (validPage - 1) * pageSize;
    return sortedFindings.slice(start, start + pageSize);
  }, [sortedFindings, validPage, pageSize]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setSourceFilter('ALL');
    setConfidenceFilter('ALL');
    setPurposeFilter('ALL');
    setCurrentPage(1);
  };

  const hasActiveFilters = searchQuery !== '' || sourceFilter !== 'ALL' || confidenceFilter !== 'ALL' || purposeFilter !== 'ALL';

  return (
    <div className="findings-table-container" data-testid="findings-table-container">
      {/* Toolbar / Filters */}
      <div className="findings-toolbar" role="search" aria-label="Findings filters">
        <div className="findings-search-wrapper">
          <span className="findings-search-icon" aria-hidden="true">🔍</span>
          <input
            type="text"
            id="findings-search-input"
            className="findings-search-input"
            placeholder={searchPlaceholder}
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
            aria-label="Search findings"
          />
        </div>

        <div className="findings-filters-group">
          <select
            id="findings-source-filter"
            className="findings-filter-select"
            value={sourceFilter}
            onChange={(e) => {
              setSourceFilter(e.target.value);
              setCurrentPage(1);
            }}
            aria-label="Filter by source type"
          >
            <option value="ALL">All Sources</option>
            {availableSources.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>

          <select
            id="findings-confidence-filter"
            className="findings-filter-select"
            value={confidenceFilter}
            onChange={(e) => {
              setConfidenceFilter(e.target.value);
              setCurrentPage(1);
            }}
            aria-label="Filter by confidence"
          >
            <option value="ALL">All Confidence Levels</option>
            <option value="CONFIRMED">Confirmed</option>
            <option value="HIGH">High</option>
            <option value="INFERRED">Inferred</option>
            <option value="HEURISTIC">Heuristic</option>
            <option value="UNASSESSED">Unassessed / Other</option>
          </select>

          {availablePurposes.length > 0 && (
            <select
              id="findings-purpose-filter"
              className="findings-filter-select"
              value={purposeFilter}
              onChange={(e) => {
                setPurposeFilter(e.target.value);
                setCurrentPage(1);
              }}
              aria-label="Filter by cryptographic purpose"
            >
              <option value="ALL">All Purposes</option>
              {availablePurposes.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          )}

          {hasActiveFilters && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleClearFilters}
              aria-label="Clear all applied filters"
            >
              Reset Filters
            </Button>
          )}
        </div>
      </div>

      {/* Table Display */}
      <div className="findings-table-wrapper">
        <table className="findings-table" aria-label="Cryptographic findings list">
          <thead>
            <tr>
              <th
                scope="col"
                className="sortable"
                onClick={() => handleSort('algorithm')}
                aria-sort={sortField === 'algorithm' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
              >
                Algorithm / Primitive
                {sortField === 'algorithm' && (
                  <span className="sort-icon">{sortOrder === 'asc' ? '▲' : '▼'}</span>
                )}
              </th>
              <th
                scope="col"
                className="sortable"
                onClick={() => handleSort('sourceKind')}
                aria-sort={sortField === 'sourceKind' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
              >
                Source Surface
                {sortField === 'sourceKind' && (
                  <span className="sort-icon">{sortOrder === 'asc' ? '▲' : '▼'}</span>
                )}
              </th>
              <th
                scope="col"
                className="sortable"
                onClick={() => handleSort('purpose')}
                aria-sort={sortField === 'purpose' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
              >
                Purpose / Usage
                {sortField === 'purpose' && (
                  <span className="sort-icon">{sortOrder === 'asc' ? '▲' : '▼'}</span>
                )}
              </th>
              <th
                scope="col"
                className="sortable"
                onClick={() => handleSort('relativePath')}
                aria-sort={sortField === 'relativePath' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
              >
                Location
                {sortField === 'relativePath' && (
                  <span className="sort-icon">{sortOrder === 'asc' ? '▲' : '▼'}</span>
                )}
              </th>
              <th
                scope="col"
                className="sortable"
                onClick={() => handleSort('confidence')}
                aria-sort={sortField === 'confidence' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
              >
                Confidence
                {sortField === 'confidence' && (
                  <span className="sort-icon">{sortOrder === 'asc' ? '▲' : '▼'}</span>
                )}
              </th>
              <th scope="col">Action</th>
            </tr>
          </thead>
          <tbody>
            {paginatedFindings.length === 0 ? (
              <tr>
                <td colSpan="6" className="empty-matches">
                  {allFindings.length === 0
                    ? 'No cryptographic findings discovered in this scan.'
                    : 'No findings match your search and filter criteria.'}
                </td>
              </tr>
            ) : (
              paginatedFindings.map((finding) => {
                const locText = finding.relativePath !== 'Unknown'
                  ? (finding.startLine ? `${finding.relativePath}:${finding.startLine}` : finding.relativePath)
                  : 'N/A';

                return (
                  <tr
                    key={finding.id}
                    tabIndex={0}
                    onClick={() => onSelectFinding?.(finding)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        onSelectFinding?.(finding);
                      }
                    }}
                    role="button"
                    aria-label={`View details for ${finding.algorithm} at ${locText}`}
                  >
                    <td>
                      <div className="finding-algorithm-cell">
                        <span className="finding-algo-name">{finding.algorithm}</span>
                        <span className="finding-asset-id" title={finding.assetId}>
                          {finding.assetId}
                        </span>
                      </div>
                    </td>
                    <td>
                      <Badge variant={getSourceKindVariant(finding.sourceKind)}>
                        {finding.sourceKind}
                      </Badge>
                    </td>
                    <td>
                      <span style={{ color: 'var(--text-muted)' }}>
                        {finding.purpose || 'UNSPECIFIED'}
                      </span>
                    </td>
                    <td>
                      <code className="finding-location-code" title={locText}>
                        {locText}
                      </code>
                    </td>
                    <td>
                      <Badge variant={getConfidenceVariant(finding.confidence)}>
                        {finding.confidence}
                      </Badge>
                    </td>
                    <td>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectFinding?.(finding);
                        }}
                        aria-label={`Inspect evidence for ${finding.algorithm}`}
                      >
                        Inspect
                      </Button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {totalItems > 0 && (
        <div className="findings-pagination">
          <span>
            Showing <strong>{Math.min(totalItems, (validPage - 1) * pageSize + 1)}</strong> to{' '}
            <strong>{Math.min(totalItems, validPage * pageSize)}</strong> of{' '}
            <strong>{totalItems}</strong> findings
          </span>

          <div className="findings-pagination-controls">
            <button
              type="button"
              className="findings-pagination-btn"
              disabled={validPage <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              aria-label="Previous page"
            >
              Previous
            </button>
            <span>
              Page {validPage} of {totalPages}
            </span>
            <button
              type="button"
              className="findings-pagination-btn"
              disabled={validPage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              aria-label="Next page"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
