import { describe, expect, it } from "vitest";
import { demoRequestPolicy } from "../config/runtime";

describe("public demo request policy", () => {
  it("never sends GET requests to a backend in demo mode", () => {
    expect(demoRequestPolicy("GET", true, true)).toBe("fixture");
    expect(demoRequestPolicy("GET", false, true)).toBe("unavailable");
  });

  it("blocks every state-changing request in demo mode", () => {
    for (const method of ["POST", "PUT", "PATCH", "DELETE"]) {
      expect(demoRequestPolicy(method, true, true)).toBe("blocked");
    }
  });

  it("preserves the existing real API path outside demo mode", () => {
    expect(demoRequestPolicy("GET", false, false)).toBe("network");
    expect(demoRequestPolicy("POST", true, false)).toBe("network");
  });
});
