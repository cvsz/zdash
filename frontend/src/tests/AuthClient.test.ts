import { afterEach, describe, expect, it, vi } from "vitest";

import {
  applyStoredSession,
  clearStoredSession,
  loginWithPassword,
  readStoredSession,
  writeStoredSession,
} from "../api/auth";
import { apiClient, setSession } from "../api/client";

describe("auth client", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    clearStoredSession();
    setSession(undefined);
  });

  it("stores and clears session tokens in isolated auth module", () => {
    writeStoredSession({ accessToken: "access-1", refreshToken: "refresh-1" });
    expect(readStoredSession()).toEqual({
      accessToken: "access-1",
      refreshToken: "refresh-1",
    });

    clearStoredSession();
    expect(readStoredSession()).toBeNull();
  });

  it("adds Authorization header after applying stored session", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        ok: true,
        data: { ok: true },
        error: null,
        timestamp: "2026-01-01T00:00:00Z",
      }),
    }) as unknown as typeof fetch;

    writeStoredSession({ accessToken: "access-token", refreshToken: "refresh-token" });
    applyStoredSession(readStoredSession());

    await apiClient.get<{ ok: boolean }>("/api/secure");

    const requestInit = (globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0][1] as
      | RequestInit
      | undefined;
    const headers = new Headers(requestInit?.headers);
    expect(headers.get("Authorization")).toBe("Bearer access-token");
  });

  it("stores login tokens after successful login", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        ok: true,
        data: {
          access_token: "login-access",
          refresh_token: "login-refresh",
          token_type: "bearer",
          role: "admin",
          username: "admin",
        },
        error: null,
        timestamp: "2026-01-01T00:00:00Z",
      }),
    }) as unknown as typeof fetch;

    const result = await loginWithPassword("admin", "pass");
    expect(result.access_token).toBe("login-access");
    expect(readStoredSession()).toEqual({
      accessToken: "login-access",
      refreshToken: "login-refresh",
    });
  });
});
