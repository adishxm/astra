import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ScanPage from './ScanPage';

describe('ScanPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders scan initiation heading and intake cards', () => {
    render(
      <MemoryRouter>
        <ScanPage />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1, name: /initiate cryptographic scan/i })).toBeInTheDocument();
    expect(screen.getByText('Repository Archive Intake')).toBeInTheDocument();
    expect(screen.getByText(/intake security & privacy/i)).toBeInTheDocument();
    expect(screen.getByText(/100 MB Size Limit/i)).toBeInTheDocument();
    expect(screen.getByText(/NIST FIPS PQC Ruleset/i)).toBeInTheDocument();
  });
});
