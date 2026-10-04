import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import CbomAlgorithmMatrix, { getAlgorithmFamily } from './CbomAlgorithmMatrix';

describe('CbomAlgorithmMatrix', () => {
  const mockComponents = [
    { algorithm: 'ML-KEM-768', purpose: 'KEY_EXCHANGE', keySizeBits: 768, sourceKind: 'SOURCE_CODE' },
    { algorithm: 'RSA-2048', purpose: 'ASYMMETRIC', keySizeBits: 2048, sourceKind: 'SOURCE_CODE' },
    { algorithm: 'AES-256', purpose: 'ENCRYPTION', keySizeBits: 256, sourceKind: 'CONFIG' },
    { algorithm: 'MD5', purpose: 'HASHING', keySizeBits: null, sourceKind: 'SOURCE_CODE' },
    { algorithm: 'TLSv1.3', purpose: 'PROTOCOL_VERSION', keySizeBits: null, sourceKind: 'CONFIG' },
  ];

  it('renders algorithm families matrix grouped accurately', () => {
    render(<CbomAlgorithmMatrix components={mockComponents} />);

    expect(screen.getByText(/Post-Quantum & Key Encapsulation/i)).toBeInTheDocument();
    expect(screen.getByText(/Public Key & Asymmetric Cryptography/i)).toBeInTheDocument();
    expect(screen.getByText(/Symmetric Block & Stream Ciphers/i)).toBeInTheDocument();
    expect(screen.getByText(/Cryptographic Hash & Digest Functions/i)).toBeInTheDocument();

    expect(screen.getByText('ML-KEM-768')).toBeInTheDocument();
    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
    expect(screen.getByText('AES-256')).toBeInTheDocument();
  });

  it('calls onSelectAlgorithm when clicking an algorithm card', () => {
    const handleSelect = vi.fn();
    render(
      <CbomAlgorithmMatrix
        components={mockComponents}
        onSelectAlgorithm={handleSelect}
      />
    );

    const algoCard = screen.getByTestId('algo-item-RSA-2048');
    fireEvent.click(algoCard);

    expect(handleSelect).toHaveBeenCalledTimes(1);
    expect(handleSelect).toHaveBeenCalledWith('RSA-2048');
  });

  it('getAlgorithmFamily accurately classifies algorithms', () => {
    expect(getAlgorithmFamily('ML-KEM-1024', 'KEY_EXCHANGE')).toContain('Post-Quantum');
    expect(getAlgorithmFamily('RSA', 'ASYMMETRIC')).toContain('Public Key');
    expect(getAlgorithmFamily('AES-GCM', 'ENCRYPTION')).toContain('Symmetric');
    expect(getAlgorithmFamily('SHA-256', 'HASHING')).toContain('Hash');
    expect(getAlgorithmFamily('TLSv1.3', 'PROTOCOL')).toContain('Transport Security');
  });
});
