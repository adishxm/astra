import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LoadingSpinner from './LoadingSpinner';

describe('LoadingSpinner', () => {
  it('has role="status" and an accessible label', () => {
    const { rerender } = render(<LoadingSpinner ariaLabel="Scanning dependencies..." />);
    const spinner = screen.getByRole('status');
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveAttribute('aria-label', 'Scanning dependencies...');

    rerender(<LoadingSpinner elapsedSeconds={12} />);
    expect(screen.getByText('Analyzing... 12s')).toBeInTheDocument();
  });
});
