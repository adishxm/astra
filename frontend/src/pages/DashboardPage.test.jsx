import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import DashboardPage from './DashboardPage';
import scansListFixture from '../test/fixtures/scans_list.json';
import healthFixture from '../test/fixtures/health.json';

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders loading state', () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(() => new Promise(() => {}))
    );

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1, name: /dashboard/i })).toBeInTheDocument();
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText(/loading cryptographic inventory/i)).toBeInTheDocument();
  });

  it('renders successful data with scan list and statistics', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(async (url) => {
        if (url.includes('/health')) {
          return {
            ok: true,
            status: 200,
            headers: { get: () => 'application/json' },
            json: async () => healthFixture,
          };
        }
        return {
          ok: true,
          status: 200,
          headers: { get: () => 'application/json' },
          json: async () => scansListFixture,
        };
      })
    );

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    // Header and titles
    expect(await screen.findByRole('heading', { level: 1, name: /dashboard/i })).toBeInTheDocument();

    // Aggregated stats (0 + 1 + 16 = 17 total assets across the 3 fixtures)
    expect(screen.getByText('17')).toBeInTheDocument();
    expect(screen.getByText('Total Assets Discovered')).toBeInTheDocument();

    // Recent scans table
    expect(screen.getByRole('heading', { level: 2, name: /recent scans/i })).toBeInTheDocument();
    expect(screen.getByText('clean_state.zip')).toBeInTheDocument();
    expect(screen.getByText('partial_coverage.zip')).toBeInTheDocument();
    expect(screen.getByText('synthetic_sample.zip')).toBeInTheDocument();
  });

  it('renders empty state when no scans exist', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(async (url) => {
        if (url.includes('/health')) {
          return {
            ok: true,
            status: 200,
            headers: { get: () => 'application/json' },
            json: async () => healthFixture,
          };
        }
        return {
          ok: true,
          status: 200,
          headers: { get: () => 'application/json' },
          json: async () => [],
        };
      })
    );

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    expect(await screen.findByText('No Cryptographic Scans Yet')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /start your first scan/i })).toBeInTheDocument();
  });

  it('renders API error banner with retry option', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockRejectedValue(new TypeError('Network connection lost'))
    );

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    const alert = await screen.findByRole('alert');
    expect(alert).toBeInTheDocument();
    expect(screen.getByText('Failed to Load Scans')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('does not display fake positive values for unassessed state', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(async (url) => {
        if (url.includes('/health')) {
          return {
            ok: true,
            status: 200,
            headers: { get: () => 'application/json' },
            json: async () => ({ status: 'fail' }),
          };
        }
        return {
          ok: true,
          status: 200,
          headers: { get: () => 'application/json' },
          json: async () => [],
        };
      })
    );

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    // Must display "Unassessed" badge and "—", NOT 100% or "Safe"
    expect(await screen.findByText('Unassessed')).toBeInTheDocument();
    expect(screen.getByText('—')).toBeInTheDocument();
    expect(screen.getByText('0')).toBeInTheDocument();
  });
});
