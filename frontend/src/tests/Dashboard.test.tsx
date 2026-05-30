import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { resetMockFallbackState, setMockFallbackState } from "../api/client";
import Dashboard from "../pages/Dashboard";

describe("Dashboard", () => {
  afterEach(() => {
    resetMockFallbackState();
  });

  it("renders metric cards and key sections", () => {
    render(<Dashboard />);

    expect(screen.getByText((t) => t.includes("System Health"))).toBeTruthy();
    expect(screen.getByText((t) => t.includes("Agents Online"))).toBeTruthy();
    expect(screen.getByText((t) => t.includes("Trading Mode"))).toBeTruthy();
    expect(screen.getByText((t) => t.includes("Risk Level"))).toBeTruthy();
    expect(screen.getByText("Phase Progress")).toBeTruthy();
    expect(screen.getByText((t) => t.includes("Session Logs"))).toBeTruthy();
  });

  it("renders mock fallback banner when fallback is active", () => {
    setMockFallbackState(true);
    render(<Dashboard />);

    expect(screen.getByText(/Mock fallback mode active/i)).toBeTruthy();
  });
});
