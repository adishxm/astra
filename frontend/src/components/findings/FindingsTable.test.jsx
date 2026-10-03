import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import FindingsTable, { normalizeFindings } from './FindingsTable';

describe('FindingsTable', () => {
  const sampleCanonicalAssets = [
    {
      asset_id: 'rsa-2048-crypto.py-10',
      primary_name: 'RSA-2048',
      observations: [
        {
          canonical_id: 'canon-1',
          asset_id: 'rsa-2048-crypto.py-10',
          claim_type: 'ALGORITHM_USE',
          source_kind: 'SOURCE_CODE',
          algorithm: 'RSA-2048',
          purpose: 'ASYMMETRIC',
          key_size_bits: 2048,
          confidence: 'CONFIRMED',
          confidence_rationale: 'Pattern match in Python source',
          relative_path: 'crypto.py',
          start_line: 10,
          sanitized_excerpt: 'crypto.generate_key("RSA-2048")',
          detector_id: 'source-detector-v1',
        },
      ],
    },
    {
      asset_id: 'aes-128-config.json-2',
      primary_name: 'AES-128',
      observations: [
        {
          canonical_id: 'canon-2',
          asset_id: 'aes-128-config.json-2',
          claim_type: 'CONFIG_PARAMETER',
          source_kind: 'CONFIG',
          algorithm: 'AES-128',
          purpose: 'ENCRYPTION',
          key_size_bits: 128,
          confidence: 'HIGH',
          relative_path: 'config.json',
          start_line: 2,
          sanitized_excerpt: '"cipher": "AES-128"',
          detector_id: 'config-detector-v1',
        },
      ],
    },
    {
      asset_id: 'md5-legacy.py-40',
      primary_name: 'MD5',
      observations: [
        {
          canonical_id: 'canon-3',
          asset_id: 'md5-legacy.py-40',
          claim_type: 'ALGORITHM_USE',
          source_kind: 'SOURCE_CODE',
          algorithm: 'MD5',
          purpose: 'HASHING',
          key_size_bits: null,
          confidence: 'UNASSESSED',
          relative_path: 'legacy.py',
          start_line: 40,
          sanitized_excerpt: 'hashlib.md5(data)',
          detector_id: 'source-detector-v1',
        },
      ],
    },
  ];

  it('normalizes canonical assets into flat findings array', () => {
    const items = normalizeFindings(sampleCanonicalAssets);
    expect(items).toHaveLength(3);
    expect(items[0].algorithm).toBe('RSA-2048');
    expect(items[0].sourceKind).toBe('SOURCE_CODE');
    expect(items[0].confidence).toBe('CONFIRMED');
    expect(items[0].relativePath).toBe('crypto.py');
  });

  it('renders table headers and finding rows correctly', () => {
    render(<FindingsTable canonicalAssets={sampleCanonicalAssets} />);

    expect(screen.getByRole('search', { name: /findings filters/i })).toBeInTheDocument();
    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
    expect(screen.getByText('AES-128')).toBeInTheDocument();
    expect(screen.getByText('MD5')).toBeInTheDocument();
    expect(screen.getByText('crypto.py:10')).toBeInTheDocument();
  });

  it('filters rows by text search', () => {
    render(<FindingsTable canonicalAssets={sampleCanonicalAssets} />);

    const searchInput = screen.getByLabelText(/search findings/i);
    fireEvent.change(searchInput, { target: { value: 'AES' } });

    expect(screen.getByText('AES-128')).toBeInTheDocument();
    expect(screen.queryByText('RSA-2048')).not.toBeInTheDocument();
    expect(screen.queryByText('MD5')).not.toBeInTheDocument();
  });

  it('filters rows by source surface dropdown', () => {
    render(<FindingsTable canonicalAssets={sampleCanonicalAssets} />);

    const sourceSelect = screen.getByLabelText(/filter by source type/i);
    fireEvent.change(sourceSelect, { target: { value: 'CONFIG' } });

    expect(screen.getByText('AES-128')).toBeInTheDocument();
    expect(screen.queryByText('RSA-2048')).not.toBeInTheDocument();
  });

  it('filters rows by confidence dropdown', () => {
    render(<FindingsTable canonicalAssets={sampleCanonicalAssets} />);

    const confSelect = screen.getByLabelText(/filter by confidence/i);
    fireEvent.change(confSelect, { target: { value: 'CONFIRMED' } });

    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
    expect(screen.queryByText('AES-128')).not.toBeInTheDocument();
  });

  it('resets filters when clicking Reset Filters button', () => {
    render(<FindingsTable canonicalAssets={sampleCanonicalAssets} />);

    const searchInput = screen.getByLabelText(/search findings/i);
    fireEvent.change(searchInput, { target: { value: 'NonExistent' } });

    expect(screen.getByText(/no findings match your search/i)).toBeInTheDocument();

    const resetBtn = screen.getByRole('button', { name: /clear all applied filters/i });
    fireEvent.click(resetBtn);

    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
    expect(screen.getByText('AES-128')).toBeInTheDocument();
  });

  it('sorts rows when clicking column headers', () => {
    render(<FindingsTable canonicalAssets={sampleCanonicalAssets} />);

    const algoHeader = screen.getByRole('columnheader', { name: /algorithm/i });
    // Default asc: AES-128, MD5, RSA-2048
    fireEvent.click(algoHeader); // Toggles to desc: RSA-2048, MD5, AES-128
    const rows = screen.getAllByRole('button', { name: /view details for/i });
    expect(rows[0]).toHaveTextContent('RSA-2048');
  });

  it('triggers onSelectFinding on row click and Enter key', () => {
    const onSelect = vi.fn();
    render(<FindingsTable canonicalAssets={sampleCanonicalAssets} onSelectFinding={onSelect} />);

    const row = screen.getAllByRole('button', { name: /view details for/i })[0];
    fireEvent.click(row);
    expect(onSelect).toHaveBeenCalledTimes(1);

    fireEvent.keyDown(row, { key: 'Enter', code: 'Enter' });
    expect(onSelect).toHaveBeenCalledTimes(2);
  });

  it('renders empty table message when empty', () => {
    render(<FindingsTable canonicalAssets={[]} />);
    expect(screen.getByText(/no cryptographic findings discovered/i)).toBeInTheDocument();
  });
});
