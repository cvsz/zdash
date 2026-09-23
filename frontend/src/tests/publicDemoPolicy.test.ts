import { afterEach, describe, expect, it, vi } from "vitest";
import { demoRequestPolicy } from "../config/runtime";

describe("public demo request policy", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
    vi.resetModules();
  });

  it("never sends GET requests to a backend in demo mode", () => {
    expect(demoRequestPolicy("GET", true, true)).toBe("fixture");
    expect(demoRequestPolicy("GET", false, true)).toBe("unavailable");
  });

  it("blocks every state-changing request in demo mode", () => {
    for (const method of ["POST", "PUT", "PATCH", "DELETE"]) {
      expect(demoRequestPolicy(method, true, true)).toBe("blocked");
    }
  });

  it("blocks fetch for demo reads and mutations", async () => {
    vi.stubEnv("VITE_PUBLIC_DEMO", "true");
    vi.resetModules();
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    const { apiClient } = await import("../api/client");

    await expect(apiClient.get("/api/health", { status: "simulated" })).resolves.toEqual({
      status: "simulated",
    });
    await expect(apiClient.post("/api/risk/halt", { enabled: true })).rejects.toMatchObject({
      code: "DEMO_READ_ONLY",
    });
    await expect(apiClient.get("/api/unavailable")).rejects.toMatchObject({
      code: "DEMO_FIXTURE_UNAVAILABLE",
    });
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("preserves the existing real API path outside demo mode", () => {
    expect(demoRequestPolicy("GET", false, false)).toBe("network");
    expect(demoRequestPolicy("POST", true, false)).toBe("network");
  });
});
