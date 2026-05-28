import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Billing } from "../pages/Billing";

// Mock the API endpoints so we don't make network calls in tests
vi.mock("../api/endpoints", () => {
  return {
    getBillingStatus: vi.fn(async () => ({
      status: "active",
      plan_tier: "pro",
      plan_id: "pro",
      provider: "mock",
      cancel_at_period_end: false,
      current_period_start: "2026-05-28T00:00:00Z",
      current_period_end: "2026-06-28T00:00:00Z",
      trial_ends_at: null,
    })),
    getBillingPlans: vi.fn(async () => [
      {
        id: "free",
        tier: "free",
        name: "Free Plan",
        description: "Basic trading operations",
        price_monthly: 0,
        price_yearly: 0,
        features: ["Backtest runs", "Basic signals"],
        limits: { backtest_runs: 10, content_generation_tokens: 0, marketplace_plugins: 0, iot_actions: 0 },
      },
      {
        id: "pro",
        tier: "pro",
        name: "Pro Plan",
        description: "Advanced automation and safety",
        price_monthly: 49,
        price_yearly: 490,
        features: ["Backtest runs", "Advanced signals"],
        limits: { backtest_runs: 200, content_generation_tokens: 50000, marketplace_plugins: 5, iot_actions: 100 },
      },
    ]),
    getInvoices: vi.fn(async () => [
      {
        id: "inv-001",
        number: "INV-2026-001",
        amount: 49.0,
        currency: "usd",
        status: "paid",
        created_at: "2026-05-01T00:00:00Z",
        pdf_url: "https://mock-pdf.test",
      },
    ]),
    startCheckout: vi.fn(),
    openBillingPortal: vi.fn(),
    cancelSubscription: vi.fn(),
    applyMockPlan: vi.fn(),
  };
});

describe("Billing Page", () => {
  it("renders subscription status, pricing table, plan comparison, and invoice history table", async () => {
    render(<Billing />);

    // Renders current plan status
    expect((await screen.findAllByText(/pro Plan/i)).length).toBeGreaterThan(0);

    // Renders mock billing banner when provider is mock
    expect(await screen.findByText(/Mock Billing Mode/i)).toBeTruthy();

    // Renders plan details / pricing table
    expect((await screen.findAllByText("Free Plan")).length).toBeGreaterThan(0);
    expect((await screen.findAllByText("Pro Plan")).length).toBeGreaterThan(0);

    // Renders invoice table
    expect(await screen.findByText("INV-2026-001")).toBeTruthy();
    expect(await screen.findByText("$49.00 USD")).toBeTruthy();
  });
});
