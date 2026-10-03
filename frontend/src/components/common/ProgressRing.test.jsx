import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ProgressRing, { getProgressTone } from './ProgressRing';

describe('ProgressRing', () => {
  it('arc/aria value matches percentage', () => {
    const { rerender } = render(<ProgressRing value={75} label="Coverage" />);
    const progressbar = screen.getByRole('progressbar');
    expect(progressbar).toBeInTheDocument();
    expect(progressbar).toHaveAttribute('aria-valuenow', '75');
    expect(progressbar).toHaveAttribute('aria-valuemin', '0');
    expect(progressbar).toHaveAttribute('aria-valuemax', '100');
    expect(screen.getByText('75%')).toBeInTheDocument();
    expect(screen.getByText('Coverage')).toBeInTheDocument();

    // Test clamping and honesty
    rerender(<ProgressRing value={120} />);
    expect(screen.getByText('100%')).toBeInTheDocument();

    rerender(<ProgressRing value={-10} />);
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('getProgressTone thresholds', () => {
    // Below 50 is danger
    expect(getProgressTone(0)).toBe('danger');
    expect(getProgressTone(49)).toBe('danger');

    // 50 to under 80 is warning
    expect(getProgressTone(50)).toBe('warning');
    expect(getProgressTone(79)).toBe('warning');

    // 80 and above is good
    expect(getProgressTone(80)).toBe('good');
    expect(getProgressTone(100)).toBe('good');
  });
});
