import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import RiskPanel from "../pages/RiskPanel";
import { waitForStableUi } from "./utils/settle";

describe("RiskPanel", () => {
  it("renders kill-switch, halt, and drawdown risk status", async () => {
    render(<RiskPanel />);
    await waitForStableUi();

    expect(await screen.findByText("Risk Panel")).toBeTruthy();
    expect(await screen.findByText("Kill Switch")).toBeTruthy();
    expect(await screen.findByText("Total Drawdown")).toBeTruthy();
    expect(await screen.findByText("Manual Halt")).toBeTruthy();
    expect(await screen.findByText("Manual halt")).toBeTruthy();
    expect(await screen.findByText("Manual Resume")).toBeTruthy();
    expect(await screen.findByPlaceholderText("Resume reason")).toBeTruthy();
  });

  it("requires resume reason before confirmation", async () => {
    render(<RiskPanel />);
    await waitForStableUi();

    const resumeButton = screen.getByText("Resume trading") as HTMLButtonElement;
    expect(resumeButton.disabled).toBe(true);

    fireEvent.change(screen.getByPlaceholderText("Resume reason"), {
      target: { value: "Risk normalized" },
    });

    expect((screen.getByText("Resume trading") as HTMLButtonElement).disabled).toBe(false);
    fireEvent.click(screen.getByText("Resume trading"));

    expect(await screen.findByText("Confirm manual resume")).toBeTruthy();
  });
});
