import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import ScanDetailPage from './ScanDetailPage';
import * as useApiModule from '../hooks/useApi';

vi.mock('../hooks/useApi');

describe('ScanDetailPage', () => {
  const mockScanDetail = {
    scan_id: 'scan-cf529d73',
    status: 'completed',
    target_name: 'synthetic_sample.zip',
    created_at: '2026-10-03T16:58:45Z',
    asset_count: 2,
    coverage_percentage: 100.0,
    clean_state_label: 'COMPLETE_WITH_COVERAGE_ACCOUNTING',
    cryptographic_dna_hash: 'edcb54e8c8b2e04a1380807d36d5b7a43ca3c25f4cff275073214177e8a67875',
    summary: {
      total_files: 2,
      assessed_files: 2,
      coverage_percentage: 100.0,
      clean_state_label: 'COMPLETE_WITH_COVERAGE_ACCOUNTING',
      critical_urgency_count: 0,
      high_urgency_count: 1,
      medium_urgency_count: 1,
      low_urgency_count: 0,
    },
    coverage: {
      overall_coverage_percentage: 100.0,
      total_files_in_archive: 2,
      total_assessed_files: 2,
      surface_breakdown: {
        SOURCE_CODE: {
          surface: 'SOURCE_CODE',
          total_files: 1,
          assessed_files: 1,
          files_with_findings: 1,
          coverage_percentage: 100.0,
        },
      },
    },
    canonical_assets: [
      {
        asset_id: 'rsa-2048-crypto.py-1',
        primary_name: 'RSA-2048',
        observations: [
          {
            canonical_id: 'obs-1',
            asset_id: 'rsa-2048-crypto.py-1',
            algorithm: 'RSA-2048',
            source_kind: 'SOURCE_CODE',
            purpose: 'ASYMMETRIC',
            confidence: 'CONFIRMED',
            relative_path: 'crypto.py',
            start_line: 1,
            sanitized_excerpt: 'RSA.generate(2048)',
            detector_id: 'source-detector-v1',
          },
        ],
      },
    ],
    risk_evaluations: [
      {
        asset_id: 'rsa-2048-crypto.py-1',
        algorithm: 'RSA-2048',
        risk_score: 64.3,
        urgency: 'HIGH',
      },
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  function renderWithRouter(scanId = 'scan-cf529d73') {
    return render(
      <MemoryRouter initialEntries={[`/scans/${scanId}`]}>
        <Routes>
          <Route path="/scans/:scanId" element={<ScanDetailPage />} />
        </Routes>
      </MemoryRouter>
    );
  }

  it('renders loading spinner when useApi is loading', () => {
    vi.spyOn(useApiModule, 'useApi').mockReturnValue({
      data: null,
      loading: true,
      error: null,
      refetch: vi.fn(),
    });

    renderWithRouter();
    expect(screen.getByTestId('scan-detail-loading')).toBeInTheDocument();
    expect(screen.getByText(/loading scan results/i)).toBeInTheDocument();
  });

  it('renders error banner and retry on API error', () => {
    const refetch = vi.fn();
    vi.spyOn(useApiModule, 'useApi').mockReturnValue({
      data: null,
      loading: false,
      error: 'Failed to connect to engine',
      refetch,
    });

    renderWithRouter();
    expect(screen.getByTestId('scan-detail-error')).toBeInTheDocument();
    expect(screen.getByText(/Failed to connect to engine/i)).toBeInTheDocument();

    const retryBtn = screen.getByRole('button', { name: /retry/i });
    fireEvent.click(retryBtn);
    expect(refetch).toHaveBeenCalled();
  });

  it('renders empty state if scan record is not found', () => {
    vi.spyOn(useApiModule, 'useApi').mockReturnValue({
      data: null,
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderWithRouter('non-existent-scan');
    expect(screen.getByTestId('scan-detail-notfound')).toBeInTheDocument();
    expect(screen.getByText(/scan result unavailable/i)).toBeInTheDocument();
  });

  it('renders complete scan details, metrics, surfaces, and findings table', () => {
    vi.spyOn(useApiModule, 'useApi').mockReturnValue({
      data: mockScanDetail,
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderWithRouter();

    expect(screen.getByTestId('scan-detail-page')).toBeInTheDocument();
    expect(screen.getByText('synthetic_sample.zip')).toBeInTheDocument();
    expect(screen.getByText('COMPLETED')).toBeInTheDocument();
    expect(screen.getByText(/edcb54e8c8b2e04a1380807d36d5b7a43ca3c25f4cff275073214177e8a67875/i)).toBeInTheDocument();
    expect(screen.getByText('COMPLETE_WITH_COVERAGE_ACCOUNTING')).toBeInTheDocument();
    expect(screen.getAllByText('SOURCE_CODE')[0]).toBeInTheDocument();
    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
  });

  it('opens finding detail modal when clicking Inspect on a finding', () => {
    vi.spyOn(useApiModule, 'useApi').mockReturnValue({
      data: mockScanDetail,
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderWithRouter();

    const inspectBtn = screen.getByRole('button', { name: /inspect evidence for rsa-2048/i });
    fireEvent.click(inspectBtn);

    expect(screen.getByText(/Finding Details: RSA-2048/i)).toBeInTheDocument();
    expect(screen.getByText(/RSA.generate\(2048\)/i)).toBeInTheDocument();
  });
});
