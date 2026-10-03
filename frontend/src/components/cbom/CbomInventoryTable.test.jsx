import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import CbomInventoryTable, {
  normalizeCbomInventory,
  formatPurpose,
} from './CbomInventoryTable';

describe('CbomInventoryTable', () => {
  const mockComponents = [
    {
      id: 'comp-1',
      componentName: 'RSA-2048-crypto-service',
      assetId: 'rsa-2048-crypto_service.py-22',
      algorithm: 'RSA-2048',
      purpose: 'ASYMMETRIC',
      assetType: 'algorithm',
      parameterSetIdentifier: '2048',
      executionEnvironment: 'software-plain-ram',
      keySizeBits: 2048,
      sourceKind: 'SOURCE_CODE',
      claimType: 'ALGORITHM_USE',
      relativePath: 'crypto_service.py',
      startLine: 22,
      confidence: 'CONFIRMED',
      detectorId: 'source-code-v1',
    },
    {
      id: 'comp-2',
      componentName: 'AES-256-crypto-service',
      assetId: 'aes-256-crypto_service.py-28',
      algorithm: 'AES-256',
      purpose: 'ENCRYPTION',
      assetType: 'algorithm',
      parameterSetIdentifier: '256',
      executionEnvironment: 'software-plain-ram',
      keySizeBits: 256,
      sourceKind: 'CONFIG',
      claimType: 'CIPHER_SUITE',
      relativePath: 'nginx.conf',
      startLine: 12,
      confidence: 'INFERRED',
      detectorId: 'config-detector-v1',
    },
    {
      id: 'comp-3',
      componentName: 'MD5-crypto-service',
      assetId: 'md5-crypto_service.py-42',
      algorithm: 'MD5',
      purpose: 'HASHING',
      assetType: 'algorithm',
      parameterSetIdentifier: 'standard',
      executionEnvironment: 'software-plain-ram',
      keySizeBits: null,
      sourceKind: 'SOURCE_CODE',
      claimType: 'ALGORITHM_USE',
      relativePath: 'crypto_service.py',
      startLine: 42,
      confidence: 'HEURISTIC',
      detectorId: 'source-code-v1',
    },
  ];

  function renderWithRouter(ui) {
    return render(<MemoryRouter>{ui}</MemoryRouter>);
  }

  it('renders CBOM table with algorithm, purpose, location, parameters, and confidence', () => {
    renderWithRouter(<CbomInventoryTable components={mockComponents} />);

    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
    expect(screen.getByText('AES-256')).toBeInTheDocument();
    expect(screen.getByText('MD5')).toBeInTheDocument();

    expect(screen.getAllByText('ASYMMETRIC').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('ENCRYPTION').length).toBeGreaterThanOrEqual(1);

    expect(screen.getByText(/2048 bits/i)).toBeInTheDocument();
    expect(screen.getByText(/256 bits/i)).toBeInTheDocument();
  });

  it('filters components by search query', () => {
    renderWithRouter(<CbomInventoryTable components={mockComponents} />);

    const searchInput = screen.getByTestId('cbom-search-input');
    fireEvent.change(searchInput, { target: { value: 'nginx.conf' } });

    expect(screen.getByText('AES-256')).toBeInTheDocument();
    expect(screen.queryByText('RSA-2048')).not.toBeInTheDocument();
  });

  it('filters components by purpose and surface', () => {
    renderWithRouter(<CbomInventoryTable components={mockComponents} />);

    const purposeSelect = screen.getByTestId('cbom-purpose-filter');
    fireEvent.change(purposeSelect, { target: { value: 'HASHING' } });

    expect(screen.getByText('MD5')).toBeInTheDocument();
    expect(screen.queryByText('RSA-2048')).not.toBeInTheDocument();
  });

  it('sorts components on clicking column header', () => {
    renderWithRouter(<CbomInventoryTable components={mockComponents} />);

    const algoSortBtn = screen.getByRole('button', { name: /Algorithm & Asset/i });
    fireEvent.click(algoSortBtn);

    const rows = screen.getAllByRole('button', { name: /^Inspect CBOM component for/i });
    expect(rows.length).toBe(3);
  });

  it('triggers onSelectComponent on clicking row or inspect button', () => {
    const handleSelect = vi.fn();
    renderWithRouter(
      <CbomInventoryTable
        components={mockComponents}
        onSelectComponent={handleSelect}
      />
    );

    const inspectBtns = screen.getAllByRole('button', { name: /Inspect.*CBOM component/i });
    fireEvent.click(inspectBtns[0]);

    expect(handleSelect).toHaveBeenCalledTimes(1);
    expect(handleSelect).toHaveBeenCalledWith(
      expect.objectContaining({
        algorithm: 'AES-256',
      })
    );
  });

  it('handles keyboard navigation (Enter/Space) to select component', () => {
    const handleSelect = vi.fn();
    renderWithRouter(
      <CbomInventoryTable
        components={mockComponents}
        onSelectComponent={handleSelect}
      />
    );

    const row = screen.getByTestId('cbom-row-comp-1');
    fireEvent.keyDown(row, { key: 'Enter', code: 'Enter' });

    expect(handleSelect).toHaveBeenCalledTimes(1);
  });

  it('shows empty state when no items match and resets filters', () => {
    renderWithRouter(<CbomInventoryTable components={mockComponents} />);

    const searchInput = screen.getByTestId('cbom-search-input');
    fireEvent.change(searchInput, { target: { value: 'NO_MATCHING_PRIMITIVE' } });

    expect(screen.getByText(/No CBOM Components Match Criteria/i)).toBeInTheDocument();

    const resetBtn = screen.getByRole('button', { name: /Reset Filters/i });
    fireEvent.click(resetBtn);

    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
  });

  it('normalizeCbomInventory correctly transforms canonical assets and observations', () => {
    const canonicalAssets = [
      {
        asset_id: 'rsa-1',
        primary_name: 'RSA-2048',
        observations: [
          {
            algorithm: 'RSA-2048',
            purpose: 'ASYMMETRIC',
            source_kind: 'SOURCE_CODE',
            key_size_bits: 2048,
          },
        ],
      },
    ];

    const result = normalizeCbomInventory(canonicalAssets);
    expect(result.length).toBe(1);
    expect(result[0].algorithm).toBe('RSA-2048');
    expect(result[0].keySizeBits).toBe(2048);
  });

  it('formatPurpose formats snake_case purpose strings into title case', () => {
    expect(formatPurpose('KEY_EXCHANGE')).toBe('KEY EXCHANGE');
    expect(formatPurpose('')).toBe('General Crypto');
  });
});
