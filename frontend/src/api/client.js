/**
 * ASTRA API Client & Typed Error Layer
 * Fully aligned with API contract and real backend fixtures.
 */

const BASE_URL =
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL) || '';

/**
 * Custom Error class for ASTRA API communication
 */
export class ApiError extends Error {
  /**
   * @param {string} message
   * @param {Object} options
   * @param {number} [options.status=0]
   * @param {*} [options.detail=null]
   * @param {'network' | 'client' | 'server' | 'not_found' | 'too_large' | 'aborted'} [options.kind='client']
   */
  constructor(message, { status = 0, detail = null, kind = 'client' } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
    this.kind = kind;
  }
}

/**
 * Extracts and formats detail messages from API error bodies (supports strings and 422 arrays)
 * @param {*} detail
 * @returns {string|null}
 */
function extractDetailText(detail) {
  if (!detail) return null;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    // FastAPI 422 validation error format: [{ loc, msg, type }]
    return detail
      .map((item) => {
        if (typeof item === 'string') return item;
        const loc = Array.isArray(item.loc) ? item.loc.join('.') : item.loc;
        return loc ? `${loc}: ${item.msg || 'Invalid value'}` : (item.msg || JSON.stringify(item));
      })
      .join('; ');
  }
  if (typeof detail === 'object') {
    return detail.message || detail.error || JSON.stringify(detail);
  }
  return String(detail);
}

/**
 * Classifies HTTP status code into an ApiError kind
 * @param {number} status
 * @returns {'network' | 'client' | 'server' | 'not_found' | 'too_large' | 'aborted'}
 */
function classifyStatus(status) {
  if (status === 0) return 'network';
  if (status === 404) return 'not_found';
  if (status === 413) return 'too_large';
  if (status >= 400 && status < 500) return 'client';
  if (status >= 500) return 'server';
  return 'client';
}

/**
 * Builds user-friendly error message based on status code and detail
 * @param {number} status
 * @param {*} rawDetail
 * @param {string} [statusText='']
 * @returns {string}
 */
function buildErrorMessage(status, rawDetail, statusText = '') {
  const detailText = extractDetailText(rawDetail);

  if (status === 0) {
    return 'Unable to connect to ASTRA engine';
  }
  if (status === 400) {
    return detailText
      ? `The archive could not be accepted: ${detailText}`
      : 'The archive could not be accepted.';
  }
  if (status === 404) {
    return detailText ? `Not found: ${detailText}` : 'Not found.';
  }
  if (status === 413) {
    return detailText
      ? `The archive is too large. ${detailText}`
      : 'The archive is too large.';
  }
  if (status >= 500) {
    return detailText
      ? `The ASTRA engine reported an error: ${detailText}`
      : `The ASTRA engine reported an error: HTTP ${status}`;
  }
  if (detailText) {
    return detailText;
  }
  return statusText || `HTTP error ${status}`;
}

/**
 * Converts any caught error into a human-readable string
 * @param {*} error
 * @returns {string}
 */
export function getErrorMessage(error) {
  if (!error) return 'An unknown error occurred';
  if (error instanceof ApiError || (error && typeof error === 'object' && 'kind' in error)) {
    if (error.kind === 'network') {
      return 'Unable to connect to ASTRA engine';
    }
    return error.message || 'An error occurred while communicating with the ASTRA engine';
  }
  if (error instanceof Error) {
    if (error.name === 'AbortError') {
      return 'Request was cancelled';
    }
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'An unexpected error occurred';
}

/**
 * GET request with JSON parsing, typed ApiError handling, and abort signal support
 * @param {string} path
 * @param {Object} [options]
 * @param {AbortSignal} [options.signal]
 * @returns {Promise<any>}
 */
export async function apiGet(path, { signal } = {}) {
  const url = `${BASE_URL}${path}`;

  let res;
  try {
    res = await fetch(url, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
      signal,
    });
  } catch (err) {
    if (err.name === 'AbortError' || (signal && signal.aborted)) {
      throw new ApiError('Request aborted', { status: 0, kind: 'aborted' });
    }
    throw new ApiError('Unable to connect to ASTRA engine', {
      status: 0,
      kind: 'network',
      detail: err.message,
    });
  }

  let body = null;
  const contentType = res.headers?.get?.('content-type') || '';
  const hasJson = contentType.includes('application/json');

  try {
    if (res.status !== 204) {
      if (hasJson) {
        body = await res.json();
      } else {
        const text = await res.text();
        if (text) {
          try {
            body = JSON.parse(text);
          } catch {
            body = text;
          }
        }
      }
    }
  } catch {
    body = null;
  }

  if (!res.ok) {
    const rawDetail = body && typeof body === 'object' ? body.detail : body;
    const kind = classifyStatus(res.status);
    const message = buildErrorMessage(res.status, rawDetail, res.statusText);
    throw new ApiError(message, {
      status: res.status,
      detail: rawDetail,
      kind,
    });
  }

  return body;
}

