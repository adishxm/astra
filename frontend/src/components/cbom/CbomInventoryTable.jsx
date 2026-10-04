import React, { useState, useMemo } from 'react';
import Badge from '../common/Badge';
import Button from '../common/Button';
import EmptyState from '../common/EmptyState';
import {
  Search,
  Filter,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Key,
} from 'lucide-react';
import './CbomInventoryTable.css';

/**
 * Normalizes scan data and/or CycloneDX export components into standard CBOM inventory records.
 * @param {Array} canonicalAssets
 * @param {Array} [_directObservations=[]]
 * @param {Object} [exportData=null]
 * @returns {Array}
 */
export function normalizeCbomInventory(canonicalAssets = [], _directObservations = [], exportData = null) {
  const items = [];

  // Build a lookup of CycloneDX components if available
  const exportComponentMap = new Map();
  if (Array.isArray(exportData?.components)) {
    exportData.components.forEach((c) => {
      if (c?.name) {
        exportComponentMap.set(c.name, c);
        const baseAlgo = c.cryptoProperties?.algorithmProperties?.name;
        if (baseAlgo) {
          exportComponentMap.set(baseAlgo, c);
        }
      }
    });
  }

  // 1. Process canonical assets and their observations
  if (Array.isArray(canonicalAssets) && canonicalAssets.length > 0) {
    canonicalAssets.forEach((asset) => {
      const assetId = asset.asset_id || asset.id || 'unidentified-asset';
      const primaryName = asset.primary_name || asset.name || 'Unknown Cryptographic Asset';

      if (Array.isArray(asset.observations) && asset.observations.length > 0) {
        asset.observations.forEach((obs, idx) => {
          const algo = obs.algorithm || primaryName;
          const matchedExport = exportComponentMap.get(algo) || null;
          const paramSet =
            matchedExport?.cryptoProperties?.algorithmProperties?.parameterSetIdentifier ||
            (obs.key_size_bits ? String(obs.key_size_bits) : obs.curve_name || 'standard');
          const assetType = matchedExport?.cryptoProperties?.assetType || 'algorithm';
          const execEnv =
            matchedExport?.cryptoProperties?.algorithmProperties?.executionEnvironment ||
            'software-plain-ram';

          items.push({
            id: obs.canonical_id || obs.observation_id || `${assetId}-cbom-${idx}`,
            componentName: matchedExport?.name || `${algo}-${assetId.slice(0, 8)}`,
            assetId,
            primaryName,
            algorithm: algo,
            purpose: obs.purpose || 'UNSPECIFIED',
            assetType,
            parameterSetIdentifier: paramSet,
            executionEnvironment: execEnv,
            keySizeBits: obs.key_size_bits || null,
            curveName: obs.curve_name || null,
            sourceKind: obs.source_kind || 'UNKNOWN',
            claimType: obs.claim_type || 'ALGORITHM_USE',
            relativePath: obs.relative_path || 'Unknown location',
            startLine: obs.start_line,
            endLine: obs.end_line,
            confidence: obs.confidence || 'UNASSESSED',
            confidenceRationale: obs.confidence_rationale || null,
            sanitizedExcerpt: obs.sanitized_excerpt || '',
            evidenceDigest: obs.evidence_digest || null,
            detectorId: obs.detector_id || 'unknown-detector',
            rulesetVersion: obs.ruleset_version || null,
            rawParameters: obs.raw_parameters || {},
            cycloneDxComponent: matchedExport,
          });
        });
      } else {
        items.push({
          id: assetId,
          componentName: `${primaryName}-${assetId.slice(0, 8)}`,
          assetId,
          primaryName,
          algorithm: primaryName,
          purpose: 'UNSPECIFIED',
          assetType: 'algorithm',
          parameterSetIdentifier: 'standard',
          executionEnvironment: 'software-plain-ram',
          keySizeBits: null,
          curveName: null,
          sourceKind: 'UNKNOWN',
          claimType: 'ALGORITHM_USE',
          relativePath: 'Unknown location',
          startLine: null,
          endLine: null,
          confidence: 'UNASSESSED',
          confidenceRationale: null,
          sanitizedExcerpt: '',
          evidenceDigest: null,
          detectorId: 'unknown-detector',
          rulesetVersion: null,
          rawParameters: {},
          cycloneDxComponent: null,
        });
      }
    });
  } else if (Array.isArray(exportData?.components) && exportData.components.length > 0) {
    // Fallback: derive directly from CycloneDX components
    exportData.components.forEach((c, idx) => {
      const algoName = c.cryptoProperties?.algorithmProperties?.name || c.name || 'Cryptographic Asset';
      items.push({
        id: `cyclonedx-comp-${idx}`,
        componentName: c.name || algoName,
        assetId: `cyclonedx-asset-${idx}`,
        primaryName: algoName,
        algorithm: algoName,
        purpose: 'UNSPECIFIED',
        assetType: c.cryptoProperties?.assetType || 'algorithm',
        parameterSetIdentifier:
          c.cryptoProperties?.algorithmProperties?.parameterSetIdentifier || 'standard',
        executionEnvironment:
          c.cryptoProperties?.algorithmProperties?.executionEnvironment || 'software-plain-ram',
        keySizeBits: null,
        curveName: null,
        sourceKind: 'UNKNOWN',
        claimType: 'ALGORITHM_USE',
        relativePath: 'CycloneDX CBOM Specification',
        startLine: null,
        endLine: null,
        confidence: 'CONFIRMED',
        confidenceRationale: 'Derived from CycloneDX 1.6 export artifact',
        sanitizedExcerpt: '',
        evidenceDigest: null,
        detectorId: 'cyclonedx-exporter',
        rulesetVersion: '1.6',
        rawParameters: {},
        cycloneDxComponent: c,
      });
    });
  }

  return items;
}

