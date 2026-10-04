import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import CbomDetailModal from './CbomDetailModal';

describe('CbomDetailModal', () => {
  const mockComponent = {
    id: 'comp-1',
    componentName: 'RSA-2048-crypto-service',
    assetId: 'rsa-2048-crypto_service.py-22',
    algorithm: 'RSA-2048',
    purpose: 'ASYMMETRIC',
    assetType: 'algorithm',
    parameterSetIdentifier: '2048',
    executionEnvironment: 'software-plain-ram',
    keySizeBits: 2048,
    curveName: null,
    sourceKind: 'SOURCE_CODE',
    claimType: 'ALGORITHM_USE',
    relativePath: 'crypto_service.py',
    startLine: 22,
    endLine: 24,
    confidence: 'CONFIRMED',
    confidenceRationale: 'Direct AST invocation of RSA.generate(2048)',
    sanitizedExcerpt: 'key = RSA.generate(2048)',
    evidenceDigest: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    detectorId: 'ast-crypto-detector-v1',
    rulesetVersion: '2026.10-nist-pqc',
  };

  it('renders nothing when closed or component is null', () => {
    const { container } = render(
      <CbomDetailModal open={false} component={mockComponent} onClose={() => {}} />
    );
    expect(container).toBeEmptyDOMElement();
  });

  it('renders full component details, CycloneDX properties, and sanitized evidence when open', () => {
    render(
      <CbomDetailModal open={true} component={mockComponent} onClose={() => {}} />
    );

    expect(screen.getByText('CBOM Component: RSA-2048')).toBeInTheDocument();
    expect(screen.getByText('RSA-2048-crypto-service')).toBeInTheDocument();
    expect(screen.getByText('rsa-2048-crypto_service.py-22')).toBeInTheDocument();

    // CycloneDX 1.6 properties
    expect(screen.getByText('software-plain-ram')).toBeInTheDocument();
    expect(screen.getByText('2048 bits')).toBeInTheDocument();

    // Provenance
    expect(screen.getByText(/Direct AST invocation of RSA.generate\(2048\)/i)).toBeInTheDocument();
    expect(screen.getByText('key = RSA.generate(2048)')).toBeInTheDocument();
  });

  it('calls onClose when clicking close button', () => {
    const handleClose = vi.fn();
    render(
      <CbomDetailModal open={true} component={mockComponent} onClose={handleClose} />
    );

    const closeBtn = screen.getByRole('button', { name: /Close component detail dialog/i });
    fireEvent.click(closeBtn);

    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
