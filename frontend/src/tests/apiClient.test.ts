import { afterEach, describe, expect, it, vi } from "vitest";
import { apiClient, mockFallbackActive, resetMockFallbackState } from "../api/client";
import { ApiError } from "../api/types";

describe("apiClient", () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
    resetMockFallbackState();
  });

  it("unwraps successful API response data", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        ok: true,
        data: { a: 1 },
        error: null,
        timestamp: "2026-01-01T00:00:00Z",
      }),
    }) as unknown as typeof fetch;

    await expect(apiClient.get("/x")).resolves.toEqual({ a: 1 });
  });

  it("throws typed error for API error envelope", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({
        ok: false,
        data: null,
        error: { code: "BAD_REQUEST", message: "bad payload" },
        timestamp: "2026-01-01T00:00:00Z",
      }),
    }) as unknown as typeof fetch;

    const thrown = await apiClient.get("/x").catch((error) => error as ApiError);
    expect(thrown).toBeInstanceOf(ApiError);
    expect(thrown.code).toBe("BAD_REQUEST");
    expect(thrown.status).toBe(400);
    expect(thrown.message).toContain("bad payload");
  });

  it("activates mock fallback when backend is unavailable", async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(
      new TypeError("Failed to fetch"),
    ) as unknown as typeof fetch;

    const fallback = { source: "mock" as const };
    await expect(apiClient.get("/x", fallback)).resolves.toEqual(fallback);
    expect(mockFallbackActive).toBe(true);
  });

  it("handles timeout safely", async () => {
    vi.useFakeTimers();

    globalThis.fetch = vi.fn(
      (_input: RequestInfo | URL, init?: RequestInit) =>
        new Promise((_, reject) => {
          const signal = init?.signal;
          signal?.addEventListener("abort", () => {
            reject(new DOMException("Aborted", "AbortError"));
          });
        }),
    ) as unknown as typeof fetch;

    const pending = apiClient
      .get("/slow", undefined, { timeoutMs: 10 })
      .catch((error) => error as ApiError);
    await vi.advanceTimersByTimeAsync(20);

    const thrown = await pending;
    expect(thrown).toBeInstanceOf(ApiError);
    expect(thrown.code).toBe("TIMEOUT");
  });
});
