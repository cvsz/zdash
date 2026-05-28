import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Usage } from "../pages/Usage";

// Mock the API endpoints so we don't make network calls in tests
vi.mock("../api/endpoints", () => {
  return {
    getUsageSummary: vi.fn(async () => ({
      metrics: {
        backtest_runs: { limit: 100, usage: 85 }, // > 80% to trigger warning
        marketplace_plugins: { limit: 5, usage: 5 }, // 100% to trigger exceeded
        iot_actions: { limit: 50, usage: 10 },
      },
      reset_timestamp: "2026-06-28T00:00:00Z",
    })),
  };
});

describe("Usage Page", () => {
  it("renders usage cards, quota warning at >80%, and exceeded quota banner", async () => {
    render(<Usage />);

    // Renders usage labels
    expect(await screen.findByText("Backtest Runs")).toBeTruthy();
    expect(await screen.findByText("Marketplace Plugins")).toBeTruthy();
    expect(await screen.findByText("IoT Actions")).toBeTruthy();

    // Warning at >80%
    expect(
      await screen.findByText(/Approaching usage limit/i)
    ).toBeTruthy();

    // Exceeded banner
    expect(
      await screen.findByText(/Limit exceeded! Some operations in this category are blocked/i)
    ).toBeTruthy();
  });
});
