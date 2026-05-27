import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import RiskPanel from "../pages/RiskPanel";

describe("RiskPanel", () => {
  it("renders kill-switch, halt, and drawdown risk status", () => {
    render(<RiskPanel />);

    expect(screen.getByText("Risk Panel")).toBeTruthy();
    expect(screen.getByText("Kill Switch")).toBeTruthy();
    expect(screen.getByText("Total Drawdown")).toBeTruthy();
    expect(screen.getByText("Manual Halt")).toBeTruthy();
    expect(screen.getByText("Manual halt")).toBeTruthy();
    expect(screen.getByText("Manual Resume")).toBeTruthy();
    expect(screen.getByPlaceholderText("Resume reason")).toBeTruthy();
  });

  it("requires resume reason before confirmation", () => {
    render(<RiskPanel />);

    const resumeButton = screen.getByText("Resume trading") as HTMLButtonElement;
    expect(resumeButton.disabled).toBe(true);

    fireEvent.change(screen.getByPlaceholderText("Resume reason"), {
      target: { value: "Risk normalized" },
    });

    expect((screen.getByText("Resume trading") as HTMLButtonElement).disabled).toBe(false);
    fireEvent.click(screen.getByText("Resume trading"));

    expect(screen.getByText("Confirm manual resume")).toBeTruthy();
  });
});
