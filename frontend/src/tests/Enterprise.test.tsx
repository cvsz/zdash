import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Enterprise } from "../pages/Enterprise";

// Mock the API endpoints so we don't make network calls in tests
vi.mock("../api/endpoints", () => {
  return {
    getEnterpriseStatus: vi.fn(async () => ({
      license: {
        organization_id: "org-1",
        status: "active",
        tier: "enterprise",
        seats: 50,
        features: ["feature.branding", "feature.exports"],
        expires_at: "2027-05-28T00:00:00Z",
        offline_mode: false,
        issued_to: "Zeaz Inc",
      },
      branding: {
        organization_id: "org-1",
        workspace_id: "ws-1",
        brand_name: "zDash Custom Title",
        logo_url: "",
        primary_color: "#7c3aed",
        accent_color: "#22c55e",
        support_email: "support@zeaz.dev",
        custom_domain: "dash.zeaz.dev",
      },
    })),
    getLicenseStatus: vi.fn(),
    applyLicense: vi.fn(),
    revokeLicense: vi.fn(),
    getBrandingSettings: vi.fn(),
    updateBrandingSettings: vi.fn(),
    resetBrandingSettings: vi.fn(),
    listExportBundles: vi.fn(async () => [
      {
        id: "exp-001",
        organization_id: "org-1",
        workspace_id: "ws-1",
        export_type: "full",
        status: "completed",
        file_path: "/exports/bundle_001.zip",
        include_audit_logs: true,
        include_content: true,
        include_backtests: false,
        include_scheduler: true,
        include_secrets: false,
        created_by: "admin@zeaz.dev",
        created_at: "2026-05-20T00:00:00Z",
      },
    ]),
    createExportBundle: vi.fn(),
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
      active_users: 2,
      usage_trend: "stable",
    })),
  };
});

describe("Enterprise Page", () => {
  it("renders license status, branding editor, onboarding checklist, and enforces export secrets validation input check", async () => {
    render(<Enterprise />);

    // Renders license details
    expect(await screen.findByText("50 operators")).toBeTruthy();
    expect(await screen.findByText("Zeaz Inc")).toBeTruthy();

    // Renders whitelabel branding editor settings name
    const brandNameInput = await screen.findByDisplayValue("zDash Custom Title");
    expect(brandNameInput).toBeTruthy();

    // Onboarding checklist step renders
    expect(await screen.findByText("create organization")).toBeTruthy();
    expect(await screen.findByText("invite team")).toBeTruthy();

    // Export panel requires CONFIRM_SECRET_EXPORT confirmation input before submit
    const secretsCheckbox = await screen.findByLabelText(/Include Encryption Keys & Private API Credentials/i);
    fireEvent.click(secretsCheckbox);

    // Prompt warning appears
    expect(screen.getByText(/WARNING: Exporting raw secrets and keys is high-risk/i)).toBeTruthy();

    // Generate button is disabled initially since typing input is missing
    const generateBtn = screen.getByRole("button", { name: /Generate Export Bundle/i });
    expect((generateBtn as HTMLButtonElement).disabled).toBe(true);

    // Type incorrect value
    const confirmInput = screen.getByPlaceholderText("Type CONFIRM_SECRET_EXPORT");
    fireEvent.change(confirmInput, { target: { value: "WRONG_VALUE" } });
    expect((generateBtn as HTMLButtonElement).disabled).toBe(true);

    // Type correct value
    fireEvent.change(confirmInput, { target: { value: "CONFIRM_SECRET_EXPORT" } });
    expect((generateBtn as HTMLButtonElement).disabled).toBe(false);
  });
});
