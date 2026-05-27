import { renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { useApi } from '../hooks/useApi';

describe('useApi', () => {
  it('loads and refetches data', async () => {
    const fetcher = vi.fn().mockResolvedValueOnce('one').mockResolvedValueOnce('two');
    const { result } = renderHook(() => useApi(fetcher, []));
    await waitFor(() => expect(result.current.data).toBe('one'));
    await result.current.refetch();
    await waitFor(() => expect(result.current.data).toBe('two'));
  });

  it('captures error safely', async () => {
    const { result } = renderHook(() => useApi(async () => { throw new Error('boom'); }, []));
    await waitFor(() => expect(result.current.error).toBe('boom'));
  });
});
