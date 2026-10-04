import { useState, useEffect, useCallback, useRef } from 'react';
import { apiGet } from '../api/client';

/**
 * Generic API fetching hook with race-condition guard, auto-cancellation, and manual refetch
 * @template T
 * @param {string | null | undefined} path
 * @param {Object} [options]
 * @param {boolean} [options.enabled=true]
 * @returns {{ data: T | null, loading: boolean, error: ApiError | null, refetch: () => void }}
 */
export function useApi(path, options = {}) {
  const { enabled = true } = options;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(Boolean(path && enabled));
  const [error, setError] = useState(null);
  const [fetchIndex, setFetchIndex] = useState(0);

  const isMountedRef = useRef(true);
  const activeAbortControllerRef = useRef(null);
  const currentRequestIdRef = useRef(0);

  const refetch = useCallback(() => {
    setFetchIndex((prev) => prev + 1);
  }, []);

  useEffect(() => {
    isMountedRef.current = true;

    if (!path || !enabled) {
      setLoading(false);
      return;
    }

    const requestId = ++currentRequestIdRef.current;

    // Abort previous pending request
    if (activeAbortControllerRef.current) {
      activeAbortControllerRef.current.abort();
    }

    const controller = new AbortController();
    activeAbortControllerRef.current = controller;

    setLoading(true);
    setError(null);

    apiGet(path, { signal: controller.signal })
      .then((resData) => {
        // Only update state if this is still the newest active request and component is mounted
        if (isMountedRef.current && requestId === currentRequestIdRef.current) {
          setData(resData);
          setLoading(false);
          setError(null);
        }
      })
      .catch((err) => {
        if (!isMountedRef.current || requestId !== currentRequestIdRef.current) {
          return;
        }

        // Ignore aborted errors
        if (err?.kind === 'aborted') {
          return;
        }

        setError(err);
        setLoading(false);
      });

    return () => {
      controller.abort();
    };
  }, [path, enabled, fetchIndex]);

  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (activeAbortControllerRef.current) {
        activeAbortControllerRef.current.abort();
      }
    };
  }, []);

  return { data, loading, error, refetch };
}
