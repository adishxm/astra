import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Badge from './Badge';

describe('Badge', () => {
  it('renders text', () => {
    render(<Badge variant="info">Custom Info</Badge>);
    expect(screen.getByText('Custom Info')).toBeInTheDocument();
  });

  it('applies the right class for safe / vulnerable / unknown', () => {
    const { container, rerender } = render(<Badge variant="safe" />);
    expect(screen.getByText('Safe')).toBeInTheDocument();
    expect(container.firstChild).toHaveClass('badge--safe');
    expect(container.firstChild).not.toHaveClass('badge--unknown');

    rerender(<Badge variant="vulnerable" />);
    expect(screen.getByText('Vulnerable')).toBeInTheDocument();
    expect(container.firstChild).toHaveClass('badge--vulnerable');

    rerender(<Badge variant="unknown" />);
    expect(screen.getByText('Unknown')).toBeInTheDocument();
    expect(container.firstChild).toHaveClass('badge--unknown');
    expect(container.firstChild).not.toHaveClass('badge--safe');
  });

  it('applies status and urgency classes', () => {
    const { container, rerender } = render(<Badge variant="pass" />);
    expect(container.firstChild).toHaveClass('badge--pass');

    rerender(<Badge variant="fail" />);
    expect(container.firstChild).toHaveClass('badge--fail');

    rerender(<Badge variant="critical" pulse />);
    expect(container.firstChild).toHaveClass('badge--critical', 'badge--pulse');
  });
});
