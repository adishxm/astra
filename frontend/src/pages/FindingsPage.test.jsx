import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import FindingsPage from './FindingsPage';
import * as useApiModule from '../hooks/useApi';

vi.mock('../hooks/useApi');

describe('FindingsPage', () => {
  const mockScansList = [
    {
      scan_id: 'scan-001',
      target_name: 'repo-alpha.zip',
      asset_count: 5,
    },
    {
      scan_id: 'scan-002',
      target_name: 'repo-beta.zip',
      asset_count: 2,
    },
  ];

  const mockFindingsData = {
    scan_id: 'scan-001',
    asset_count: 1,
    canonical_assets: [
      {
        asset_id: 'ecdsa-p256-auth.go-15',
        primary_name: 'ECDSA-P256',
        observations: [
          {
            canonical_id: 'obs-ecdsa',
            asset_id: 'ecdsa-p256-auth.go-15',
            algorithm: 'ECDSA-P256',
            source_kind: 'SOURCE_CODE',
            purpose: 'SIGNATURE',
            confidence: 'CONFIRMED',
            relative_path: 'auth.go',
            start_line: 15,
            sanitized_excerpt: 'ecdsa.GenerateKey(elliptic.P256(), rand.Reader)',
            detector_id: 'source-detector-v1',
          },
        ],
      },
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  function renderWithRouter() {
    return render(
      <MemoryRouter initialEntries={['/findings']}>
        <FindingsPage />
      </MemoryRouter>
    );
  }

  it('renders loading state when scans are loading', () => {
    vi.spyOn(useApiModule, 'useApi').mockImplementation((url) => {
      if (url === '/api/v1/scans') {
        return { data: null, loading: true, error: null, refetch: vi.fn() };
      }
      return { data: null, loading: false, error: null, refetch: vi.fn() };
    });

    renderWithRouter();
    expect(screen.getByTestId('findings-page-loading')).toBeInTheDocument();
  });

  it('renders error state when scan fetch fails', () => {
    vi.spyOn(useApiModule, 'useApi').mockImplementation((url) => {
      if (url === '/api/v1/scans') {
        return { data: null, loading: false, error: 'Network error', refetch: vi.fn() };
      }
      return { data: null, loading: false, error: null, refetch: vi.fn() };
    });

    renderWithRouter();
    expect(screen.getByTestId('findings-page-error')).toBeInTheDocument();
    expect(screen.getByText(/Failed to load scans/i)).toBeInTheDocument();
  });

  it('renders empty state when no scans exist', () => {
    vi.spyOn(useApiModule, 'useApi').mockImplementation((url) => {
      if (url === '/api/v1/scans') {
        return { data: [], loading: false, error: null, refetch: vi.fn() };
      }
      return { data: null, loading: false, error: null, refetch: vi.fn() };
    });

    renderWithRouter();
    expect(screen.getByTestId('findings-page-empty')).toBeInTheDocument();
    expect(screen.getByText(/No Cryptographic Scans Available/i)).toBeInTheDocument();
  });

  it('renders scan selector and findings table when scans exist', () => {
    vi.spyOn(useApiModule, 'useApi').mockImplementation((url) => {
      if (url === '/api/v1/scans') {
        return { data: mockScansList, loading: false, error: null, refetch: vi.fn() };
      }
      if (url?.includes('/findings')) {
        return { data: mockFindingsData, loading: false, error: null, refetch: vi.fn() };
      }
      return { data: null, loading: false, error: null, refetch: vi.fn() };
    });

    renderWithRouter();
    expect(screen.getByTestId('findings-page')).toBeInTheDocument();
    expect(screen.getByLabelText(/select target scan/i)).toBeInTheDocument();
    expect(screen.getByText('repo-alpha.zip (5 assets)')).toBeInTheDocument();
    expect(screen.getByText('ECDSA-P256')).toBeInTheDocument();
  });

  it('updates scan selection on change', () => {
    vi.spyOn(useApiModule, 'useApi').mockImplementation((url) => {
      if (url === '/api/v1/scans') {
        return { data: mockScansList, loading: false, error: null, refetch: vi.fn() };
      }
      if (url === '/api/v1/scans/scan-001/findings') {
        return { data: mockFindingsData, loading: false, error: null, refetch: vi.fn() };
      }
      return { data: null, loading: false, error: null, refetch: vi.fn() };
    });

    renderWithRouter();
    const select = screen.getByLabelText(/select target scan/i);
    fireEvent.change(select, { target: { value: 'scan-002' } });
    expect(select.value).toBe('scan-002');
  });
});
