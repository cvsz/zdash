import { render, screen, waitForElementToBeRemoved } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { resetMockFallbackState, setMockFallbackState } from "../api/client";
import Dashboard from "../pages/Dashboard";
import { waitForStableUi } from "./utils/settle";

describe("Dashboard", () => {
  afterEach(() => {
    resetMockFallbackState();
  });

  it("renders metric cards and key sections", async () => {
    render(<Dashboard />);

    await waitForStableUi();
    await waitForElementToBeRemoved(() => screen.queryByText(/Loading/i), { timeout: 2000 }).catch(() => {});

    expect(await screen.findByText((t) => t.includes("System Health"))).toBeTruthy();
    expect(await screen.findByText((t) => t.includes("Agents Online"))).toBeTruthy();
    expect(await screen.findByText((t) => t.includes("Trading Mode"))).toBeTruthy();
    expect(await screen.findByText((t) => t.includes("Risk Level"))).toBeTruthy();
    expect(await screen.findByText("Phase Progress")).toBeTruthy();
    expect(await screen.findByText((t) => t.includes("Session Logs"))).toBeTruthy();
  });

  it("renders mock fallback banner when fallback is active", async () => {
    setMockFallbackState(true);
    render(<Dashboard />);

    expect(await screen.findByText(/Mock fallback mode active/i)).toBeTruthy();
  });
});
