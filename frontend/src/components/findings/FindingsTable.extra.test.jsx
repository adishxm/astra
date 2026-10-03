import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import FindingsTable, { normalizeFindings } from './FindingsTable';

describe('FindingsTable Extra Coverage', () => {
  const sampleObservations = [
    {
      observation_id: 'obs-dir-1',
      candidate_asset_id: 'rsa-direct',
      algorithm: 'RSA',
      source_kind: 'SOURCE_CODE',
      purpose: 'ASYMMETRIC',
      confidence: 'CONFIRMED',
      relative_path: 'auth.py',
      start_line: 15,
      end_line: 18,
      sanitized_excerpt: 'rsa.generate()',
      detector_id: 'py-detector',
      observed_at: '2026-10-03T10:00:00Z',
    },
    {
      observation_id: 'obs-dir-2',
      candidate_asset_id: 'ecdsa-direct',
      algorithm: 'ECDSA',
      source_kind: 'SOURCE_CODE',
      purpose: 'SIGNATURE',
      confidence: 'INFERRED',
      relative_path: 'sign.py',
      start_line: 20,
      sanitized_excerpt: 'ecdsa.sign()',
      detector_id: 'py-detector',
    },
    {
      observation_id: 'obs-dir-3',
      candidate_asset_id: 'aes-direct',
      algorithm: 'AES',
      source_kind: 'CONFIG',
      purpose: 'ENCRYPTION',
      confidence: 'HEURISTIC',
      relative_path: 'app.conf',
      start_line: 5,
      sanitized_excerpt: 'cipher=AES',
      detector_id: 'conf-detector',
    },
    {
      observation_id: 'obs-dir-4',
      candidate_asset_id: 'sha-direct',
      algorithm: 'SHA-256',
      source_kind: 'MANIFEST',
      purpose: 'HASHING',
      confidence: 'UNASSESSED',
      relative_path: 'package.json',
      start_line: null,
      sanitized_excerpt: 'sha256',
      detector_id: 'pkg-detector',
    },
    {
      observation_id: 'obs-dir-5',
      candidate_asset_id: 'cert-direct',
      algorithm: 'X509-RSA',
      source_kind: 'CERTIFICATE',
      purpose: 'IDENTITY',
      confidence: 'CONFIRMED',
      relative_path: 'server.crt',
      start_line: 1,
      sanitized_excerpt: 'Subject: CN=test',
      detector_id: 'crt-detector',
    },
  ];

  const generateMultipleObservations = (count) => {
    return Array.from({ length: count }, (_, i) => ({
      observation_id: `obs-page-${i}`,
      candidate_asset_id: `asset-${i}`,
      algorithm: `ALGO-${String(i).padStart(2, '0')}`,
      source_kind: 'SOURCE_CODE',
      purpose: 'ENCRYPTION',
      confidence: 'CONFIRMED',
      relative_path: `file_${i}.py`,
      start_line: i + 1,
      sanitized_excerpt: `code_${i}`,
      detector_id: 'py-detector',
    }));
  };

  it('normalizes direct observations with risk evaluation mapping', () => {
    const riskEvals = [
      { asset_id: 'rsa-direct', risk_score: 80, urgency: 'HIGH' },
    ];
    const items = normalizeFindings([], sampleObservations, riskEvals);
    expect(items).toHaveLength(5);
    expect(items[0].riskEvaluation).not.toBeNull();
    expect(items[0].riskEvaluation.urgency).toBe('HIGH');
  });

  it('filters by purpose dropdown', () => {
    render(<FindingsTable directObservations={sampleObservations} />);

    const purposeSelect = screen.getByLabelText(/filter by cryptographic purpose/i);
    fireEvent.change(purposeSelect, { target: { value: 'SIGNATURE' } });

    expect(screen.getByText('ECDSA')).toBeInTheDocument();
    expect(screen.queryByText('AES')).not.toBeInTheDocument();
  });

  it('navigates through multiple pages with pagination controls', () => {
    const manyObs = generateMultipleObservations(25);
    render(<FindingsTable directObservations={manyObs} />);

    // Page 1 should show ALGO-00 to ALGO-09
    expect(screen.getByText('ALGO-00')).toBeInTheDocument();
    expect(screen.getByText('ALGO-09')).toBeInTheDocument();
    expect(screen.queryByText('ALGO-10')).not.toBeInTheDocument();

    const nextBtn = screen.getByRole('button', { name: /next page/i });
    fireEvent.click(nextBtn);

    // Page 2 should show ALGO-10 to ALGO-19
    expect(screen.getByText('ALGO-10')).toBeInTheDocument();
    expect(screen.getByText('Page 2 of 3')).toBeInTheDocument();

    const prevBtn = screen.getByRole('button', { name: /previous page/i });
    fireEvent.click(prevBtn);

    // Back to Page 1
    expect(screen.getByText('ALGO-00')).toBeInTheDocument();
    expect(screen.getByText('Page 1 of 3')).toBeInTheDocument();
  });

  it('handles asset without observations in canonicalAssets', () => {
    const assetWithoutObs = [
      {
        asset_id: 'empty-asset-1',
        primary_name: 'Empty-Primitive',
        observations: [],
      },
    ];

    render(<FindingsTable canonicalAssets={assetWithoutObs} />);
    expect(screen.getByText('Empty-Primitive')).toBeInTheDocument();
  });
});
