/** Public demo never receives backend authority or production credentials. */
export const isPublicDemo =
  String(import.meta.env.VITE_PUBLIC_DEMO ?? "false").toLowerCase() === "true";

export const isProductionBuild = import.meta.env.PROD && !isPublicDemo;

export const frontendAuthRequired =
  isProductionBuild ||
  String(import.meta.env.VITE_AUTH_ENABLED ?? "false").toLowerCase() === "true";

export const mockFallbackAllowed =
  isPublicDemo ||
  (!isProductionBuild &&
    String(import.meta.env.VITE_ENABLE_MOCK_FALLBACK ?? "false").toLowerCase() ===
      "true");

export const realtimeAllowed =
  !isPublicDemo &&
  String(import.meta.env.VITE_REALTIME_ENABLED ?? "true").toLowerCase() === "true";

/** A demo is an offline, read-only view; never issue API mutations. */
export function demoRequestPolicy(
  method: string,
  hasFallback: boolean,
  demo = isPublicDemo,
): "network" | "fixture" | "unavailable" | "blocked" {
  if (!demo) return "network";
  if (method.toUpperCase() !== "GET") return "blocked";
  return hasFallback ? "fixture" : "unavailable";
}
