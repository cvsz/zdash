import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Scheduler from "../pages/Scheduler";

describe("Scheduler", () => {
  it("renders scheduler controls and safety labels", async () => {
    render(<Scheduler />);

    expect(screen.getByRole("heading", { name: "Scheduler", level: 2 })).toBeTruthy();
    expect(screen.getByText("Default Jobs")).toBeTruthy();
    expect(screen.getByText("Job Table")).toBeTruthy();
    expect(screen.getByText("Create Job")).toBeTruthy();
    expect(screen.getAllByText("iot_power_cycle").length).toBeGreaterThan(0);
    expect(screen.getAllByText("trading_scan").length).toBeGreaterThan(0);
    expect(screen.getByText("Confirmation warning")).toBeTruthy();
    expect(screen.getByText("Approval required, no auto-publish")).toBeTruthy();
    const runButtons = await screen.findAllByRole("button", { name: "Run" });
    expect(runButtons.length).toBeGreaterThan(0);
  });
});
