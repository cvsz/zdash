import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import RealtimeEventFeed from "../components/realtime/RealtimeEventFeed";

describe("RealtimeEventFeed", () => {
  it("renders empty state", () => {
    render(<RealtimeEventFeed title="Live Feed" events={[]} emptyMessage="Waiting" />);
    expect(screen.getByText("Live Feed")).toBeTruthy();
    expect(screen.getByText("Waiting")).toBeTruthy();
  });

  it("renders realtime events with payload messages", () => {
    render(
      <RealtimeEventFeed
        title="Live Feed"
        events={[
          {
            type: "risk.alert",
            timestamp: new Date().toISOString(),
            source: "guardian",
            severity: "warning",
            payload: { message: "Drawdown warning" },
          },
        ]}
      />,
    );

    expect(screen.getByText("risk.alert")).toBeTruthy();
    expect(screen.getByText("Drawdown warning")).toBeTruthy();
    expect(screen.getByText(/guardian/i)).toBeTruthy();
  });
});
