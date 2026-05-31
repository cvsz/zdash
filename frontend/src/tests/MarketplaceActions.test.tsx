import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Marketplace } from "../pages/Marketplace";

const mockPlugins = [
  {
    id: "plugin-tapo",
    name: "Tapo Smart Plug Controller",
    slug: "tapo-controller",
    version: "1.0.2",
    description: "Control smart plugs and devices automatically based on risk events.",
    author: "zDash Team",
    category: "iot",
    status: "approved",
    required_features: ["feature.iot"],
    required_permissions: ["iot_control"],
    config_schema: {},
    default_config: {},
    entrypoint: "main.py",
    safety_level: "sandbox",
    source_type: "builtin",
    source_ref: null,
    checksum: null,
    metadata_json: {},
  },
  {
    id: "plugin-slack",
    name: "Slack Webhook Notifier",
    slug: "slack-notifier",
    version: "2.1.0",
    description: "Send system alerts to Slack channels.",
    author: "Slack Inc.",
    category: "notifications",
    status: "approved",
    required_features: [],
    required_permissions: [],
    config_schema: {},
    default_config: {},
    entrypoint: "slack.py",
    safety_level: "restricted",
    source_type: "builtin",
    source_ref: null,
    checksum: null,
    metadata_json: {},
  },
];

const mockInstallations = [
  {
    id: "inst-tapo",
    organization_id: "org-1",
    workspace_id: "ws-1",
    plugin_id: "plugin-tapo",
    version: "1.0.2",
    status: "enabled",
    config_json: {},
    enabled: true,
    installed_by: "admin@zeaz.dev",
    installed_at: "2026-05-20T00:00:00Z",
  },
];

vi.mock("../api/endpoints", () => {
  const installFn = vi.fn(async () => ({
    ok: true, id: "inst-slack", source_type: "builtin",
  }));
  const enableFn = vi.fn(async () => ({ ok: true }));
  const disableFn = vi.fn(async () => ({ ok: true }));
  const uninstallFn = vi.fn(async () => ({ ok: true }));
  const runActionFn = vi.fn(async () => ({
    ok: true,
    output: { status: "simulated_success", dry_run: true },
  }));

  return {
    listMarketplacePlugins: vi.fn(async () => mockPlugins),
    listPluginInstallations: vi.fn(async () => mockInstallations),
    listPluginCategories: vi.fn(async () => ["risk", "backtesting", "content", "automation", "notifications", "compliance"]),
    installMarketplacePlugin: installFn,
    enablePluginInstallation: enableFn,
    disablePluginInstallation: disableFn,
    uninstallPluginInstallation: uninstallFn,
    runPluginAction: runActionFn,
  };
});

describe("Marketplace Actions", () => {
  it("renders install button for not-installed plugin", async () => {
    render(<Marketplace />);
    const installBtns = await screen.findAllByRole("button", { name: /Install/i });
    expect(installBtns.length).toBeGreaterThan(0);
  });

  it("renders enable/disable and uninstall buttons for installed plugin", async () => {
    render(<Marketplace />);
    const uninstallBtns = await screen.findAllByRole("button", { name: /Uninstall/i });
    expect(uninstallBtns.length).toBeGreaterThan(0);

    const disableBtns = await screen.findAllByRole("button", { name: /Disable/i });
    expect(disableBtns.length).toBeGreaterThan(0);
  });

  it("renders console button for installed plugin", async () => {
    render(<Marketplace />);
    const consoleBtns = await screen.findAllByRole("button", { name: /Console/i });
    expect(consoleBtns.length).toBeGreaterThan(0);
  });

  it("opens detail panel with dry-run console when console clicked", async () => {
    render(<Marketplace />);
    const consoleBtns = await screen.findAllByRole("button", { name: /Console/i });
    fireEvent.click(consoleBtns[0]);

    expect(await screen.findByText("Dry-Run Plugin Console")).toBeTruthy();
    expect(screen.getByText(/Simulate actions/i)).toBeTruthy();
  });

  it("detail panel shows action form and run button", async () => {
    render(<Marketplace />);
    const consoleBtns = await screen.findAllByRole("button", { name: /Console/i });
    fireEvent.click(consoleBtns[0]);

    expect(await screen.findByText("Dry-Run Plugin Console")).toBeTruthy();

    const actionInput = screen.getByPlaceholderText(/e\.g\. test_action/i);
    expect(actionInput).toBeTruthy();

    const runBtn = screen.getByRole("button", { name: /Run Dry-Run Action/i });
    expect(runBtn).toBeTruthy();
  });

  it("detail panel shows source type for builtin plugin", async () => {
    render(<Marketplace />);
    const consoleBtns = await screen.findAllByRole("button", { name: /Console/i });
    fireEvent.click(consoleBtns[0]);

    expect(await screen.findByText(/builtin/i)).toBeTruthy();
  });

  it("render shows safety badge on plugin cards", async () => {
    render(<Marketplace />);
    const sandboxBadges = await screen.findAllByText(/sandbox/i);
    expect(sandboxBadges.length).toBeGreaterThan(0);
  });
});
