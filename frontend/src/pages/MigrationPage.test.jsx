import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import MigrationPage from './MigrationPage';
import * as useApiModule from '../hooks/useApi';

describe('MigrationPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  const mockScansList = {
    scans: [
      { scan_id: 'scan-cf529d73', target_name: 'synthetic_sample.zip' },
    ],
  };

  const mockScanDetail = {
    scan_id: 'scan-cf529d73',
    target_name: 'synthetic_sample.zip',
    backlog_items: [
      {
        task_id: 'mig-task-1',
        asset_id: 'rsa-2048-crypto_service.py-22',
        current_algorithm: 'RSA-2048',
        purpose: 'ASYMMETRIC',
        priority: 'HIGH',
        composite_risk_score: 66.3,
        target_pqc_algorithm: 'ML-KEM-768 (FIPS 203)',
        target_hybrid_algorithm: 'Hybrid X25519 + ML-KEM-768',
        dated_standard_ref: 'NIST FIPS 203 (Aug 2024)',
        relative_path: 'crypto_service.py',
        start_line: 22,
        status: 'OPEN',
        recommended_action: 'Plan upgrade to ML-KEM-768',
        compatibility_gaps: ['Public key expands to 1184 bytes'],
      },
    ],
  };

  it('renders loading spinner when scans list is loading', () => {
    vi.spyOn(useApiModule, 'useApi').mockReturnValue({
      data: null,
      loading: true,
      error: null,
      refetch: vi.fn(),
    });

    render(
      <MemoryRouter>
        <MigrationPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('migration-page-loading')).toBeInTheDocument();
  });

  it('renders error banner when scans request fails', () => {
    vi.spyOn(useApiModule, 'useApi').mockReturnValue({
      data: null,
      loading: false,
      error: 'Network connection failed',
      refetch: vi.fn(),
    });

    render(
      <MemoryRouter>
        <MigrationPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('migration-page-error')).toBeInTheDocument();
  });

  it('renders empty state when no scans exist', () => {
    vi.spyOn(useApiModule, 'useApi').mockReturnValue({
      data: { scans: [] },
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    render(
      <MemoryRouter>
        <MigrationPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('migration-page-empty')).toBeInTheDocument();
  });

  it('renders Migration Summary, Roadmap View, and Recommendation Table', () => {
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
        data: mockScanDetail,
        loading: false,
        error: null,
        refetch: vi.fn(),
      };
    });

    render(
      <MemoryRouter>
        <MigrationPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('migration-page')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1, name: /Migration Planning & Recommendations/i })).toBeInTheDocument();
    expect(screen.getByTestId('migration-summary')).toBeInTheDocument();
    expect(screen.getByTestId('migration-roadmap-view')).toBeInTheDocument();
    expect(screen.getByTestId('migration-table')).toBeInTheDocument();
  });

  it('opens migration detail modal on clicking inspect button', () => {
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
        data: mockScanDetail,
        loading: false,
        error: null,
        refetch: vi.fn(),
      };
    });

    render(
      <MemoryRouter>
        <MigrationPage />
      </MemoryRouter>
    );

    const inspectBtns = screen.getAllByRole('button', { name: /Inspect.*recommendation/i });
    fireEvent.click(inspectBtns[0]);

    expect(screen.getByTestId('migration-detail-modal-body')).toBeInTheDocument();
  });
});
