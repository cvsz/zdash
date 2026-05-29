import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import AITraderSimulationCard from "../components/trading/AITraderSimulationCard";

describe("AI Trader Control Plane", () => {
  it("renders simulation-only controls, strategies, compare, and dry-run wording", async () => {
    const user = userEvent.setup();
    render(<AITraderSimulationCard />);

    expect(screen.getByText("AI Trader Control Plane")).toBeInTheDocument();
    expect(screen.getByText(/Simulation only\. No live broker execution\. Not financial advice/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Strategy/i)).toBeInTheDocument();
    expect(await screen.findByText("Trend Momentum v1")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /Generate simulation signal/i }));
    expect(await screen.findByText(/Decision explanation/i)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /Compare simulation strategies/i }));
    const simulationOnlyCells = await screen.findAllByText(/simulation-only/i);
    expect(simulationOnlyCells.length).toBeGreaterThanOrEqual(4);

    expect(screen.getByRole("button", { name: /Run dry-run paper trade only/i })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Live/i })).not.toBeInTheDocument();
    expect(screen.getByText(/Live trading button intentionally does not exist/i)).toBeInTheDocument();
  });
});
