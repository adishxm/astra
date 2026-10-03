import { render, screen, fireEvent, within } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import RiskTable, { formatRiskScore, formatReasonCode } from './RiskTable';

describe('RiskTable', () => {
  const mockEvaluations = [
    {
      asset_id: 'rsa-2048-crypto_service.py-22',
      algorithm: 'RSA-2048',
      purpose: 'ASYMMETRIC',
      risk_score: 74.0,
      urgency: 'CRITICAL',
      mosca_condition_violated: true,
      mosca_slack_years: -12.0,
      reason_codes: ['RC_MOSCA_DEADLINE_VIOLATED_SNDL_RISK'],
    },
    {
      asset_id: 'rsa-crypto_service.py-22',
      algorithm: 'RSA',
      purpose: 'ASYMMETRIC',
      risk_score: 66.31,
      urgency: 'HIGH',
      mosca_condition_violated: false,
      mosca_slack_years: 1.0,
      reason_codes: ['RC_HIGH_COMPOSITE_RISK'],
    },
    {
      asset_id: 'aes-256-crypto_service.py-28',
      algorithm: 'AES-256',
      purpose: 'ENCRYPTION',
      risk_score: 27.0,
      urgency: 'LOW',
      mosca_condition_violated: false,
      mosca_slack_years: 1.0,
      reason_codes: ['RC_LOW_RISK_CLASSICAL'],
    },
    {
      asset_id: 'unknown-primitive-99',
      algorithm: 'CUSTOM_PRIMITIVE',
      purpose: 'UNSPECIFIED',
      risk_score: null,
      urgency: 'UNASSESSED',
      mosca_condition_violated: false,
      mosca_slack_years: null,
      reason_codes: [],
    },
  ];

  const mockBacklog = [
    {
      task_id: 'mig-123',
      asset_id: 'rsa-2048-crypto_service.py-22',
      target_pqc_algorithm: 'ML-KEM-768 (NIST FIPS 203)',
      priority: 'CRITICAL',
    },
  ];

  function renderWithRouter(ui) {
    return render(<MemoryRouter>{ui}</MemoryRouter>);
  }

  it('renders table rows and formats scores, badges, and reason codes', () => {
    renderWithRouter(<RiskTable riskEvaluations={mockEvaluations} backlogItems={mockBacklog} />);

    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
    expect(screen.getByText('74.00')).toBeInTheDocument();
    expect(screen.getByText('CRITICAL')).toBeInTheDocument();
    expect(screen.getByText('-12.0 yrs')).toBeInTheDocument();
    expect(screen.getByText('MOSCA DEADLINE VIOLATED SNDL RISK')).toBeInTheDocument();

    // Truthfulness: unassessed row does NOT show 0 or LOW
    expect(screen.getByText('CUSTOM_PRIMITIVE')).toBeInTheDocument();
    const unassessedRow = screen.getByTestId('risk-row-unknown-primitive-99');
    expect(within(unassessedRow).getAllByText('Unassessed').length).toBeGreaterThan(0);
  });

  it('filters evaluations by search query', () => {
    renderWithRouter(<RiskTable riskEvaluations={mockEvaluations} />);

    const searchInput = screen.getByTestId('risk-search-input');
    fireEvent.change(searchInput, { target: { value: 'AES-256' } });

    expect(screen.getByText('AES-256')).toBeInTheDocument();
    expect(screen.queryByText('RSA-2048')).not.toBeInTheDocument();
  });

  it('filters evaluations by urgency select', () => {
    renderWithRouter(<RiskTable riskEvaluations={mockEvaluations} />);

    const urgencySelect = screen.getByTestId('urgency-filter-select');
    fireEvent.change(urgencySelect, { target: { value: 'CRITICAL' } });

    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
    expect(screen.queryByText('AES-256')).not.toBeInTheDocument();
    expect(screen.queryByText('CUSTOM_PRIMITIVE')).not.toBeInTheDocument();
  });

  it('filters evaluations by Mosca timeline status', () => {
    renderWithRouter(<RiskTable riskEvaluations={mockEvaluations} />);

    const moscaSelect = screen.getByTestId('mosca-filter-select');
    fireEvent.change(moscaSelect, { target: { value: 'VIOLATED' } });

    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
    expect(screen.queryByText('AES-256')).not.toBeInTheDocument();
  });

  it('sorts evaluations when clicking column headers', () => {
    renderWithRouter(<RiskTable riskEvaluations={mockEvaluations} />);

    const algoSortBtn = screen.getByRole('button', { name: /Asset & Algorithm/i });
    fireEvent.click(algoSortBtn);

    const rows = screen.getAllByRole('button', { name: /^Inspect risk for/i });
    expect(rows.length).toBe(4);
  });

  it('calls onSelectRisk with item and matched backlog item when clicking row or Inspect button', () => {
    const handleSelect = vi.fn();
    renderWithRouter(
      <RiskTable
        riskEvaluations={mockEvaluations}
        backlogItems={mockBacklog}
        onSelectRisk={handleSelect}
      />
    );

    const inspectBtns = screen.getAllByRole('button', { name: /Inspect.*risk detail/i });
    fireEvent.click(inspectBtns[0]);

    expect(handleSelect).toHaveBeenCalledTimes(1);
    expect(handleSelect).toHaveBeenCalledWith(
      expect.objectContaining({
        asset_id: 'rsa-2048-crypto_service.py-22',
        backlogItem: expect.objectContaining({
          target_pqc_algorithm: 'ML-KEM-768 (NIST FIPS 203)',
        }),
      })
    );
  });

  it('handles keyboard navigation (Enter/Space) to select risk', () => {
    const handleSelect = vi.fn();
    renderWithRouter(
      <RiskTable
        riskEvaluations={mockEvaluations}
        onSelectRisk={handleSelect}
      />
    );

    const row = screen.getByTestId('risk-row-rsa-2048-crypto_service.py-22');
    fireEvent.keyDown(row, { key: 'Enter', code: 'Enter' });

    expect(handleSelect).toHaveBeenCalledTimes(1);
  });

  it('shows empty state when no evaluations match filter and allows reset', () => {
    renderWithRouter(<RiskTable riskEvaluations={mockEvaluations} />);

    const searchInput = screen.getByTestId('risk-search-input');
    fireEvent.change(searchInput, { target: { value: 'NON_EXISTENT_QUERY_12345' } });

    expect(screen.getByText(/No Risk Evaluations Match Filters/i)).toBeInTheDocument();

    const resetBtn = screen.getByRole('button', { name: /Reset Filters/i });
    fireEvent.click(resetBtn);

    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
  });

  it('helper functions format scores and reason codes truthfully', () => {
    expect(formatRiskScore(74.567)).toBe('74.57');
    expect(formatRiskScore(null)).toBe('Unassessed');
    expect(formatRiskScore(undefined)).toBe('Unassessed');
    expect(formatRiskScore(NaN)).toBe('Unassessed');

    expect(formatReasonCode('RC_ALGORITHM_BROKEN_LEGACY')).toBe('ALGORITHM BROKEN LEGACY');
    expect(formatReasonCode('')).toBe('Standard Evaluation');
  });
});
