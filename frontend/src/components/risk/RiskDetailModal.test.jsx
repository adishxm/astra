import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import RiskDetailModal from './RiskDetailModal';

describe('RiskDetailModal', () => {
  const mockEvaluation = {
    asset_id: 'rsa-2048-crypto_service.py-22',
    algorithm: 'RSA-2048',
    purpose: 'ASYMMETRIC',
    risk_score: 74.0,
    urgency: 'CRITICAL',
    mosca_condition_violated: true,
    mosca_slack_years: -12.0,
    evaluated_at: '2026-10-03T16:58:45.449871+00:00',
    factor_contributions: {
      algorithm_vulnerability: 37.8,
      mosca_horizon_urgency: 33.8,
      operational_exposure: 16.2,
      business_criticality: 12.2,
    },
    reason_codes: ['RC_MOSCA_DEADLINE_VIOLATED_SNDL_RISK', 'RC_HIGH_COMPOSITE_RISK'],
    assumptions_applied: {
      scenario_id: 'standard-2034-horizon',
      quantum_threat_horizon_years: 3.0,
      data_shelf_life_years: 10.0,
      migration_duration_years: 5.0,
      context_source: 'DEFAULT_ASSUMPTION',
      ruleset_version: '2026.10-nist-pqc',
      scenario_caveat: 'Mosca urgency reflects scenario simulation assumptions.',
    },
    backlogItem: {
      task_id: 'mig-2e42289f',
      target_pqc_algorithm: 'ML-KEM-768 (NIST FIPS 203)',
      dated_standard_ref: 'NIST FIPS 203 (Aug 2024)',
      priority: 'CRITICAL',
      recommended_action: 'Replace RSA-2048 with ML-KEM-768 for quantum-resistant key encapsulation',
      compatibility_gaps: ['Ciphertext size increases from 256 bytes to 1088 bytes'],
      operational_benchmarking_caveat: 'Advisory candidate mapping from NIST standards.',
    },
  };

  it('renders nothing when closed or evaluation is null', () => {
    const { container } = render(
      <RiskDetailModal open={false} evaluation={mockEvaluation} onClose={() => {}} />
    );
    expect(container).toBeEmptyDOMElement();
  });

  it('renders full evaluation details, scores, and SNDL warning when open', () => {
    render(
      <RiskDetailModal open={true} evaluation={mockEvaluation} onClose={() => {}} />
    );

    expect(screen.getByText('Risk Assessment: RSA-2048')).toBeInTheDocument();
    expect(screen.getByText('74.00')).toBeInTheDocument();
    expect(screen.getByText('CRITICAL')).toBeInTheDocument();
    expect(screen.getByText('SNDL VIOLATION')).toBeInTheDocument();

    // Mosca timeline analysis
    expect(screen.getByText('-12.0 yrs')).toBeInTheDocument();
    expect(screen.getByText(/Store Now, Decrypt Later \(SNDL\) Critical Warning/i)).toBeInTheDocument();

    // Reason codes
    expect(screen.getByTestId('reason-code-RC_MOSCA_DEADLINE_VIOLATED_SNDL_RISK')).toBeInTheDocument();
    expect(screen.getByTestId('reason-code-RC_HIGH_COMPOSITE_RISK')).toBeInTheDocument();

    // Backlog item
    expect(screen.getByText('ML-KEM-768 (NIST FIPS 203)')).toBeInTheDocument();
    expect(screen.getByText(/Ciphertext size increases from 256 bytes to 1088 bytes/i)).toBeInTheDocument();
  });

  it('truthfulness: renders unassessed score and state neutrally when score is missing', () => {
    const unassessedItem = {
      asset_id: 'unassessed-asset-01',
      algorithm: 'CUSTOM_ALGORITHM',
      purpose: 'UNKNOWN',
      risk_score: null,
      urgency: 'UNASSESSED',
    };

    render(
      <RiskDetailModal open={true} evaluation={unassessedItem} onClose={() => {}} />
    );

    expect(screen.getAllByText('Unassessed').length).toBeGreaterThan(0);
    expect(screen.getByText('Score unavailable')).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const handleClose = vi.fn();
    render(
      <RiskDetailModal open={true} evaluation={mockEvaluation} onClose={handleClose} />
    );

    const closeBtn = screen.getByRole('button', { name: /Close risk detail dialog/i });
    fireEvent.click(closeBtn);

    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
