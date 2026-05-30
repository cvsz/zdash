import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { resetMockFallbackState } from "../api/client";
import ZFinance from "../pages/ZFinance";

describe("ZFinance", () => {
  afterEach(() => {
    resetMockFallbackState();
  });

  it("renders page title header", () => {
    render(<ZFinance />);

    expect(screen.getByRole("heading", { name: "zFinance" })).toBeTruthy();
  });

  it("renders subtitle with read-only disclaimer", () => {
    render(<ZFinance />);

    expect(screen.getByText(/Read-only safe-link adapter/)).toBeTruthy();
  });

  it("renders warning badges", () => {
    render(<ZFinance />);

    expect(screen.getByText("Read-only")).toBeTruthy();
    expect(screen.getByText("No scraping")).toBeTruthy();
    expect(screen.getByText("Not financial advice")).toBeTruthy();
  });
});
