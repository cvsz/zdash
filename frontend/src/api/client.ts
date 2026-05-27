import { mockHealth, mockLogs } from "./mockData";
import { ApiError, type ApiErrorPayload, type ApiResponse } from "./types";

const DEFAULT_API_BASE_URL = "http://localhost:8005";
const DEFAULT_TIMEOUT_MS = 6000;
const RETRYABLE_STATUSES = new Set([502, 503, 504]);

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const baseUrl = (configuredBaseUrl || DEFAULT_API_BASE_URL).replace(/\/+$/, "");
const mockFallbackEnabled =
  String(import.meta.env.VITE_ENABLE_MOCK_FALLBACK ?? "true").toLowerCase() ===
  "true";

export let mockFallbackActive = false;

export const apiClientConfig = {
  baseUrl,
  mockFallbackEnabled,
};

type RequestOptions<T> = {
  fallback?: T;
  timeoutMs?: number;
};

function isApiErrorPayload(value: unknown): value is ApiErrorPayload {
  if (!value || typeof value !== "object") {
    return false;
  }

  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.code === "string" && typeof candidate.message === "string"
  );
}

function isApiResponse<T>(value: unknown): value is ApiResponse<T> {
  if (!value || typeof value !== "object") {
    return false;
  }

  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.ok === "boolean" &&
    "data" in candidate &&
    "error" in candidate &&
    typeof candidate.timestamp === "string"
  );
}

function normalizeApiError(
  error: unknown,
  status: number | undefined,
  path: string,
): ApiError {
  if (error instanceof ApiError) {
    return error;
  }

  if (error instanceof DOMException && error.name === "AbortError") {
    return new ApiError("Request timed out", {
      code: "TIMEOUT",
      status,
      path,
      cause: error,
    });
  }

  if (error instanceof TypeError) {
    return new ApiError("Backend is unavailable", {
      code: "NETWORK_ERROR",
      status,
      path,
      cause: error,
    });
  }

  if (error instanceof Error) {
    return new ApiError(error.message, {
      code: "REQUEST_FAILED",
      status,
      path,
      cause: error,
    });
  }

  return new ApiError("Unknown request error", {
    code: "REQUEST_FAILED",
    status,
    path,
    details: error,
  });
}

function shouldUseMockFallback<T>(
  error: ApiError,
  fallback: T | undefined,
): fallback is T {
  if (!mockFallbackEnabled || fallback === undefined) {
    return false;
  }

  if (error.code === "TIMEOUT" || error.code === "NETWORK_ERROR") {
    return true;
  }

  if (error.status !== undefined && RETRYABLE_STATUSES.has(error.status)) {
    return true;
  }

  return false;
}

async function request<T>(
  path: string,
  init: RequestInit = {},
  options: RequestOptions<T> = {},
): Promise<T> {
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  const url = `${baseUrl}${path}`;

  try {
    const response = await fetch(url, {
      ...init,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(init.headers || {}),
      },
    });

    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch (error) {
      throw normalizeApiError(
        new ApiError("Invalid JSON response", {
          code: "INVALID_RESPONSE",
          status: response.status,
          path,
          cause: error,
        }),
        response.status,
        path,
      );
    }

    if (!isApiResponse<T>(payload)) {
      throw new ApiError("Invalid API envelope", {
        code: "INVALID_ENVELOPE",
        status: response.status,
        path,
        details: payload,
      });
    }

    if (!response.ok || !payload.ok) {
      const envelopeError = isApiErrorPayload(payload.error)
        ? payload.error
        : null;
      throw new ApiError(
        envelopeError?.message || `Request failed with status ${response.status}`,
        {
          code: envelopeError?.code || `HTTP_${response.status || 500}`,
          status: response.status,
          path,
          details: payload.error,
        },
      );
    }

    if (payload.data === null) {
      throw new ApiError("API returned empty data", {
        code: "EMPTY_DATA",
        status: response.status,
        path,
      });
    }

    return payload.data;
  } catch (error) {
    const apiError = normalizeApiError(error, undefined, path);
    if (shouldUseMockFallback(apiError, options.fallback)) {
      mockFallbackActive = true;
      return options.fallback;
    }
    throw apiError;
  } finally {
    clearTimeout(timeout);
  }
}

export const apiClient = {
  get<T>(path: string, fallback?: T, options?: Omit<RequestOptions<T>, "fallback">) {
    return request<T>(path, {}, { ...options, fallback });
  },
  post<T>(
    path: string,
    body?: unknown,
    fallback?: T,
    options?: Omit<RequestOptions<T>, "fallback">,
  ) {
    return request<T>(
      path,
      {
        method: "POST",
        body: JSON.stringify(body ?? {}),
      },
      { ...options, fallback },
    );
  },
  delete<T>(
    path: string,
    fallback?: T,
    options?: Omit<RequestOptions<T>, "fallback">,
  ) {
    return request<T>(
      path,
      {
        method: "DELETE",
      },
      { ...options, fallback },
    );
  },
  getHealth() {
    return request("/health", {}, { fallback: mockHealth });
  },
  getLogs() {
    return request("/api/logs", {}, { fallback: { events: mockLogs } });
  },
};

export function resetMockFallbackState() {
  mockFallbackActive = false;
}

export const apiGet = apiClient.get;
export const apiPostEnvelope = apiClient.post;
export const setSession = (_token?: string) => {};
