import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Onboarding } from "../pages/Onboarding";

// Mock the API endpoints so we don't make network calls in tests
vi.mock("../api/endpoints", () => {
  return {
    getEnterpriseStatus: vi.fn(async () => ({
      license: { status: "active", tier: "enterprise" },
      branding: { brand_name: "zDash" },
    })),
    getOnboardingChecklist: vi.fn(async () => ({
      organization_id: "org-1",
      workspace_id: "ws-1",
      completed_steps: ["create organization"],
      pending_steps: ["invite team"],
      progress_percent: 50.0,
    })),
    completeOnboardingStep: vi.fn(),
    resetOnboardingChecklist: vi.fn(),
    getCustomerHealth: vi.fn(async () => ({
      health_score: 50.0,
      status: "fair",
      active_users: 1,
      usage_trend: "stable",
    })),
    listExportBundles: vi.fn(async () => []),
  };
});

describe("Onboarding Page", () => {
  it("renders onboarding checklists, safety checklists, and dry-run labeled actions", async () => {
    render(<Onboarding />);

    // Safety guidelines section renders
    const safetyHeadings = await screen.findAllByText(/Safety Guidelines/i, {}, { timeout: 3000 });
    expect(safetyHeadings.length).toBeGreaterThan(0);
    expect(await screen.findByText(/Drawdown Risk Guardian checks enabled by default/i, {}, { timeout: 3000 })).toBeTruthy();

    // Onboarding checklist steps render
    expect(await screen.findByText("create organization")).toBeTruthy();
    expect(await screen.findByText("invite team")).toBeTruthy();

    // Quick actions are present and dry-run labeled
    expect(await screen.findByText(/Run Dry-Run Scan/i, {}, { timeout: 4000 })).toBeTruthy();
    expect(await screen.findByText(/Run Backtest/i, {}, { timeout: 4000 })).toBeTruthy();
    expect(await screen.findByText(/Create Content Item/i, {}, { timeout: 4000 })).toBeTruthy();
  });
});
