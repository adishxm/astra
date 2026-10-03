import { useMemo } from 'react';
import { useApi } from './useApi';

/**
 * Hook to retrieve cryptographic scans list from GET /api/v1/scans
 * @returns {{ scans: Array<Object>, loading: boolean, error: import('../api/client').ApiError | null, refetch: () => void }}
 */
export function useScans() {
  const { data, loading, error, refetch } = useApi('/api/v1/scans');

  const scans = useMemo(() => {
    if (!data) return [];
    if (Array.isArray(data)) return data;
    if (Array.isArray(data.scans)) return data.scans;
    return [];
  }, [data]);

  return { scans, loading, error, refetch };
}
