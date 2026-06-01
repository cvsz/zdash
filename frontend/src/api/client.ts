import i18n from "../i18n";
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
let sessionToken: string | null = null;
let currentTenant: string | null = null;
let currentWorkspace: string | null = null;
let unauthorizedHandler: (() => void) | null = null;

export const apiClientConfig = {
  baseUrl,
  mockFallbackEnabled,
};

type RequestOptions<T> = {
  fallback?: T;
  timeoutMs?: number;
};

function buildRequestHeaders(headers?: HeadersInit): HeadersInit {
  const mergedHeaders = new Headers(headers);
  mergedHeaders.set("Content-Type", "application/json");
  if (sessionToken) {
    mergedHeaders.set("Authorization", `Bearer ${sessionToken}`);
  }
  if (currentTenant) {
    mergedHeaders.set("X-ZDash-Tenant", currentTenant);
  }
  if (currentWorkspace) {
    mergedHeaders.set("X-ZDash-Workspace", currentWorkspace);
  }
  return mergedHeaders;
}

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
    return new ApiError(i18n.t('api.timeout'), {
      code: "TIMEOUT",
      status,
      path,
      cause: error,
    });
  }

  if (error instanceof TypeError) {
    return new ApiError(i18n.t('api.network_error'), {
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

    return new ApiError(i18n.t('api.unknown_error'), {
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

function getLegacyErrorMessage(payload: unknown): string | null {
  if (!payload || typeof payload !== "object") return null;

  const candidate = payload as { detail?: unknown; message?: unknown; error?: unknown };

  if (typeof candidate.detail === "string") return candidate.detail;
  if (typeof candidate.message === "string") return candidate.message;
  if (typeof candidate.error === "string") return candidate.error;

  if (Array.isArray(candidate.detail)) {
    return candidate.detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object" && "msg" in item) {
          return String((item as { msg: unknown }).msg);
        }
        return JSON.stringify(item);
      })
      .join("; ");
  }

  return null;
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
      headers: buildRequestHeaders(init.headers),
    });

    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch (error) {
      throw normalizeApiError(
        new ApiError(i18n.t('api.invalid_json'), {
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
      const legacyMessage = getLegacyErrorMessage(payload);

      if (!response.ok && legacyMessage) {
        throw new ApiError(legacyMessage, {
          code: `HTTP_${response.status || 500}`,
          status: response.status,
          path,
          details: payload,
        });
      }

      console.error("[zDash API] Invalid API envelope", {
        path,
        url,
        status: response.status,
        payload,
      });
      throw new ApiError(i18n.t('api.invalid_envelope'), {
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
    if (apiError.status === 401) {
      unauthorizedHandler?.();
    }
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
  patch<T>(
    path: string,
    body?: unknown,
    fallback?: T,
    options?: Omit<RequestOptions<T>, "fallback">,
  ) {
    return request<T>(
      path,
      {
        method: "PATCH",
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

export function setMockFallbackState(active: boolean) {
  mockFallbackActive = active;
}

export const apiGet = apiClient.get;
export const apiPostEnvelope = apiClient.post;

export function setSession(token?: string) {
  sessionToken = token ?? null;
}

export function setTenant(tenantId?: string) {
  currentTenant = tenantId ?? null;
}

export function setWorkspace(workspaceId?: string) {
  currentWorkspace = workspaceId ?? null;
}

export function setUnauthorizedHandler(handler?: () => void) {
  unauthorizedHandler = handler ?? null;
}
