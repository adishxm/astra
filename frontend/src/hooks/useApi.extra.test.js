import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useApi } from './useApi';
import { useScans } from './useScans';
import { useHealth } from './useHealth';
import { usePageTitle } from './usePageTitle';

import healthFixture from '../test/fixtures/health.json';
import scansListFixture from '../test/fixtures/scans_list.json';

describe('useApi (lifecycle, race condition & hook wrappers extra)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('skips request when path is null or disabled', () => {
    const fetchSpy = vi.fn();
    vi.stubGlobal('fetch', fetchSpy);

    const { result } = renderHook(() => useApi(null));
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBe(null);
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('refetch triggers a new request', async () => {
    let callCount = 0;
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(async () => {
        callCount++;
        return {
          ok: true,
          status: 200,
          headers: { get: () => 'application/json' },
          json: async () => ({ ...healthFixture, version: `${callCount}.0.0` }),
        };
      })
    );

    const { result } = renderHook(() => useApi('/health'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    expect(result.current.data.version).toBe('1.0.0');

    act(() => {
      result.current.refetch();
    });

    await waitFor(() => {
      expect(result.current.data.version).toBe('2.0.0');
    });
  });

  it('protects against out-of-order race conditions', async () => {
    let resolveFirst;
    let resolveSecond;

    const firstPromise = new Promise((resolve) => {
      resolveFirst = resolve;
    });
    const secondPromise = new Promise((resolve) => {
      resolveSecond = resolve;
    });

    const fetchMock = vi.fn().mockImplementation((url) => {
      if (url.includes('path1')) {
        return firstPromise;
      }
      return secondPromise;
    });
    vi.stubGlobal('fetch', fetchMock);

    const { result, rerender } = renderHook(({ path }) => useApi(path), {
      initialProps: { path: '/path1' },
    });

    // Switch to path2
    rerender({ path: '/path2' });

    // Resolve path2 FIRST
    resolveSecond({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({ path: 'path2_data' }),
    });

    await waitFor(() => {
      expect(result.current.data).toEqual({ path: 'path2_data' });
    });

    // Resolve path1 LATER (must NOT overwrite path2)
    resolveFirst({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({ path: 'path1_data' }),
    });

    // Data remains path2_data
    expect(result.current.data).toEqual({ path: 'path2_data' });
  });

  it('useScans returns parsed scans array or empty array', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        headers: { get: () => 'application/json' },
        json: async () => scansListFixture,
      })
    );

    const { result } = renderHook(() => useScans());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.scans).toHaveLength(3);
    expect(result.current.scans[0].scan_id).toBe('scan-7fae0e1b');
  });

  it('useHealth returns isHealthy based on status: pass', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        headers: { get: () => 'application/json' },
        json: async () => healthFixture,
      })
    );

    const { result } = renderHook(() => useHealth());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.isHealthy).toBe(true);
    expect(result.current.health.status).toBe('pass');
  });

  it('usePageTitle updates document title', () => {
    renderHook(() => usePageTitle('Test Page'));
    expect(document.title).toBe('Test Page | ASTRA');
  });
});
