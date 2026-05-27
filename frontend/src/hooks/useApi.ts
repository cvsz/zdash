import {
  DependencyList,
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';

export interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: DependencyList = [],
): ApiState<T> {
  const mountedRef = useRef(true);

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(async () => {
    try {
      if (mountedRef.current) {
        setLoading(true);
      }

      const result = await fetcher();

      if (!mountedRef.current) {
        return;
      }

      setData(result);
      setError(null);
    } catch (err) {
      if (!mountedRef.current) {
        return;
      }

      const message =
        err instanceof Error ? err.message : 'Unknown API error';

      setError(message);
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, deps);

  useEffect(() => {
    mountedRef.current = true;

    void run();

    return () => {
      mountedRef.current = false;
    };
  }, [run]);

  return {
    data,
    loading,
    error,
    refetch: run,
  };
}
