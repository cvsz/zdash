import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Marketplace } from "../pages/Marketplace";

// Mock the API endpoints so we don't make network calls in tests
vi.mock("../api/endpoints", () => {
  return {
    listMarketplacePlugins: vi.fn(async () => [
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
        metadata_json: {},
      },
    ]),
    listPluginInstallations: vi.fn(async () => [
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
    ]),
    installMarketplacePlugin: vi.fn(),
    enablePluginInstallation: vi.fn(),
    disablePluginInstallation: vi.fn(),
    uninstallPluginInstallation: vi.fn(),
    runPluginAction: vi.fn(),
  };
});

describe("Marketplace Page", () => {
  it("renders plugin grid, safety notes, installed plugins table, and install button", async () => {
    render(<Marketplace />);

    // Renders available plugin card in grid
    expect(await screen.findByText("Slack Webhook Notifier")).toBeTruthy();

    // Renders safety rating badge / notes
    expect(await screen.findByText(/Highly isolated runtime/i)).toBeTruthy();

    // Renders install button for not yet installed plugins
    const installButtons = await screen.findAllByRole("button", { name: /Install/i });
    expect(installButtons.length).toBeGreaterThan(0);

    // Renders installed plugins list
    expect(await screen.findByText("plugin-tapo")).toBeTruthy();
    expect((await screen.findAllByText("Tapo Smart Plug Controller")).length).toBeGreaterThan(0);
  });
});
