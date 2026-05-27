import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "../App";

describe("App", () => {
  it("renders app", () => {
    window.history.pushState({}, "", "/");
    render(<App />);
    expect(screen.getByText("zDash")).toBeTruthy();
  });

  it("sidebar nav exists", () => {
    window.history.pushState({}, "", "/");
    render(<App />);
    expect(screen.getAllByText("Team Roster").length).toBeGreaterThan(0);
    expect(screen.getByText("Session Logs")).toBeTruthy();
  });

  it("dashboard route works", () => {
    window.history.pushState({}, "", "/");
    render(<App />);
    expect(screen.getByRole("heading", { name: "Team Roster" })).toBeTruthy();
    expect(screen.getByText("Alexander Prime")).toBeTruthy();
    expect(screen.getByText("Agents per page")).toBeTruthy();
  });

  it("unknown route shows NotFound", () => {
    window.history.pushState({}, "", "/does-not-exist");
    render(<App />);
    expect(screen.getByText("Page not found")).toBeTruthy();
  });
});
