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
    expect(await screen.findByText(/Safety Guidelines & Sandbox Rules/i)).toBeTruthy();
    expect(await screen.findByText(/Drawdown Risk Guardian checks enabled by default/i)).toBeTruthy();

    // Onboarding checklist steps render
    expect(await screen.findByText("create organization")).toBeTruthy();
    expect(await screen.findByText("invite team")).toBeTruthy();

    // Quick actions are present and dry-run labeled
    expect(screen.getByRole("button", { name: /Run Dry-Run Scan/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /Run Backtest/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /Create Content Item/i })).toBeTruthy();
  });
});
