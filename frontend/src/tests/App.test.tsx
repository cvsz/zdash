import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "../App";

function renderAt(path: string) {
  window.history.pushState({}, "", path);
  return render(<App />);
}

describe("App routing", () => {
  it("app renders", () => {
    renderAt("/");
    expect(screen.getByText("zDash")).toBeTruthy();
  });

  it("sidebar navigation exists", () => {
    renderAt("/");
    expect(screen.getAllByText("Team Roster").length).toBeGreaterThan(0);
    expect(screen.getByText("Session Logs")).toBeTruthy();
  });

  it("dashboard route works", () => {
    renderAt("/");
    expect(screen.getByRole("heading", { name: "Dashboard", level: 2 })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Team Roster", level: 1 })).toBeTruthy();
  });

  it("renders risk route", () => {
    renderAt("/risk");
    expect(screen.getByRole("heading", { name: "Risk Panel", level: 2 })).toBeTruthy();
    expect(screen.getByText("Manual Halt")).toBeTruthy();
  });

  it("renders scheduler route", () => {
    renderAt("/scheduler");
    expect(screen.getByRole("heading", { name: "Scheduler", level: 2 })).toBeTruthy();
    expect(screen.getByText("Default Jobs")).toBeTruthy();
  });

  it("renders content route", () => {
    renderAt("/content");
    expect(screen.getByRole("heading", { name: "Content Pipeline", level: 2 })).toBeTruthy();
    expect(screen.getByText("SOCIAL_DRY_RUN")).toBeTruthy();
  });

  it("renders not-found route", () => {
    renderAt("/does-not-exist");
    expect(screen.getByText("Page not found")).toBeTruthy();
  });
});
