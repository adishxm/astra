import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import NotFoundPage from './NotFoundPage';

describe('NotFoundPage', () => {
  it('renders 404 heading and helpful descriptions', () => {
    render(
      <MemoryRouter>
        <NotFoundPage />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Resource Not Found');
    expect(screen.getByText(/HTTP 404/i)).toBeInTheDocument();
    expect(screen.getByText(/cryptographic view or artifact endpoint/i)).toBeInTheDocument();
  });

  it('provides navigation buttons to return home and go back', () => {
    const backSpy = vi.spyOn(window.history, 'back').mockImplementation(() => {});

    render(
      <MemoryRouter>
        <NotFoundPage />
      </MemoryRouter>
    );

    const homeLink = screen.getByRole('link', { name: /Return to Dashboard/i });
    expect(homeLink).toHaveAttribute('href', '/');

    const backButton = screen.getByRole('button', { name: /Go Back/i });
    fireEvent.click(backButton);
    expect(backSpy).toHaveBeenCalledTimes(1);

    backSpy.mockRestore();
  });
});
