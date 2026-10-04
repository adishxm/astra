import { useApi } from './useApi';

/**
 * Hook to retrieve engine health status from GET /health
 * Real health status passes when status === 'pass'.
 * @returns {{ health: Object | null, loading: boolean, error: import('../api/client').ApiError | null, refetch: () => void, isHealthy: boolean }}
 */
export function useHealth() {
  const { data, loading, error, refetch } = useApi('/health');
  const isHealthy = Boolean(data && data.status === 'pass');

  return { health: data, loading, error, refetch, isHealthy };
}
