import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, useLocation } from 'react-router-dom';
import EmptyState from './EmptyState';

function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location-display">{location.pathname}</div>;
}

describe('EmptyState', () => {
  it('renders message', () => {
    render(
      <MemoryRouter>
        <EmptyState
          title="No Scans Yet"
          message="Run your first CBOM scan to see cryptographic inventory."
        />
      </MemoryRouter>
    );
    expect(screen.getByText('No Scans Yet')).toBeInTheDocument();
    expect(screen.getByText('Run your first CBOM scan to see cryptographic inventory.')).toBeInTheDocument();
  });

  it('CTA navigates', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={['/']}>
        <EmptyState
          title="No Scans"
          message="Start scan now"
          ctaLabel="New Scan"
          ctaTo="/scan"
        />
        <LocationDisplay />
      </MemoryRouter>
    );

    const ctaBtn = screen.getByRole('button', { name: /new scan/i });
    expect(screen.getByTestId('location-display')).toHaveTextContent('/');
    await user.click(ctaBtn);
    expect(screen.getByTestId('location-display')).toHaveTextContent('/scan');
  });
});
