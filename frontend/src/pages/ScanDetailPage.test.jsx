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
      total_unsupported_files: 0,
      total_skipped_files: 0,
      total_failed_files: 0,
      total_observations_found: 2,
      scan_status_label: 'COMPLETE_WITH_COVERAGE_ACCOUNTING',
      surface_breakdown: {
        SOURCE_CODE: {
          surface: 'SOURCE_CODE',
          total_files: 1,
          assessed_files: 1,
          files_with_findings: 1,
          files_with_no_findings: 0,
          unsupported_files: 0,
          failed_files: 0,
          coverage_percentage: 100.0,
        },
      },
      unsupported_extensions: ['.md'],
      collector_health: {
        'detector-source-code-v1': 'OK',
      },
    },
    manifest: {
      files: [
        {
          relative_path: 'crypto.py',
          size_bytes: 500,
          file_extension: '.py',
          is_supported: true,
          skip_reason: null,
        },
        {
          relative_path: 'docs.md',
          size_bytes: 300,
          file_extension: '.md',
          is_supported: false,
          skip_reason: null,
        },
      ],
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

  it('renders complete scan details, metrics, and switches between tabs', () => {
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

    // Default tab: Findings
    expect(screen.getByText('RSA-2048')).toBeInTheDocument();

    // Switch to CBOM tab
    const cbomTab = screen.getByRole('tab', { name: /cbom/i });
    fireEvent.click(cbomTab);
    expect(screen.getByTestId('cbom-summary')).toBeInTheDocument();
    expect(screen.getByTestId('cbom-algorithm-matrix')).toBeInTheDocument();
    expect(screen.getByTestId('cbom-inventory-table')).toBeInTheDocument();

    // Switch to Risk Assessment tab
    const riskTab = screen.getByRole('tab', { name: /risk assessment/i });
    fireEvent.click(riskTab);
    expect(screen.getByTestId('risk-summary')).toBeInTheDocument();
    expect(screen.getByTestId('risk-factor-breakdown')).toBeInTheDocument();
    expect(screen.getByTestId('risk-table-container')).toBeInTheDocument();

    // Switch to Coverage & Accounting tab
    const coverageTab = screen.getByRole('tab', { name: /coverage & accounting/i });
    fireEvent.click(coverageTab);
    expect(screen.getByTestId('coverage-overview')).toBeInTheDocument();

    // Switch to Discovery Surfaces tab
    const surfacesTab = screen.getByRole('tab', { name: /discovery surfaces/i });
    fireEvent.click(surfacesTab);
    expect(screen.getByTestId('surface-breakdown')).toBeInTheDocument();

    // Switch to Coverage Gaps tab
    const gapsTab = screen.getByRole('tab', { name: /coverage gaps/i });
    fireEvent.click(gapsTab);
    expect(screen.getByTestId('coverage-gaps-table')).toBeInTheDocument();
    expect(screen.getByText('docs.md')).toBeInTheDocument();

    // Switch to Engine Health tab
    const healthTab = screen.getByRole('tab', { name: /engine health/i });
    fireEvent.click(healthTab);
    expect(screen.getByTestId('collector-health')).toBeInTheDocument();
    expect(screen.getByText('detector-source-code-v1')).toBeInTheDocument();
  });

  it('opens finding detail modal with evidence inspection', () => {
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
    expect(screen.getByText(/Observed Raw Evidence/i)).toBeInTheDocument();
  });
});
