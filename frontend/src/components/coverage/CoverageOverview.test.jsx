import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import CoverageOverview from './CoverageOverview';

describe('CoverageOverview', () => {
  const sampleCoverage = {
    overall_coverage_percentage: 57.14,
    total_files_in_archive: 7,
    total_assessed_files: 4,
    total_unsupported_files: 3,
    total_skipped_files: 0,
    total_failed_files: 0,
    total_observations_found: 16,
    scan_status_label: 'COMPLETE_WITH_COVERAGE_ACCOUNTING',
    is_partial_scan: false,
  };

  it('renders overall coverage percentage, file metrics, and honesty reminder', () => {
    render(<CoverageOverview coverage={sampleCoverage} />);

    expect(screen.getByTestId('coverage-overview')).toBeInTheDocument();
    expect(screen.getByText('57.1%')).toBeInTheDocument();
    expect(screen.getByText(/4 of 7 total files assessed/i)).toBeInTheDocument();
    expect(screen.getByText('COMPLETE_WITH_COVERAGE_ACCOUNTING')).toBeInTheDocument();
    expect(screen.getByText('16')).toBeInTheDocument();
    expect(screen.getByText(/Truthful Accounting/i)).toBeInTheDocument();
  });

  it('handles null/unassessed coverage values truthfully without converting to 0%', () => {
    render(<CoverageOverview coverage={{}} summary={{}} />);

    expect(screen.getByText('N/A')).toBeInTheDocument();
    expect(screen.getByText('UNASSESSED')).toBeInTheDocument();
  });

  it('renders partial scan warning badge if is_partial_scan is true', () => {
    const partialCoverage = {
      ...sampleCoverage,
      is_partial_scan: true,
      scan_status_label: 'PARTIAL_SCAN_EVALUATION',
    };

    render(<CoverageOverview coverage={partialCoverage} />);
    expect(screen.getByText('PARTIAL_SCAN_EVALUATION')).toBeInTheDocument();
    expect(screen.getByText(/Partial scan with unassessed surfaces/i)).toBeInTheDocument();
  });
});
