import { test, expect } from 'vitest';
import { useRealtimeEvents } from '../hooks/useRealtimeEvents';

test('fallback hook returns events', () => {
  const data = useRealtimeEvents();
  expect(Array.isArray(data.events)).toBe(true);
});
