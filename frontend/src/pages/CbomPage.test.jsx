import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import CbomPage from './CbomPage';
import * as useApiModule from '../hooks/useApi';

describe('CbomPage', () => {
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
    canonical_assets: [
      {
        asset_id: 'rsa-2048-crypto_service.py-22',
        primary_name: 'RSA-2048',
        observations: [
          {
            algorithm: 'RSA-2048',
            purpose: 'ASYMMETRIC',
            key_size_bits: 2048,
            source_kind: 'SOURCE_CODE',
            claim_type: 'ALGORITHM_USE',
            relative_path: 'crypto_service.py',
            start_line: 22,
            confidence: 'CONFIRMED',
          },
        ],
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
        <CbomPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('cbom-page-loading')).toBeInTheDocument();
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
        <CbomPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('cbom-page-error')).toBeInTheDocument();
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
        <CbomPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('cbom-page-empty')).toBeInTheDocument();
  });

  it('renders CBOM summary, algorithm matrix, and inventory table', () => {
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
        <CbomPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('cbom-page')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1, name: /Cryptographic Bill of Materials/i })).toBeInTheDocument();
    expect(screen.getByTestId('cbom-summary')).toBeInTheDocument();
    expect(screen.getByTestId('cbom-algorithm-matrix')).toBeInTheDocument();
    expect(screen.getByTestId('cbom-inventory-table')).toBeInTheDocument();
  });

  it('opens component detail modal on inspect click', () => {
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
        <CbomPage />
      </MemoryRouter>
    );

    const inspectBtns = screen.getAllByRole('button', { name: /Inspect.*CBOM component/i });
    fireEvent.click(inspectBtns[0]);

    expect(screen.getByTestId('cbom-detail-modal-body')).toBeInTheDocument();
  });

  it('opens CycloneDX export modal on Export button click', () => {
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
        <CbomPage />
      </MemoryRouter>
    );

    const exportBtn = screen.getByTestId('open-export-modal-btn');
    fireEvent.click(exportBtn);

    expect(screen.getByTestId('cbom-export-modal-body')).toBeInTheDocument();
  });
});
