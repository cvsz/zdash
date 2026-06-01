import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "../App";
import { waitForStableUi } from "./utils/settle";

function renderAt(path: string) {
  window.history.pushState({}, "", path);
  return render(<App />);
}

describe("App routing", () => {
  it("app renders", async () => {
    renderAt("/");
    await waitForStableUi();
    const heading = await screen.findByRole("heading", { name: (name) => name.replace(/\s/g, "").toLowerCase() === "zdash" });
    expect(heading).toBeTruthy();
  });

  it("sidebar navigation exists", async () => {
    renderAt("/");
    await waitForStableUi();
    expect((await screen.findAllByText("Team")).length).toBeGreaterThan(0);
    const sessionLogsLinks = await screen.findAllByText("Session Logs");
    expect(sessionLogsLinks.length).toBeGreaterThan(0);
  });

  it("dashboard route works", async () => {
    renderAt("/");
    await waitForStableUi();
    expect(await screen.findByRole("heading", { name: "Dashboard", level: 2 })).toBeTruthy();
    expect(await screen.findByRole("heading", { name: "Team Workspace", level: 1 })).toBeTruthy();
  });

  it("renders risk route", async () => {
    renderAt("/risk");
    await waitForStableUi();
    expect(await screen.findByRole("heading", { name: "Risk Management", level: 2 })).toBeTruthy();
    expect(await screen.findByText("Manual Halt")).toBeTruthy();
  });

  it("renders scheduler route", async () => {
    renderAt("/scheduler");
    await waitForStableUi();
    expect(await screen.findByRole("heading", { name: "Scheduler", level: 2 })).toBeTruthy();
    expect(await screen.findByText("Default Jobs")).toBeTruthy();
  });

  it("renders content route", async () => {
    renderAt("/content");
    await waitForStableUi();
    expect(await screen.findByRole("heading", { name: "Content Pipeline", level: 2 })).toBeTruthy();
    expect((await screen.findAllByText("Social Dry Run")).length).toBeGreaterThan(0);
  });

  it("renders not-found route", async () => {
    renderAt("/does-not-exist");
    await waitForStableUi();
    expect(await screen.findByText("404 — Page Not Found")).toBeTruthy();
  });
});
