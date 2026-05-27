import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { resetMockFallbackState, setMockFallbackState } from "../api/client";
import Dashboard from "../pages/Dashboard";

describe("Dashboard", () => {
  afterEach(() => {
    resetMockFallbackState();
  });

  it("renders module summary sections", () => {
    render(<Dashboard />);

    expect(screen.getByText("System Health")).toBeTruthy();
    expect(screen.getByText("Backend Connection")).toBeTruthy();
    expect(screen.getByText("Agent Status Summary")).toBeTruthy();
    expect(screen.getByText("Recent Session Logs")).toBeTruthy();
    expect(screen.getByText("Team Roster")).toBeTruthy();
  });

  it("renders mock fallback banner when fallback is active", () => {
    setMockFallbackState(true);
    render(<Dashboard />);

    expect(screen.getByText(/Mock fallback mode active/i)).toBeTruthy();
  });
});