/**
 * PUT request with JSON payload, typed ApiError handling, and abort signal support
 * @param {string} path
 * @param {any} data
 * @param {Object} [options]
 * @param {AbortSignal} [options.signal]
 * @returns {Promise<any>}
 */
export async function apiPut(path, data, { signal } = {}) {
  const url = `${BASE_URL}${path}`;

  let res;
  try {
    res = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(data),
      signal,
    });
  } catch (err) {
    if (err.name === 'AbortError' || (signal && signal.aborted)) {
      throw new ApiError('Request aborted', { status: 0, kind: 'aborted' });
    }
    throw new ApiError('Unable to connect to ASTRA engine', {
      status: 0,
      kind: 'network',
      detail: err.message,
    });
  }

  let body = null;
  const contentType = res.headers?.get?.('content-type') || '';
  const hasJson = contentType.includes('application/json');

  try {
    if (res.status !== 204) {
      if (hasJson) {
        body = await res.json();
      } else {
        const text = await res.text();
        if (text) {
          try {
            body = JSON.parse(text);
          } catch {
            body = text;
          }
        }
      }
    }
  } catch {
    body = null;
  }

  if (!res.ok) {
    const rawDetail = body && typeof body === 'object' ? body.detail : body;
    const kind = classifyStatus(res.status);
    const message = buildErrorMessage(res.status, rawDetail, res.statusText);
    throw new ApiError(message, {
      status: res.status,
      detail: rawDetail,
      kind,
    });
  }

  return body;
}

/**
 * Multipart file upload with real upload progress tracking via XMLHttpRequest
 * @param {string} path
 * @param {File | Blob} file
 * @param {(percent: number) => void} [onProgress]
 * @param {Object} [options]
 * @param {AbortSignal} [options.signal]
 * @returns {Promise<any>}
 */
export function apiPostFile(path, file, onProgress, { signal } = {}) {
  return new Promise((resolve, reject) => {
    if (signal && signal.aborted) {
      reject(new ApiError('Upload aborted', { status: 0, kind: 'aborted' }));
      return;
    }

    const xhr = new XMLHttpRequest();
    const url = `${BASE_URL}${path}`;
    xhr.open('POST', url);
    xhr.setRequestHeader('Accept', 'application/json');

    const abortHandler = () => {
      xhr.abort();
      reject(new ApiError('Upload aborted', { status: 0, kind: 'aborted' }));
    };

    if (signal) {
      signal.addEventListener('abort', abortHandler, { once: true });
    }

    if (xhr.upload && typeof onProgress === 'function') {
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable && e.total > 0) {
          const percent = Math.min(100, Math.max(0, Math.round((e.loaded / e.total) * 100)));
          onProgress(percent);
        }
      };
    }

    xhr.onload = () => {
      if (signal) {
        signal.removeEventListener('abort', abortHandler);
      }

      let body = null;
      if (xhr.responseText) {
        try {
          body = JSON.parse(xhr.responseText);
        } catch {
          body = xhr.responseText;
        }
      }

      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(body);
      } else {
        const rawDetail = body && typeof body === 'object' ? body.detail : body;
        const kind = classifyStatus(xhr.status);
        const message = buildErrorMessage(xhr.status, rawDetail, xhr.statusText);
        reject(
          new ApiError(message, {
            status: xhr.status,
            detail: rawDetail,
            kind,
          })
        );
      }
    };

    xhr.onerror = () => {
      if (signal) {
        signal.removeEventListener('abort', abortHandler);
      }
      reject(
        new ApiError('Unable to connect to ASTRA engine', {
          status: 0,
          kind: 'network',
        })
      );
    };

    xhr.ontimeout = () => {
      if (signal) {
        signal.removeEventListener('abort', abortHandler);
      }
      reject(
        new ApiError('Unable to connect to ASTRA engine', {
          status: 0,
          kind: 'network',
        })
      );
    };

    const formData = new FormData();
    formData.append('file', file);
    xhr.send(formData);
  });
}
