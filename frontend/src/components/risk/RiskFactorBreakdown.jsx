import React from 'react';
import Card from '../common/Card';
import { ShieldAlert, Clock, Network, Building2, Info } from 'lucide-react';
import './RiskFactorBreakdown.css';

/**
 * Standard ASTRA 4-Factor Risk Model definitions
 */
export const FACTOR_DEFINITIONS = [
  {
    key: 'algorithm_vulnerability',
    label: 'Algorithm Vulnerability',
    description: 'Inherent mathematical vulnerability to Shor’s/Grover’s algorithm and classical cryptanalysis.',
    icon: ShieldAlert,
    colorClass: 'factor-color-vulnerability',
    defaultWeight: 0.4,
  },
  {
    key: 'mosca_horizon_urgency',
    label: 'Mosca Horizon Urgency',
    description: 'Urgency computed from data retention lifespan and migration lead time against CRQC horizon.',
    icon: Clock,
    colorClass: 'factor-color-mosca',
    defaultWeight: 0.25,
  },
  {
    key: 'operational_exposure',
    label: 'Operational Exposure',
    description: 'Protocol exposure, network boundary visibility, and accessibility to active interception.',
    icon: Network,
    colorClass: 'factor-color-exposure',
    defaultWeight: 0.2,
  },
  {
    key: 'business_criticality',
    label: 'Business Criticality',
    description: 'Impact on core business services, compliance mandates, and data asset sensitivity.',
    icon: Building2,
    colorClass: 'factor-color-criticality',
    defaultWeight: 0.15,
  },
];

/**
 * Risk Factor Breakdown Component
 * Visualizes the 4 risk factors provided directly by the backend.
 * Never recalculates or modifies scores.
 *
 * @param {Object} props
 * @param {Object} [props.factors] - Specific item's factor_contributions
 * @param {Array} [props.riskEvaluations] - Array of all risk evaluations to compute observed average
 * @param {string} [props.title='Multi-Factor Risk Model Breakdown']
 * @param {string} [props.subtitle]
 * @param {string} [props.className='']
 */
export default function RiskFactorBreakdown({
  factors = null,
  riskEvaluations = [],
  title = 'Multi-Factor Risk Model Breakdown',
  subtitle = 'NIST PQC & Mosca Theorem weighted composite risk components',
  className = '',
}) {
  // If specific factors passed, use them. Otherwise compute average across evaluations if available.
  let computedFactors = factors;

  if (!computedFactors && Array.isArray(riskEvaluations) && riskEvaluations.length > 0) {
    const sums = {
      algorithm_vulnerability: 0,
      mosca_horizon_urgency: 0,
      operational_exposure: 0,
      business_criticality: 0,
    };
    let count = 0;

    riskEvaluations.forEach((item) => {
      if (item?.factor_contributions) {
        sums.algorithm_vulnerability += Number(item.factor_contributions.algorithm_vulnerability) || 0;
        sums.mosca_horizon_urgency += Number(item.factor_contributions.mosca_horizon_urgency) || 0;
        sums.operational_exposure += Number(item.factor_contributions.operational_exposure) || 0;
        sums.business_criticality += Number(item.factor_contributions.business_criticality) || 0;
        count += 1;
      }
    });

    if (count > 0) {
      computedFactors = {
        algorithm_vulnerability: (sums.algorithm_vulnerability / count),
        mosca_horizon_urgency: (sums.mosca_horizon_urgency / count),
        operational_exposure: (sums.operational_exposure / count),
        business_criticality: (sums.business_criticality / count),
      };
    }
  }

  const hasData = Boolean(computedFactors && Object.keys(computedFactors).length > 0);

  return (
    <Card className={`risk-factor-breakdown-card ${className}`} data-testid="risk-factor-breakdown">
      <div className="factor-breakdown-header">
        <div>
          <h3 className="factor-breakdown-title">{title}</h3>
          {subtitle && <p className="factor-breakdown-subtitle">{subtitle}</p>}
        </div>
        <span className="factor-model-tag">4-Factor Model</span>
      </div>

      {!hasData ? (
        <div className="factor-breakdown-empty" data-testid="factor-breakdown-empty">
          <Info size={18} aria-hidden="true" />
          <span>Factor contribution breakdown is unavailable or unassessed for this selection.</span>
        </div>
      ) : (
        <div className="factor-bars-list" role="list" aria-label="Risk factor contributions">
          {FACTOR_DEFINITIONS.map((def) => {
            const rawVal = computedFactors?.[def.key];
            const hasVal = typeof rawVal === 'number' && !Number.isNaN(rawVal);
            const val = hasVal ? rawVal : null;
            const Icon = def.icon;

            // Clamped percentage for progress bar visualization
            const barWidth = val !== null ? Math.min(100, Math.max(0, val)) : 0;

            return (
              <div
                key={def.key}
                className="factor-bar-item"
                role="listitem"
                data-testid={`factor-item-${def.key}`}
              >
                <div className="factor-bar-header">
                  <div className="factor-name-group">
                    <Icon size={16} className={`factor-icon ${def.colorClass}`} aria-hidden="true" />
                    <span className="factor-label">{def.label}</span>
                  </div>
                  <div className="factor-value-group">
                    {val !== null ? (
                      <span className="factor-value-number">{val.toFixed(1)}%</span>
                    ) : (
                      <span className="factor-value-unassessed">Unassessed</span>
                    )}
                  </div>
                </div>

                <div
                  className="factor-progress-track"
                  role="progressbar"
                  aria-valuenow={val !== null ? Math.round(val) : 0}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`${def.label} contribution`}
                >
                  <div
                    className={`factor-progress-fill ${def.colorClass}-bg`}
                    style={{ width: `${barWidth}%` }}
                  />
                </div>

                <div className="factor-desc-row">
                  <span className="factor-desc-text">{def.description}</span>
                  <span className="factor-weight-text">Base Weight: {Math.round(def.defaultWeight * 100)}%</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <div className="factor-breakdown-footer">
        <Info size={14} aria-hidden="true" style={{ flexShrink: 0, marginTop: 1 }} />
        <span>
          <strong>Backend-Governed Contributions:</strong> Factors represent normalized proportional risk
          weightings applied by the ASTRA backend engine based on NIST PQC guidelines.
        </span>
      </div>
    </Card>
  );
}
