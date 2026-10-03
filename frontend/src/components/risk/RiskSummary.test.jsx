import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, it, expect } from 'vitest';
import RiskSummary, { getUrgencyBadgeVariant } from './RiskSummary';

describe('RiskSummary', () => {
  const mockEvaluations = [
    {
      asset_id: 'rsa-2048-crypto.py-22',
      algorithm: 'RSA-2048',
      risk_score: 74.0,
      urgency: 'CRITICAL',
      mosca_condition_violated: true,
      mosca_slack_years: -12.0,
      assumptions_applied: {
        quantum_threat_horizon_years: 3.0,
        data_shelf_life_years: 10.0,
        migration_duration_years: 5.0,
        ruleset_version: '2026.10-nist-pqc',
      },
    },
    {
      asset_id: 'rsa-1024-crypto.py-25',
      algorithm: 'RSA-1024',
      risk_score: 85.0,
      urgency: 'HIGH',
      mosca_condition_violated: false,
      mosca_slack_years: 1.0,
    },
    {
      asset_id: 'aes-128-crypto.py-30',
      algorithm: 'AES-128',
      risk_score: 45.0,
      urgency: 'MEDIUM',
      mosca_condition_violated: false,
      mosca_slack_years: 1.0,
    },
    {
      asset_id: 'aes-256-crypto.py-35',
      algorithm: 'AES-256',
      risk_score: 20.0,
      urgency: 'LOW',
      mosca_condition_violated: false,
      mosca_slack_years: 1.0,
    },
    {
      asset_id: 'unknown-hash.py-40',
      algorithm: 'CUSTOM_ALGO',
      risk_score: null,
      urgency: 'UNASSESSED',
    },
  ];

  it('renders total evaluations and counts for all urgency levels correctly', () => {
    render(<RiskSummary riskEvaluations={mockEvaluations} />);

    expect(screen.getByTestId('total-risk-items')).toHaveTextContent('5');
    expect(screen.getByTestId('crit-count')).toHaveTextContent('1');
    expect(screen.getByTestId('high-count')).toHaveTextContent('1');
    expect(screen.getByTestId('med-count')).toHaveTextContent('1');
    expect(screen.getByTestId('low-count')).toHaveTextContent('1');
    expect(screen.getByTestId('unassessed-count')).toHaveTextContent('1');
  });

  it('truthfulness: ensures unassessed items do NOT get classified as low, 0, or safe', () => {
    const unassessedEvaluations = [
      {
        asset_id: 'asset-unknown-1',
        algorithm: 'UNKNOWN_PRIMITIVE',
        risk_score: null,
        urgency: null,
      },
      {
        asset_id: 'asset-unknown-2',
        algorithm: 'CUSTOM_PRIMITIVE',
        risk_score: undefined,
        urgency: 'UNASSESSED',
      },
    ];

    render(<RiskSummary riskEvaluations={unassessedEvaluations} />);

    expect(screen.getByTestId('crit-count')).toHaveTextContent('0');
    expect(screen.getByTestId('low-count')).toHaveTextContent('0');
    expect(screen.getByTestId('unassessed-count')).toHaveTextContent('2');
  });

  it('renders Mosca violation warning when mosca_condition_violated is true', () => {
    render(<RiskSummary riskEvaluations={mockEvaluations} />);

    expect(screen.getByText(/MOSCA VIOLATION: SNDL RISK/i)).toBeInTheDocument();
    expect(screen.getByTestId('mosca-violation-warning')).toBeInTheDocument();
    expect(screen.getByText('-12.0 yrs')).toBeInTheDocument();
  });

  it('renders Mosca compliant state when all evaluations are compliant', () => {
    const compliantEvaluations = [
      {
        asset_id: 'aes-256-crypto.py-35',
        algorithm: 'AES-256',
        risk_score: 20.0,
        urgency: 'LOW',
        mosca_condition_violated: false,
        mosca_slack_years: 1.0,
        assumptions_applied: {
          quantum_threat_horizon_years: 8.0,
          data_shelf_life_years: 5.0,
          migration_duration_years: 2.0,
        },
      },
    ];

    render(<RiskSummary riskEvaluations={compliantEvaluations} />);

    expect(screen.getByText(/MOSCA COMPLIANT/i)).toBeInTheDocument();
    expect(screen.getByText('+1.0 yrs')).toBeInTheDocument();
    expect(screen.queryByTestId('mosca-violation-warning')).not.toBeInTheDocument();
  });

  it('getUrgencyBadgeVariant maps urgency levels accurately', () => {
    expect(getUrgencyBadgeVariant('CRITICAL')).toBe('critical');
    expect(getUrgencyBadgeVariant('HIGH')).toBe('high');
    expect(getUrgencyBadgeVariant('MEDIUM')).toBe('medium');
    expect(getUrgencyBadgeVariant('LOW')).toBe('low');
    expect(getUrgencyBadgeVariant('UNASSESSED')).toBe('unknown');
    expect(getUrgencyBadgeVariant(null)).toBe('unknown');
    expect(getUrgencyBadgeVariant(undefined)).toBe('unknown');
  });
});
