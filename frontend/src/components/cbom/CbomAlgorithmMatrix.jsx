import React, { useMemo } from 'react';
import Card from '../common/Card';
import { Cpu } from 'lucide-react';
import './CbomAlgorithmMatrix.css';

/**
 * Categorizes algorithms into standard functional families
 * @param {string} algo
 * @param {string} purpose
 * @returns {string}
 */
export function getAlgorithmFamily(algo = '', purpose = '') {
  const a = algo.toUpperCase();
  const p = purpose.toUpperCase();

  if (a.includes('KEM') || a.includes('ML-KEM') || a.includes('KYBER') || p.includes('KEY_EXCHANGE')) {
    return 'Post-Quantum & Key Encapsulation (PQC/KEM)';
  }
  if (a.includes('RSA') || a.includes('ECC') || a.includes('ECDSA') || a.includes('ED25519') || p.includes('ASYMMETRIC')) {
    return 'Public Key & Asymmetric Cryptography';
  }
  if (a.includes('AES') || a.includes('CHACHA') || a.includes('DES') || p.includes('SYMMETRIC') || p.includes('ENCRYPTION')) {
    return 'Symmetric Block & Stream Ciphers';
  }
  if (a.includes('MD5') || a.includes('SHA') || a.includes('BLAKE') || p.includes('HASH')) {
    return 'Cryptographic Hash & Digest Functions';
  }
  if (a.includes('TLS') || a.includes('SSL') || a.includes('CIPHER') || p.includes('PROTOCOL')) {
    return 'Transport Security & Protocol Suites';
  }
  return 'Cryptographic Libraries & Generic Primitives';
}

/**
 * CBOM Algorithm Classification & Inventory Matrix
 *
 * @param {Object} props
 * @param {Array} [props.components=[]]
 * @param {(algo: string) => void} [props.onSelectAlgorithm]
 * @param {string} [props.className='']
 */
export default function CbomAlgorithmMatrix({
  components = [],
  onSelectAlgorithm,
  className = '',
}) {
  const groupedMatrix = useMemo(() => {
    const map = new Map();

    components.forEach((c) => {
      const algo = c.algorithm || 'Unknown Algorithm';
      const family = getAlgorithmFamily(algo, c.purpose);

      if (!map.has(family)) {
        map.set(family, new Map());
      }
      const familyMap = map.get(family);

      if (!familyMap.has(algo)) {
        familyMap.set(algo, {
          algorithm: algo,
          purpose: c.purpose || 'UNSPECIFIED',
          count: 0,
          parameters: new Set(),
          surfaces: new Set(),
        });
      }

      const record = familyMap.get(algo);
      record.count += 1;
      if (c.keySizeBits) record.parameters.add(`${c.keySizeBits}-bit`);
      if (c.curveName) record.parameters.add(c.curveName);
      if (c.parameterSetIdentifier && c.parameterSetIdentifier !== 'standard') {
        record.parameters.add(c.parameterSetIdentifier);
      }
      if (c.sourceKind) record.surfaces.add(c.sourceKind);
    });

    // Convert map to sorted array
    const result = [];
    map.forEach((algosMap, familyName) => {
      result.push({
        familyName,
        algorithms: Array.from(algosMap.values()).sort((a, b) => b.count - a.count),
      });
    });

    return result;
  }, [components]);

  if (groupedMatrix.length === 0) {
    return null;
  }

  return (
    <Card className={`cbom-matrix-card ${className}`} data-testid="cbom-algorithm-matrix">
      <div className="cbom-matrix-header">
        <div className="cbom-matrix-title-group">
          <Cpu size={18} className="matrix-icon" aria-hidden="true" />
          <h3 className="cbom-matrix-title">Algorithm Classification & Functional Families</h3>
        </div>
        <span className="matrix-badge">CycloneDX 1.6 Taxonomy</span>
      </div>

      <div className="matrix-families-grid">
        {groupedMatrix.map((group) => (
          <div key={group.familyName} className="family-column" data-testid={`family-${group.familyName}`}>
            <div className="family-header">
              <span className="family-name">{group.familyName}</span>
              <span className="family-count-badge">
                {group.algorithms.reduce((sum, a) => sum + a.count, 0)} instances
              </span>
            </div>

            <div className="family-algos-list">
              {group.algorithms.map((algoItem) => {
                const paramsList = Array.from(algoItem.parameters);
                const surfacesList = Array.from(algoItem.surfaces);

                return (
                  <div
                    key={algoItem.algorithm}
                    className="algo-card-item"
                    role="button"
                    tabIndex={0}
                    onClick={() => onSelectAlgorithm && onSelectAlgorithm(algoItem.algorithm)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        if (onSelectAlgorithm) onSelectAlgorithm(algoItem.algorithm);
                      }
                    }}
                    data-testid={`algo-item-${algoItem.algorithm}`}
                    aria-label={`Filter by ${algoItem.algorithm}`}
                  >
                    <div className="algo-card-top">
                      <span className="algo-title">{algoItem.algorithm}</span>
                      <span className="algo-count-tag">{algoItem.count}×</span>
                    </div>

                    <div className="algo-meta-row">
                      <span className="algo-purpose-pill">{algoItem.purpose}</span>
                      {paramsList.length > 0 && (
                        <span className="algo-param-pill">{paramsList.join(', ')}</span>
                      )}
                    </div>

                    <div className="algo-surfaces-row">
                      {surfacesList.map((s) => (
                        <span key={s} className="surface-micro-tag">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
