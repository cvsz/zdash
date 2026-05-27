import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { resetMockFallbackState, setMockFallbackState } from "../api/client";
import Dashboard from "../pages/Dashboard";

describe("Dashboard", () => {
  afterEach(() => {
    resetMockFallbackState();
  });

  it("renders team roster on the main dashboard", () => {
    render(<Dashboard />);

    expect(screen.getByText("Team Roster")).toBeTruthy();
    expect(screen.getByText("Alexander Prime")).toBeTruthy();
    expect(screen.getByText("Sophia Lane")).toBeTruthy();
    expect(screen.getByText("Agents per page")).toBeTruthy();
    expect(screen.getByText("Guardian Risk")).toBeTruthy();
    expect(screen.getByText("Content Pipeline")).toBeTruthy();
  });

  it("renders mock fallback banner when fallback is active", () => {
    setMockFallbackState(true);
    render(<Dashboard />);
    expect(screen.getByText(/Mock fallback mode active/i)).toBeTruthy();
  });
});
