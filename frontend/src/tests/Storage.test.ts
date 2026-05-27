import { describe, expect, it } from 'vitest';
import { safeLocalStorage, safeSessionStorage } from '../utils/storage';

describe('storage utils', () => {
  it('provides usable fallback-compatible local storage access', () => {
    const storage = safeLocalStorage();
    storage.setItem('k', 'v');
    expect(storage.getItem('k')).toBe('v');
    storage.removeItem('k');
    expect(storage.getItem('k')).toBeNull();
  });

  it('provides usable fallback-compatible session storage access', () => {
    const storage = safeSessionStorage();
    storage.setItem('s', '1');
    expect(storage.getItem('s')).toBe('1');
    storage.clear();
    expect(storage.getItem('s')).toBeNull();
  });
});
