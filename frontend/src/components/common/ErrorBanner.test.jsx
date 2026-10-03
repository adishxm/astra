import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorBanner from './ErrorBanner';

describe('ErrorBanner', () => {
  it('renders message with role="alert"', () => {
    render(
      <ErrorBanner
        title="Engine Failure"
        message="Unable to connect to ASTRA engine"
      />
    );
    const alert = screen.getByRole('alert');
    expect(alert).toBeInTheDocument();
    expect(screen.getByText('Engine Failure')).toBeInTheDocument();
    expect(screen.getByText('Unable to connect to ASTRA engine')).toBeInTheDocument();
  });

  it('retry button fires callback', async () => {
    const user = userEvent.setup();
    const handleRetry = vi.fn();
    render(
      <ErrorBanner
        message="Unable to connect to ASTRA engine"
        onRetry={handleRetry}
      />
    );

    const retryBtn = screen.getByRole('button', { name: /retry/i });
    expect(retryBtn).toBeInTheDocument();
    await user.click(retryBtn);
    expect(handleRetry).toHaveBeenCalledTimes(1);
  });
});
