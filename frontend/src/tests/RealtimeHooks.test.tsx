import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { createRealtimeClientManager } from "../realtime/client";
import { useRealtime } from "../realtime/useRealtime";

class MockWebSocket {
  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSING = 2;
  static readonly CLOSED = 3;
  static instances: MockWebSocket[] = [];

  readyState = MockWebSocket.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;

  constructor(public readonly url: string) {
    MockWebSocket.instances.push(this);
  }

  send(): void {
    return;
  }

  close(): void {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.({} as CloseEvent);
  }

  emitOpen(): void {
    this.readyState = MockWebSocket.OPEN;
    this.onopen?.(new Event("open"));
  }

  emitJson(payload: Record<string, unknown>): void {
    this.onmessage?.({ data: JSON.stringify(payload) } as MessageEvent);
  }

  static reset(): void {
    this.instances = [];
  }
}

function RealtimeHarness({ manager }: { manager: ReturnType<typeof createRealtimeClientManager> }) {
  const realtime = useRealtime({ enabled: true, manager, maxEvents: 5 });

  return (
    <div>
      <span data-testid="connected">{String(realtime.connection.connected)}</span>
      <span data-testid="event-count">{String(realtime.events.length)}</span>
      <span data-testid="last-type">{realtime.lastEvent?.type ?? "none"}</span>
    </div>
  );
}

describe("realtime hooks", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    MockWebSocket.reset();
  });

  it("useRealtime consumes websocket events and connection state", () => {
    vi.stubGlobal("WebSocket", MockWebSocket as unknown as typeof WebSocket);

    const manager = createRealtimeClientManager({ enabled: true, staleThresholdMs: 60000 });

    render(<RealtimeHarness manager={manager} />);

    expect(MockWebSocket.instances.length).toBe(1);
    const socket = MockWebSocket.instances[0];

    socket.emitOpen();

    expect(screen.getByTestId("connected").textContent).toBe("true");

    socket.emitJson({
      type: "scheduler.completed",
      timestamp: new Date().toISOString(),
      source: "SchedulerService",
      severity: "success",
      payload: { message: "Scheduler run completed" },
    });

    expect(screen.getByTestId("event-count").textContent).toBe("1");
    expect(screen.getByTestId("last-type").textContent).toBe("scheduler.completed");

    manager.reset();
  });
});
