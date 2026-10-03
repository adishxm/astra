import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Card from './Card';

describe('Card', () => {
  it('renders children', () => {
    render(
      <Card title="Card Title">
        <p>Card content text</p>
      </Card>
    );
    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByText('Card content text')).toBeInTheDocument();
  });

  it('variant class applied', () => {
    const { container, rerender } = render(<Card variant="elevated">Content</Card>);
    expect(container.firstChild).toHaveClass('card', 'card--elevated');

    rerender(<Card variant="glass">Content</Card>);
    expect(container.firstChild).toHaveClass('card', 'card--glass');
  });
});
