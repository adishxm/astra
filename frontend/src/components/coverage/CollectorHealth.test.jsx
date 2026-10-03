import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import CollectorHealth from './CollectorHealth';

describe('CollectorHealth', () => {
  const sampleHealth = {
    'detector-source-code-v1': 'OK',
    'detector-manifest-v1': 'OK',
    'detector-config-v1': 'OK',
    'detector-certificate-v1': 'OK',
    'binary_crypto_detector_static_v1': 'DEGRADED',
  };

  it('renders collector health grid and timestamps', () => {
    render(
      <CollectorHealth
        health={sampleHealth}
        evaluatedAt="2026-10-03T16:58:45Z"
      />
    );

    expect(screen.getByTestId('collector-health')).toBeInTheDocument();
    expect(screen.getByText('detector-source-code-v1')).toBeInTheDocument();
    expect(screen.getByText('binary_crypto_detector_static_v1')).toBeInTheDocument();
    expect(screen.getByText('DEGRADED')).toBeInTheDocument();
    expect(screen.getByText(/Evaluated at:/i)).toBeInTheDocument();
  });

  it('renders empty message when no health telemetry is provided', () => {
    render(<CollectorHealth health={{}} />);
    expect(screen.getByTestId('collector-health-empty')).toBeInTheDocument();
    expect(screen.getByText(/no detector health status telemetry/i)).toBeInTheDocument();
  });
});
