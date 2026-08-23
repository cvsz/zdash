import { render, screen, waitForElementToBeRemoved } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { resetMockFallbackState, setMockFallbackState } from "../api/client";
import Dashboard from "../pages/Dashboard";
import { waitForStableUi } from "./utils/settle";

describe("Dashboard", () => {
  afterEach(() => {
    resetMockFallbackState();
  });

  it("renders the mission-control information hierarchy", async () => {
    render(<Dashboard />);

    await waitForStableUi();
    await waitForElementToBeRemoved(() => screen.queryByText(/Loading/i), { timeout: 2000 }).catch(() => {});

    expect(await screen.findByText("Operational pulse")).toBeTruthy();
    expect(await screen.findByText("Service health")).toBeTruthy();
    expect(await screen.findByText("Live activity")).toBeTruthy();
    expect(await screen.findByText("Diagnostics & release")).toBeTruthy();

    expect(await screen.findByText((t) => t.includes("System Health"))).toBeTruthy();
    expect(await screen.findByText((t) => t.includes("Agents Online"))).toBeTruthy();
    expect(await screen.findByText((t) => t.includes("Trading Mode"))).toBeTruthy();
    expect(await screen.findByText((t) => t.includes("Risk Level"))).toBeTruthy();
    expect(await screen.findByText((t) => t.includes("Scheduler"))).toBeTruthy();
    expect(await screen.findByText((t) => t.includes("Backend"))).toBeTruthy();
  });

  it("keeps release diagnostics secondary but available", async () => {
    render(<Dashboard />);

    await waitForStableUi();

    expect(await screen.findByText("Phase Progress")).toBeTruthy();
    expect(await screen.findByText((t) => t.includes("Session Logs"))).toBeTruthy();
    expect(await screen.findByText("Release Gate")).toBeTruthy();
  });

  it("renders mock fallback banner when fallback is active", async () => {
    setMockFallbackState(true);
    render(<Dashboard />);

    expect(await screen.findByText(/Mock fallback mode active/i)).toBeTruthy();
  });
});
