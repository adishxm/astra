import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import RiskPage from './RiskPage';
import * as useApiModule from '../hooks/useApi';

describe('RiskPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  const mockScansList = {
    scans: [
      { scan_id: 'scan-cf529d73', target_name: 'synthetic_sample.zip' },
      { scan_id: 'scan-7fae0e1b', target_name: 'clean_state.zip' },
    ],
  };

  const mockRiskData = {
    scan_id: 'scan-cf529d73',
    risk_evaluations: [
      {
        asset_id: 'rsa-2048-crypto_service.py-22',
        algorithm: 'RSA-2048',
        purpose: 'ASYMMETRIC',
        risk_score: 74.0,
        urgency: 'CRITICAL',
        mosca_condition_violated: true,
        mosca_slack_years: -12.0,
        factor_contributions: {
          algorithm_vulnerability: 37.8,
          mosca_horizon_urgency: 33.8,
          operational_exposure: 16.2,
          business_criticality: 12.2,
        },
        reason_codes: ['RC_MOSCA_DEADLINE_VIOLATED_SNDL_RISK'],
        assumptions_applied: {
          quantum_threat_horizon_years: 3.0,
          data_shelf_life_years: 10.0,
          migration_duration_years: 5.0,
        },
      },
    ],
    backlog_items: [
      {
        task_id: 'mig-1',
        asset_id: 'rsa-2048-crypto_service.py-22',
        target_pqc_algorithm: 'ML-KEM-768',
      },
    ],
  };

  it('renders loading spinner when initial scans request is loading', () => {
    vi.spyOn(useApiModule, 'useApi').mockReturnValue({
      data: null,
      loading: true,
      error: null,
      refetch: vi.fn(),
    });

    render(
      <MemoryRouter>
        <RiskPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('risk-page-loading')).toBeInTheDocument();
  });

  it('renders error banner when scans request fails', () => {
    vi.spyOn(useApiModule, 'useApi').mockReturnValue({
      data: null,
      loading: false,
      error: 'Network connection error',
      refetch: vi.fn(),
    });

    render(
      <MemoryRouter>
        <RiskPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('risk-page-error')).toBeInTheDocument();
  });

  it('renders empty state when no scans are returned', () => {
    vi.spyOn(useApiModule, 'useApi').mockReturnValue({
      data: { scans: [] },
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    render(
      <MemoryRouter>
        <RiskPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('risk-page-empty')).toBeInTheDocument();
  });

  it('renders risk assessment dashboard, summary, breakdown, and table', () => {
    vi.spyOn(useApiModule, 'useApi').mockImplementation((path) => {
      if (path === '/api/v1/scans') {
        return {
          data: mockScansList,
          loading: false,
          error: null,
          refetch: vi.fn(),
        };
      }
      return {
        data: mockRiskData,
        loading: false,
        error: null,
        refetch: vi.fn(),
      };
    });

    render(
      <MemoryRouter>
        <RiskPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('risk-page')).toBeInTheDocument();
    expect(screen.getByText('Cryptographic Risk Assessment')).toBeInTheDocument();
    expect(screen.getByTestId('scan-picker-select')).toBeInTheDocument();
    expect(screen.getByTestId('risk-summary')).toBeInTheDocument();
    expect(screen.getByTestId('risk-factor-breakdown')).toBeInTheDocument();
    expect(screen.getByTestId('risk-table-container')).toBeInTheDocument();
  });

  it('allows toggling Mosca scenario simulation controls and applying params', () => {
    vi.spyOn(useApiModule, 'useApi').mockImplementation((path) => {
      if (path === '/api/v1/scans') {
        return {
          data: mockScansList,
          loading: false,
          error: null,
          refetch: vi.fn(),
        };
      }
      return {
        data: mockRiskData,
        loading: false,
        error: null,
        refetch: vi.fn(),
      };
    });

    render(
      <MemoryRouter>
        <RiskPage />
      </MemoryRouter>
    );

    const toggleBtn = screen.getByTestId('toggle-simulation-btn');
    fireEvent.click(toggleBtn);

    expect(screen.getByTestId('simulation-controls-card')).toBeInTheDocument();

    const applyBtn = screen.getByTestId('apply-simulation-btn');
    fireEvent.click(applyBtn);

    expect(screen.getByTestId('reset-simulation-btn')).toBeInTheDocument();
  });

  it('opens RiskDetailModal on inspect click', () => {
    vi.spyOn(useApiModule, 'useApi').mockImplementation((path) => {
      if (path === '/api/v1/scans') {
        return {
          data: mockScansList,
          loading: false,
          error: null,
          refetch: vi.fn(),
        };
      }
      return {
        data: mockRiskData,
        loading: false,
        error: null,
        refetch: vi.fn(),
      };
    });

    render(
      <MemoryRouter>
        <RiskPage />
      </MemoryRouter>
    );

    const inspectBtn = screen.getByRole('button', { name: /Inspect.*risk detail/i });
    fireEvent.click(inspectBtn);

    expect(screen.getByTestId('risk-detail-modal-body')).toBeInTheDocument();
  });
});
