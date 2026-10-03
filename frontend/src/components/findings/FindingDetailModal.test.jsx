import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import FindingDetailModal, { sanitizeEvidenceContent } from './FindingDetailModal';

describe('FindingDetailModal', () => {
  const sampleFinding = {
    id: 'obs-123',
    assetId: 'rsa-2048-crypto.py-10',
    primaryName: 'RSA-2048',
    algorithm: 'RSA-2048',
    sourceKind: 'SOURCE_CODE',
    claimType: 'ALGORITHM_USE',
    purpose: 'ASYMMETRIC',
    keySizeBits: 2048,
    curveName: null,
    confidence: 'CONFIRMED',
    confidenceRationale: 'Identified RSA-2048 constructor in Python cryptography module.',
    relativePath: 'crypto_service.py',
    startLine: 10,
    endLine: 12,
    detectorId: 'detector-source-code-v1',
    rulesetVersion: '2026.10-nist-pqc',
    observedAt: '2026-10-03T12:00:00Z',
    sanitizedExcerpt: 'rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)',
    evidenceDigest: 'c7f8132721b51c65c823888216059d498d643aba34078d925342fab90902eb8a',
    riskEvaluation: {
      risk_score: 64.3,
      urgency: 'MEDIUM',
    },
  };

  it('renders nothing if not open or finding is null', () => {
    const { container } = render(
      <FindingDetailModal finding={null} open={false} onClose={vi.fn()} />
    );
    expect(container).toBeEmptyDOMElement();
  });

  it('renders finding metadata, location, and confidence rationale', () => {
    render(
      <FindingDetailModal finding={sampleFinding} open={true} onClose={vi.fn()} />
    );

    expect(screen.getByText(/Finding Details: RSA-2048/i)).toBeInTheDocument();
    expect(screen.getByText('rsa-2048-crypto.py-10')).toBeInTheDocument();
    expect(screen.getByText('2048 bits')).toBeInTheDocument();
    expect(screen.getByText('crypto_service.py:10-12')).toBeInTheDocument();
    expect(screen.getByText('detector-source-code-v1')).toBeInTheDocument();
    expect(screen.getByText(/Identified RSA-2048 constructor/i)).toBeInTheDocument();
    expect(screen.getByText(/c7f8132721b51c65c823888216059d498d643aba34078d925342fab90902eb8a/i)).toBeInTheDocument();
  });

  it('calls onClose when clicking the close button', () => {
    const onClose = vi.fn();
    render(
      <FindingDetailModal finding={sampleFinding} open={true} onClose={onClose} />
    );

    const closeButtons = screen.getAllByRole('button', { name: /close/i });
    fireEvent.click(closeButtons[0]);
    expect(onClose).toHaveBeenCalled();
  });

  describe('sanitizeEvidenceContent', () => {
    it('returns Evidence unavailable for empty input', () => {
      expect(sanitizeEvidenceContent('')).toBe('Evidence unavailable');
      expect(sanitizeEvidenceContent(null)).toBe('Evidence unavailable');
    });

    it('redacts private key blocks', () => {
      const raw = 'Header\n-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...\n-----END RSA PRIVATE KEY-----\nFooter';
      const sanitized = sanitizeEvidenceContent(raw);
      expect(sanitized).toContain('[REDACTED_PRIVATE_KEY_MATERIAL]');
      expect(sanitized).not.toContain('MIIEowIBAAKCAQEA0');
    });

    it('redacts secret assignments', () => {
      const raw = 'api_key: "secret-key-12345"';
      const sanitized = sanitizeEvidenceContent(raw);
      expect(sanitized).toContain('[REDACTED_SECRET]');
      expect(sanitized).not.toContain('secret-key-12345');
    });
  });
});
