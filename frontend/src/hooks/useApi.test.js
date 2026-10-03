import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useApi } from './useApi';
import healthFixture from '../test/fixtures/health.json';
import notFoundFixture from '../test/fixtures/errors/404_scan_not_found.json';

describe('useApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('loading state', () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(() => new Promise(() => {}))
    );

    const { result } = renderHook(() => useApi('/health'));
    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe(null);
  });

  it('success state', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        headers: { get: () => 'application/json' },
        json: async () => healthFixture,
      })
    );

    const { result } = renderHook(() => useApi('/health'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(healthFixture);
    expect(result.current.error).toBe(null);
    expect(result.current.data.status).toBe('pass');
  });

  it('error state', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        headers: { get: () => 'application/json' },
        json: async () => notFoundFixture,
      })
    );

    const { result } = renderHook(() => useApi('/api/v1/scans/missing-id'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBe(null);
    expect(result.current.error).toBeDefined();
    expect(result.current.error.status).toBe(404);
    expect(result.current.error.kind).toBe('not_found');
  });
});