const CONFIDENCE_WEIGHTS = {
  CONFIRMED: 3,
  INFERRED: 2,
  HEURISTIC: 1,
  UNASSESSED: 0,
};

/**
 * Format purpose label into clean human-readable text
 * @param {string} purpose
 * @returns {string}
 */
export function formatPurpose(purpose) {
  if (!purpose || purpose === 'UNSPECIFIED') return 'General Crypto';
  return String(purpose).replace(/_/g, ' ');
}

/**
 * Cryptographic Bill of Materials (CBOM) Inventory Table
 *
 * @param {Object} props
 * @param {Array} [props.components=[]]
 * @param {(item: Object) => void} [props.onSelectComponent]
 * @param {string} [props.className='']
 */
export default function CbomInventoryTable({
  components = [],
  onSelectComponent,
  className = '',
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [purposeFilter, setPurposeFilter] = useState('ALL');
  const [surfaceFilter, setSurfaceFilter] = useState('ALL');
  const [confidenceFilter, setConfidenceFilter] = useState('ALL');
  const [sortField, setSortField] = useState('algorithm');
  const [sortDir, setSortDir] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Extract unique filter options
  const purposeOptions = useMemo(() => {
    const set = new Set();
    components.forEach((c) => {
      if (c.purpose) set.add(c.purpose);
    });
    return Array.from(set).sort();
  }, [components]);

  const surfaceOptions = useMemo(() => {
    const set = new Set();
    components.forEach((c) => {
      if (c.sourceKind) set.add(c.sourceKind);
    });
    return Array.from(set).sort();
  }, [components]);

  // Filter components
  const filteredItems = useMemo(() => {
    return components.filter((item) => {
      // 1. Purpose filter
      if (purposeFilter !== 'ALL' && item.purpose !== purposeFilter) {
        return false;
      }

      // 2. Surface filter
      if (surfaceFilter !== 'ALL' && item.sourceKind !== surfaceFilter) {
        return false;
      }

      // 3. Confidence filter
      if (confidenceFilter !== 'ALL') {
        const itemConfidence = (item.confidence ? String(item.confidence).toUpperCase() : 'UNASSESSED');
        if (itemConfidence !== confidenceFilter) {
          return false;
        }
      }

      // 4. Search query
      if (searchTerm.trim()) {
        const query = searchTerm.toLowerCase();
        const algo = (item.algorithm || '').toLowerCase();
        const compName = (item.componentName || '').toLowerCase();
        const assetId = (item.assetId || '').toLowerCase();
        const path = (item.relativePath || '').toLowerCase();
        const purpose = (item.purpose || '').toLowerCase();
        const detector = (item.detectorId || '').toLowerCase();
        const param = (item.parameterSetIdentifier || '').toLowerCase();

        const matches =
          algo.includes(query) ||
          compName.includes(query) ||
          assetId.includes(query) ||
          path.includes(query) ||
          purpose.includes(query) ||
          detector.includes(query) ||
          param.includes(query);

        if (!matches) return false;
      }

      return true;
    });
  }, [components, purposeFilter, surfaceFilter, confidenceFilter, searchTerm]);

  // Sort components
  const sortedItems = useMemo(() => {
    const items = [...filteredItems];
    items.sort((a, b) => {
      let comparison = 0;

      if (sortField === 'algorithm') {
        comparison = (a.algorithm || '').localeCompare(b.algorithm || '');
      } else if (sortField === 'purpose') {
        comparison = (a.purpose || '').localeCompare(b.purpose || '');
      } else if (sortField === 'location') {
        comparison = (a.relativePath || '').localeCompare(b.relativePath || '');
      } else if (sortField === 'keysize') {
        const sizeA = typeof a.keySizeBits === 'number' ? a.keySizeBits : -1;
        const sizeB = typeof b.keySizeBits === 'number' ? b.keySizeBits : -1;
        comparison = sizeA - sizeB;
      } else if (sortField === 'confidence') {
        const confA = CONFIDENCE_WEIGHTS[a.confidence?.toUpperCase()] ?? 0;
        const confB = CONFIDENCE_WEIGHTS[b.confidence?.toUpperCase()] ?? 0;
        comparison = confA - confB;
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

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  const handlePurposeChange = (val) => {
    setPurposeFilter(val);
    setCurrentPage(1);
  };

  const handleSurfaceChange = (val) => {
    setSurfaceFilter(val);
    setCurrentPage(1);
  };

  const handleConfidenceChange = (val) => {
    setConfidenceFilter(val);
    setCurrentPage(1);
  };

  const handleResetFilters = () => {
    setSearchTerm('');
    setPurposeFilter('ALL');
    setSurfaceFilter('ALL');
    setConfidenceFilter('ALL');
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
      return <ArrowUpDown size={14} className="cbom-sort-icon cbom-sort-icon--inactive" aria-hidden="true" />;
    }
    return sortDir === 'asc' ? (
      <ArrowUp size={14} className="cbom-sort-icon cbom-sort-icon--active" aria-hidden="true" />
    ) : (
      <ArrowDown size={14} className="cbom-sort-icon cbom-sort-icon--active" aria-hidden="true" />
    );
  };

  return (
    <div className={`cbom-table-container ${className}`} data-testid="cbom-inventory-table">
      {/* Search & Filter Controls */}
      <div className="cbom-table-controls">
        <div className="cbom-search-box">
          <Search size={16} className="cbom-search-icon" aria-hidden="true" />
          <input
            type="text"
            placeholder="Search CBOM by algorithm, parameter, path, asset, or detector..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="cbom-search-input"
            aria-label="Filter CBOM components"
            data-testid="cbom-search-input"
          />
          {searchTerm && (
            <button
              type="button"
              className="cbom-search-clear"
              onClick={() => {
                setSearchTerm('');
                setCurrentPage(1);
              }}
              aria-label="Clear CBOM search query"
            >
              ×
            </button>
          )}
        </div>

        <div className="cbom-filters-group">
          {/* Purpose Filter */}
          <div className="cbom-select-wrapper">
            <Key size={14} className="cbom-select-icon" aria-hidden="true" />
            <select
              value={purposeFilter}
              onChange={(e) => handlePurposeChange(e.target.value)}
              className="cbom-select"
              aria-label="Filter by Cryptographic Purpose"
              data-testid="cbom-purpose-filter"
            >
              <option value="ALL">All Purposes</option>
              {purposeOptions.map((p) => (
                <option key={p} value={p}>
                  {formatPurpose(p)}
                </option>
              ))}
            </select>
          </div>

          {/* Surface Filter */}
          <div className="cbom-select-wrapper">
            <Filter size={14} className="cbom-select-icon" aria-hidden="true" />
            <select
              value={surfaceFilter}
              onChange={(e) => handleSurfaceChange(e.target.value)}
              className="cbom-select"
              aria-label="Filter by Discovery Surface"
              data-testid="cbom-surface-filter"
            >
              <option value="ALL">All Surfaces</option>
              {surfaceOptions.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          {/* Confidence Filter */}
          <div className="cbom-select-wrapper">
            <ShieldCheck size={14} className="cbom-select-icon" aria-hidden="true" />
            <select
              value={confidenceFilter}
              onChange={(e) => handleConfidenceChange(e.target.value)}
              className="cbom-select"
              aria-label="Filter by Detection Confidence"
              data-testid="cbom-confidence-filter"
            >
              <option value="ALL">All Confidences</option>
              <option value="CONFIRMED">Confirmed</option>
              <option value="INFERRED">Inferred</option>
              <option value="HEURISTIC">Heuristic</option>
              <option value="UNASSESSED">Unassessed</option>
            </select>
          </div>

          {(searchTerm || purposeFilter !== 'ALL' || surfaceFilter !== 'ALL' || confidenceFilter !== 'ALL') && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleResetFilters}
              data-testid="cbom-reset-filters-btn"
            >
              Reset
            </Button>
          )}
        </div>
      </div>

      {/* Table Content */}
      {paginatedItems.length === 0 ? (
        <div className="cbom-table-empty">
          <EmptyState
            title="No CBOM Components Match Criteria"
            message={
              components.length === 0
                ? 'No cryptographic components are recorded in this Bill of Materials.'
                : 'Try adjusting your search query, purpose filter, or surface filters.'
            }
            ctaLabel={components.length > 0 ? 'Reset Filters' : undefined}
            onCta={components.length > 0 ? handleResetFilters : undefined}
          />
        </div>
      ) : (
        <div className="cbom-table-scroll">
          <table className="cbom-table" aria-label="Cryptographic Bill of Materials Inventory">
            <thead>
              <tr>
                <th scope="col" className="col-comp-algo">
                  <button
                    type="button"
                    className="th-cbom-button"
                    onClick={() => handleSort('algorithm')}
                  >
                    <span>Algorithm & Asset</span>
                    {getSortIcon('algorithm')}
                  </button>
                </th>
                <th scope="col" className="col-comp-purpose">
                  <button
                    type="button"
                    className="th-cbom-button"
                    onClick={() => handleSort('purpose')}
                  >
                    <span>Purpose</span>
                    {getSortIcon('purpose')}
                  </button>
                </th>
                <th scope="col" className="col-comp-location">
                  <button
                    type="button"
                    className="th-cbom-button"
                    onClick={() => handleSort('location')}
                  >
                    <span>Source Location</span>
                    {getSortIcon('location')}
                  </button>
                </th>
                <th scope="col" className="col-comp-params">
                  <button
                    type="button"
                    className="th-cbom-button"
                    onClick={() => handleSort('keysize')}
                  >
                    <span>Parameters</span>
                    {getSortIcon('keysize')}
                  </button>
                </th>
                <th scope="col" className="col-comp-confidence">
                  <button
                    type="button"
                    className="th-cbom-button"
                    onClick={() => handleSort('confidence')}
                  >
                    <span>Confidence</span>
                    {getSortIcon('confidence')}
                  </button>
                </th>
                <th scope="col" className="col-comp-action">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {paginatedItems.map((item, idx) => {
                const confUpper = (item.confidence ? String(item.confidence).toUpperCase() : 'UNASSESSED');
                const confVariant =
                  confUpper === 'CONFIRMED'
                    ? 'safe'
                    : confUpper === 'INFERRED'
                    ? 'medium'
                    : confUpper === 'HEURISTIC'
                    ? 'high'
                    : 'unknown';

                return (
                  <tr
                    key={item.id || `cbom-row-${idx}`}
                    className="cbom-table-row"
                    data-testid={`cbom-row-${item.id || idx}`}
                    onClick={() => onSelectComponent && onSelectComponent(item)}
                    tabIndex={0}
                    role="button"
                    aria-label={`Inspect CBOM component for ${item.algorithm}`}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        if (onSelectComponent) onSelectComponent(item);
                      }
                    }}
                  >
                    <td className="col-comp-algo">
                      <div className="comp-algo-cell">
                        <span className="comp-algo-name">{item.algorithm}</span>
                        <div className="comp-asset-row">
                          <code className="comp-asset-id" title={item.assetId}>
                            {item.assetId}
                          </code>
                          <span className="comp-asset-type-tag">{item.assetType || 'algorithm'}</span>
                        </div>
                      </div>
                    </td>

                    <td className="col-comp-purpose">
                      <span className="comp-purpose-badge">
                        {formatPurpose(item.purpose)}
                      </span>
                    </td>

                    <td className="col-comp-location">
                      <div className="comp-location-cell">
                        <div className="comp-surface-row">
                          <Badge variant="neutral" className="comp-surface-badge">
                            {item.sourceKind || 'UNKNOWN'}
                          </Badge>
                          <span className="comp-claim-tag">{item.claimType}</span>
                        </div>
                        <span className="comp-path-text" title={item.relativePath}>
                          {item.relativePath}
                          {item.startLine !== null && item.startLine !== undefined && (
                            <span className="comp-line-tag">:{item.startLine}</span>
                          )}
                        </span>
                      </div>
                    </td>

                    <td className="col-comp-params">
                      <div className="comp-params-cell">
                        {item.keySizeBits ? (
                          <span className="param-pill">
                            Key: <strong>{item.keySizeBits} bits</strong>
                          </span>
                        ) : item.curveName ? (
                          <span className="param-pill">
                            Curve: <strong>{item.curveName}</strong>
                          </span>
                        ) : (
                          <span className="param-pill">
                            Set: <strong>{item.parameterSetIdentifier || 'standard'}</strong>
                          </span>
                        )}
                        <span className="comp-env-subtext">{item.executionEnvironment}</span>
                      </div>
                    </td>

                    <td className="col-comp-confidence">
                      <Badge variant={confVariant}>
                        {confUpper === 'CONFIRMED' ? 'Confirmed' : confUpper}
                      </Badge>
                    </td>

                    <td className="col-comp-action">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onSelectComponent) onSelectComponent(item);
                        }}
                        aria-label={`Inspect ${item.algorithm} CBOM component`}
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
        <div className="cbom-pagination" role="navigation" aria-label="CBOM Inventory Pagination">
          <div className="cbom-pagination-info">
            Showing <strong>{(currentPage - 1) * pageSize + 1}</strong> to{' '}
            <strong>{Math.min(currentPage * pageSize, filteredItems.length)}</strong> of{' '}
            <strong>{filteredItems.length}</strong> components
          </div>

          <div className="cbom-pagination-controls">
            <div className="cbom-page-size-selector">
              <label htmlFor="cbom-page-size-select" className="cbom-page-size-label">
                Per page:
              </label>
              <select
                id="cbom-page-size-select"
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="cbom-page-size-select"
                aria-label="Components per page"
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
              aria-label="Previous CBOM page"
            >
              <ChevronLeft size={16} aria-hidden="true" />
              <span>Prev</span>
            </Button>

            <span className="cbom-page-counter">
              Page <strong>{currentPage}</strong> of <strong>{totalPages}</strong>
            </span>

            <Button
              variant="outline"
              size="sm"
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              aria-label="Next CBOM page"
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
