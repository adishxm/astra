import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import EvidenceViewer from './EvidenceViewer';

describe('EvidenceViewer', () => {
  const sampleObservation = {
    observation_id: 'obs-001',
    candidate_asset_id: 'rsa-2048-crypto.py-1',
    algorithm: 'RSA-2048',
    source_kind: 'SOURCE_CODE',
    purpose: 'ASYMMETRIC',
    confidence: 'CONFIRMED',
    confidence_rationale: 'Regex pattern matched RSA key instantiation',
    relative_path: 'crypto_service.py',
    start_line: 12,
    end_line: 14,
    sanitized_excerpt: 'crypto.generate_rsa(2048)',
    evidence_digest: 'c7f8132721b51c65c823888216059d498d643aba34078d925342fab90902eb8a',
    detector_id: 'detector-source-code-v1',
    ruleset_version: '2026.10-nist-pqc',
    observed_at: '2026-10-03T16:58:45Z',
    raw_parameters: {
      key_size: 2048,
    },
  };

  it('renders raw observed evidence vs derived system interpretation', () => {
    render(<EvidenceViewer observation={sampleObservation} />);

    expect(screen.getByTestId('evidence-viewer')).toBeInTheDocument();
    expect(screen.getByText(/Observed Raw Evidence/i)).toBeInTheDocument();
    expect(screen.getByText(/Derived Interpretation/i)).toBeInTheDocument();
    expect(screen.getByText('crypto_service.py:12-14')).toBeInTheDocument();
    expect(screen.getByText(/crypto.generate_rsa\(2048\)/i)).toBeInTheDocument();
    expect(screen.getByText(/c7f8132721b51c65c823888216059d498d643aba34078d925342fab90902eb8a/i)).toBeInTheDocument();
    expect(screen.getByText(/Regex pattern matched RSA key instantiation/i)).toBeInTheDocument();
  });

  it('renders empty message when no observation is provided', () => {
    render(<EvidenceViewer observation={null} />);
    expect(screen.getByTestId('evidence-viewer-empty')).toBeInTheDocument();
    expect(screen.getByText(/no observation or evidence selected/i)).toBeInTheDocument();
  });
});
