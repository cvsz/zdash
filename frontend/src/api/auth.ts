import { apiClient, setSession } from "./client";
import type { AuthTokenPair, AuthUser, StoredAuthSession } from "./types";

const AUTH_STORAGE_KEY = "zdash.auth.session";
export const DEFAULT_ADMIN_USERNAME = "admin";
export const DEFAULT_ADMIN_PASSWORD = "dev-only-change-before-production";

function getStorage(): Storage | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage;
}

export function readStoredSession(): StoredAuthSession | null {
  const storage = getStorage();
  if (!storage) {
    return null;
  }

  const raw = storage.getItem(AUTH_STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    const parsed = JSON.parse(raw) as Partial<StoredAuthSession>;
    if (
      typeof parsed.accessToken === "string" &&
      parsed.accessToken &&
      typeof parsed.refreshToken === "string" &&
      parsed.refreshToken
    ) {
      return {
        accessToken: parsed.accessToken,
        refreshToken: parsed.refreshToken,
      };
    }
  } catch {
    return null;
  }

  return null;
}

export function writeStoredSession(session: StoredAuthSession): void {
  const storage = getStorage();
  if (!storage) {
    return;
  }
  storage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session));
}

export function clearStoredSession(): void {
  const storage = getStorage();
  if (!storage) {
    return;
  }
  storage.removeItem(AUTH_STORAGE_KEY);
}

export function applyStoredSession(session: StoredAuthSession | null): void {
  setSession(session?.accessToken);
}

export function isDefaultAdminCredentials(
  username: string,
  password: string,
): boolean {
  return (
    username.trim() === DEFAULT_ADMIN_USERNAME &&
    password === DEFAULT_ADMIN_PASSWORD
  );
}

export async function loginWithPassword(
  username: string,
  password: string,
): Promise<AuthTokenPair> {
  const tokenPair = await apiClient.post<AuthTokenPair>("/api/auth/login", {
    username,
    password,
  });

  writeStoredSession({
    accessToken: tokenPair.access_token,
    refreshToken: tokenPair.refresh_token,
  });
  applyStoredSession(readStoredSession());

  return tokenPair;
}

export async function refreshSession(
  refreshToken: string,
): Promise<AuthTokenPair> {
  const tokenPair = await apiClient.post<AuthTokenPair>("/api/auth/refresh", {
    refresh_token: refreshToken,
  });

  writeStoredSession({
    accessToken: tokenPair.access_token,
    refreshToken: tokenPair.refresh_token,
  });
  applyStoredSession(readStoredSession());

  return tokenPair;
}

export async function logoutSession(refreshToken?: string): Promise<void> {
  try {
    if (refreshToken) {
      await apiClient.post<{ revoked: boolean }>("/api/auth/logout", {
        refresh_token: refreshToken,
      });
    }
  } finally {
    clearStoredSession();
    applyStoredSession(null);
  }
}

export function getCurrentUser(): Promise<AuthUser> {
  return apiClient.get<AuthUser>("/api/auth/me");
}
