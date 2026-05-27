type StorageLike = Pick<Storage, 'getItem' | 'setItem' | 'removeItem' | 'clear' | 'key' | 'length'>;

function createMemoryStorage(): StorageLike {
  const store = new Map<string, string>();
  return {
    get length() {
      return store.size;
    },
    key(index: number): string | null {
      return Array.from(store.keys())[index] ?? null;
    },
    getItem(key: string): string | null {
      return store.get(key) ?? null;
    },
    setItem(key: string, value: string): void {
      store.set(key, value);
    },
    removeItem(key: string): void {
      store.delete(key);
    },
    clear(): void {
      store.clear();
    },
  };
}

const memoryLocalStorage = createMemoryStorage();
const memorySessionStorage = createMemoryStorage();

function resolveStorage(kind: 'localStorage' | 'sessionStorage', fallback: StorageLike): StorageLike {
  if (typeof window === 'undefined') {
    return fallback;
  }

  const storage = window[kind];
  if (!storage) {
    return fallback;
  }

  try {
    const key = '__zdash_storage_probe__';
    storage.setItem(key, 'ok');
    storage.removeItem(key);
    return storage;
  } catch {
    return fallback;
  }
}

export function safeLocalStorage(): StorageLike {
  return resolveStorage('localStorage', memoryLocalStorage);
}

export function safeSessionStorage(): StorageLike {
  return resolveStorage('sessionStorage', memorySessionStorage);
}
