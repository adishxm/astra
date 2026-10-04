import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SurfaceBreakdown from './SurfaceBreakdown';

describe('SurfaceBreakdown', () => {
  const sampleBreakdown = {
    SOURCE_CODE: {
      surface: 'SOURCE_CODE',
      total_files: 2,
      assessed_files: 2,
      files_with_findings: 2,
      files_with_no_findings: 0,
      unsupported_files: 0,
      coverage_percentage: 100.0,
    },
    CONFIGURATION: {
      surface: 'CONFIGURATION',
      total_files: 1,
      assessed_files: 1,
      files_with_findings: 1,
      files_with_no_findings: 0,
      unsupported_files: 0,
      coverage_percentage: 100.0,
    },
    UNSUPPORTED_SURFACE: {
      surface: 'UNSUPPORTED_SURFACE',
      total_files: 3,
      assessed_files: 0,
      files_with_findings: 0,
      files_with_no_findings: 0,
      unsupported_files: 3,
      coverage_percentage: 0.0,
    },
  };

  it('renders all discovery surfaces with stats and percentages', () => {
    render(<SurfaceBreakdown surfaceBreakdown={sampleBreakdown} />);

    expect(screen.getByTestId('surface-breakdown')).toBeInTheDocument();
    expect(screen.getByText('SOURCE_CODE')).toBeInTheDocument();
    expect(screen.getByText('CONFIGURATION')).toBeInTheDocument();
    expect(screen.getByText('UNSUPPORTED_SURFACE')).toBeInTheDocument();
    expect(screen.getByText('0.0%')).toBeInTheDocument();
  });

  it('calls onSelectSurface on click and Enter keypress', () => {
    const onSelect = vi.fn();
    render(<SurfaceBreakdown surfaceBreakdown={sampleBreakdown} onSelectSurface={onSelect} />);

    const sourceCard = screen.getByRole('button', { name: /surface SOURCE_CODE/i });
    fireEvent.click(sourceCard);
    expect(onSelect).toHaveBeenCalledWith('SOURCE_CODE');

    fireEvent.keyDown(sourceCard, { key: 'Enter', code: 'Enter' });
    expect(onSelect).toHaveBeenCalledWith('SOURCE_CODE');
  });

  it('renders empty message when surfaceBreakdown is empty', () => {
    render(<SurfaceBreakdown surfaceBreakdown={{}} />);
    expect(screen.getByTestId('surface-breakdown-empty')).toBeInTheDocument();
    expect(screen.getByText(/no surface coverage breakdown available/i)).toBeInTheDocument();
  });
});
