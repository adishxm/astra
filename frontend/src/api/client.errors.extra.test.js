import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiGet, apiPostFile, ApiError, getErrorMessage } from './client';
import { MockXMLHttpRequest } from '../test/mockXhr';

import invalidArchiveFixture from '../test/fixtures/errors/400_invalid_archive.json';
import tooLargeFixture from '../test/fixtures/errors/413_too_large.json';

describe('client (errors & edge cases extra)', () => {
  const originalXhr = global.XMLHttpRequest;

  beforeEach(() => {
    vi.restoreAllMocks();
    MockXMLHttpRequest.reset();
    global.XMLHttpRequest = MockXMLHttpRequest;
  });

  afterEach(() => {
    global.XMLHttpRequest = originalXhr;
  });

  it('handles 400 invalid archive format error', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        headers: { get: () => 'application/json' },
        json: async () => invalidArchiveFixture,
      })
    );

    try {
      await apiGet('/api/v1/scans');
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      expect(err.status).toBe(400);
      expect(err.kind).toBe('client');
      expect(err.message).toBe(
        'The archive could not be accepted: Unsupported archive format. Expected one of: .zip, .tar, .tar.gz, .tar.bz2'
      );
    }
  });

  it('handles 413 too large error', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 413,
        statusText: 'Request Entity Too Large',
        headers: { get: () => 'application/json' },
        json: async () => tooLargeFixture,
      })
    );

    try {
      await apiGet('/api/v1/scans');
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      expect(err.status).toBe(413);
      expect(err.kind).toBe('too_large');
      expect(err.message).toBe(
        'The archive is too large. Uploaded archive exceeds maximum limit of 100 MB'
      );
    }
  });

  it('handles 422 array-style validation errors', async () => {
    const validationError = {
      detail: [
        { loc: ['body', 'scan_id'], msg: 'field required', type: 'value_error.missing' },
        { loc: ['query', 'limit'], msg: 'ensure this value is greater than 0', type: 'value_error.number.not_gt' },
      ],
    };

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        statusText: 'Unprocessable Entity',
        headers: { get: () => 'application/json' },
        json: async () => validationError,
      })
    );

    try {
      await apiGet('/api/v1/scans');
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      expect(err.status).toBe(422);
      expect(err.message).toBe(
        'body.scan_id: field required; query.limit: ensure this value is greater than 0'
      );
    }
  });

  it('handles network failure with exact message', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockRejectedValue(new TypeError('Failed to fetch'))
    );

    try {
      await apiGet('/health');
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      expect(err.status).toBe(0);
      expect(err.kind).toBe('network');
      expect(err.message).toBe('Unable to connect to ASTRA engine');
    }
  });

  it('handles abort signal cleanly', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((_url, { signal }) => {
        if (signal && signal.aborted) {
          const err = new Error('The user aborted a request.');
          err.name = 'AbortError';
          return Promise.reject(err);
        }
        return Promise.resolve({
          ok: true,
          status: 200,
          headers: { get: () => 'application/json' },
          json: async () => ({}),
        });
      })
    );

    const controller = new AbortController();
    controller.abort();

    await expect(apiGet('/health', { signal: controller.signal })).rejects.toThrow(ApiError);

    try {
      await apiGet('/health', { signal: controller.signal });
    } catch (err) {
      expect(err.kind).toBe('aborted');
      expect(err.status).toBe(0);
    }
  });

  it('getErrorMessage formats various error shapes', () => {
    expect(getErrorMessage(new ApiError('Custom message', { status: 500 }))).toBe('Custom message');
    expect(getErrorMessage(new ApiError('Ignored', { status: 0, kind: 'network' }))).toBe('Unable to connect to ASTRA engine');
    expect(getErrorMessage(new Error('Standard JS error'))).toBe('Standard JS error');
    expect(getErrorMessage('Raw string error')).toBe('Raw string error');
    expect(getErrorMessage(null)).toBe('An unknown error occurred');
  });

  it('handles 204 No Content response in apiGet', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 204,
        headers: { get: () => 'application/json' },
        json: async () => { throw new Error('no json'); },
      })
    );

    const result = await apiGet('/api/v1/action');
    expect(result).toBe(null);
  });

  it('handles 500 server error with generic detail fallback', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        headers: { get: () => 'text/plain' },
        text: async () => 'Fatal crash',
      })
    );

    try {
      await apiGet('/api/v1/crash');
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      expect(err.status).toBe(500);
      expect(err.kind).toBe('server');
      expect(err.message).toBe('The ASTRA engine reported an error: Fatal crash');
    }
  });

  it('handles XHR upload network error and abort in apiPostFile', async () => {
    const file = new File(['content'], 'test.zip');
    const controller = new AbortController();

    const uploadPromise = apiPostFile('/api/v1/scans', file, null, { signal: controller.signal });
    const xhr = MockXMLHttpRequest.lastInstance;
    controller.abort();

    await expect(uploadPromise).rejects.toMatchObject({ kind: 'aborted' });
    expect(xhr.aborted).toBe(true);
  });

  it('handles XHR upload error and timeout callbacks', async () => {
    const file = new File(['content'], 'test.zip');

    const errorPromise = apiPostFile('/api/v1/scans', file);
    const xhrError = MockXMLHttpRequest.lastInstance;
    xhrError.triggerError();
    await expect(errorPromise).rejects.toMatchObject({ kind: 'network' });

    const timeoutPromise = apiPostFile('/api/v1/scans', file);
    const xhrTimeout = MockXMLHttpRequest.lastInstance;
    if (xhrTimeout.ontimeout) {
      xhrTimeout.ontimeout();
    }
    await expect(timeoutPromise).rejects.toMatchObject({ kind: 'network' });
  });
});
