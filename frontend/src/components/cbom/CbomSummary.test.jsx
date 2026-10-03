import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import CbomSummary from './CbomSummary';

describe('CbomSummary', () => {
  const mockComponents = [
    {
      id: 'comp-1',
      algorithm: 'RSA-2048',
      purpose: 'ASYMMETRIC',
      sourceKind: 'SOURCE_CODE',
    },
    {
      id: 'comp-2',
      algorithm: 'AES-256',
      purpose: 'ENCRYPTION',
      sourceKind: 'CONFIG',
    },
    {
      id: 'comp-3',
      algorithm: 'MD5',
      purpose: 'HASHING',
      sourceKind: 'SOURCE_CODE',
    },
    {
      id: 'comp-4',
      algorithm: 'RSA-2048',
      purpose: 'ASYMMETRIC',
      sourceKind: 'CERTIFICATE',
    },
  ];

  const mockScan = {
    target_name: 'production_sample.zip',
  };

  it('renders total components, unique algorithms, and unique purposes accurately', () => {
    render(<CbomSummary components={mockComponents} scan={mockScan} />);

    expect(screen.getByTestId('total-cbom-components')).toHaveTextContent('4');
    expect(screen.getByTestId('unique-algos-count')).toHaveTextContent('3'); // RSA-2048, AES-256, MD5
    expect(screen.getByTestId('unique-purposes-count')).toHaveTextContent('3'); // ASYMMETRIC, ENCRYPTION, HASHING
    expect(screen.getByText('CycloneDX 1.6')).toBeInTheDocument();
  });

  it('renders surface breakdown counts accurately', () => {
    render(<CbomSummary components={mockComponents} scan={mockScan} />);

    expect(screen.getByText('Source:')).toBeInTheDocument();
    expect(screen.getByText('Configs:')).toBeInTheDocument();
    expect(screen.getByText('Certificates:')).toBeInTheDocument();
  });

  it('renders truthfulness notice regarding architectural inventory vs risk', () => {
    render(<CbomSummary components={mockComponents} scan={mockScan} />);

    expect(
      screen.getByText(/Cryptographic Inventory Integrity:/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Inventory inclusion does not indicate risk severity/i)
    ).toBeInTheDocument();
  });

  it('calls onExportClick when clicking the export button', () => {
    const handleExport = vi.fn();
    render(
      <CbomSummary
        components={mockComponents}
        scan={mockScan}
        onExportClick={handleExport}
      />
    );

    const exportBtn = screen.getByTestId('export-cbom-btn');
    fireEvent.click(exportBtn);

    expect(handleExport).toHaveBeenCalledTimes(1);
  });
});
