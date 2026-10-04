import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiGet, apiPostFile, ApiError } from './client';
import { MockXMLHttpRequest } from '../test/mockXhr';

import healthFixture from '../test/fixtures/health.json';
import notFoundFixture from '../test/fixtures/errors/404_scan_not_found.json';
import uploadResponseFixture from '../test/fixtures/scan_upload_response.json';

describe('client', () => {
  const originalXhr = global.XMLHttpRequest;

  beforeEach(() => {
    vi.restoreAllMocks();
    MockXMLHttpRequest.reset();
    global.XMLHttpRequest = MockXMLHttpRequest;
  });

  afterEach(() => {
    global.XMLHttpRequest = originalXhr;
  });

  it('GET success', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        headers: { get: () => 'application/json' },
        json: async () => healthFixture,
      })
    );

    const result = await apiGet('/health');
    expect(result).toEqual(healthFixture);
    expect(result.status).toBe('pass');
    expect(result.service).toBe('ASTRA Cryptographic Engine');
  });

  it('GET error', async () => {
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

    await expect(apiGet('/api/v1/scans/scan-nonexistent-id-0000')).rejects.toThrow(ApiError);

    try {
      await apiGet('/api/v1/scans/scan-nonexistent-id-0000');
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      expect(err.status).toBe(404);
      expect(err.kind).toBe('not_found');
      expect(err.message).toBe('Not found: Scan ID not found: scan-nonexistent-id-0000');
    }
  });

  it('file upload', async () => {
    const file = new File(['dummy zip content'], 'test_archive.zip', { type: 'application/zip' });

    const uploadPromise = apiPostFile('/api/v1/scans', file);
    const xhr = MockXMLHttpRequest.lastInstance;
    expect(xhr).toBeDefined();
    expect(xhr.url).toBe('/api/v1/scans');
    expect(xhr.method).toBe('POST');

    xhr.triggerLoad(200, uploadResponseFixture);
    const result = await uploadPromise;

    expect(result).toEqual(uploadResponseFixture);
    expect(result.scan_id).toBe('scan-cf529d73');
    expect(result.asset_count).toBe(16);
  });

  it('progress callback', async () => {
    const file = new File(['dummy zip content'], 'test_archive.zip', { type: 'application/zip' });
    const progressCalls = [];

    const uploadPromise = apiPostFile('/api/v1/scans', file, (percent) => {
      progressCalls.push(percent);
    });

    const xhr = MockXMLHttpRequest.lastInstance;
    xhr.triggerProgress(250, 1000);
    xhr.triggerProgress(500, 1000);
    xhr.triggerProgress(1000, 1000);

    xhr.triggerLoad(200, uploadResponseFixture);
    await uploadPromise;

    expect(progressCalls).toEqual([25, 50, 100]);
  });
});
