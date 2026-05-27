import { afterEach, describe, expect, it, vi } from "vitest";

import { createRealtimeClientManager } from "../realtime/client";
import type { RealtimeEnvelope } from "../realtime/types";

class MockWebSocket {
  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSING = 2;
  static readonly CLOSED = 3;
  static instances: MockWebSocket[] = [];

  readonly url: string;
  readyState = MockWebSocket.CONNECTING;
  sentMessages: string[] = [];

  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }

  send(message: string): void {
    this.sentMessages.push(message);
  }

  close(): void {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.({} as CloseEvent);
  }

  emitOpen(): void {
    this.readyState = MockWebSocket.OPEN;
    this.onopen?.(new Event("open"));
  }

  emitMessage(payload: RealtimeEnvelope): void {
    this.onmessage?.({ data: JSON.stringify(payload) } as MessageEvent);
  }

  emitClose(): void {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.({} as CloseEvent);
  }

  static reset(): void {
    this.instances = [];
  }
}

describe("RealtimeClientManager", () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
    MockWebSocket.reset();
  });

  it("connects to a channel and delivers typed events", () => {
    vi.stubGlobal("WebSocket", MockWebSocket as unknown as typeof WebSocket);

    const manager = createRealtimeClientManager({ enabled: true, staleThresholdMs: 60000 });
    const events: RealtimeEnvelope[] = [];

    const unsubscribe = manager.subscribe("events", (event) => {
      events.push(event);
    });

    expect(MockWebSocket.instances.length).toBe(1);
    const socket = MockWebSocket.instances[0];
    expect(socket.url.endsWith("/ws/events")).toBe(true);

    socket.emitOpen();
    socket.emitMessage({
      type: "system.ping",
      timestamp: new Date().toISOString(),
      source: "realtime.heartbeat",
      severity: "info",
      payload: {},
    });
    socket.emitMessage({
      type: "risk.alert",
      timestamp: new Date().toISOString(),
      source: "guardian",
      severity: "warning",
      payload: { message: "Drawdown warning" },
    });

    expect(events.some((event) => event.type === "risk.alert")).toBe(true);
    expect(socket.sentMessages.some((message) => message.includes("system.pong"))).toBe(true);

    unsubscribe();
    manager.reset();
  });

  it("reconnects after socket close with backoff", () => {
    vi.useFakeTimers();
    vi.stubGlobal("WebSocket", MockWebSocket as unknown as typeof WebSocket);

    const manager = createRealtimeClientManager({
      enabled: true,
      reconnectBaseDelayMs: 100,
      reconnectMaxDelayMs: 100,
      staleThresholdMs: 60000,
    });

    const unsubscribe = manager.subscribe("risk", () => undefined);

    expect(MockWebSocket.instances.length).toBe(1);
    const first = MockWebSocket.instances[0];
    first.emitOpen();
    first.emitClose();

    vi.advanceTimersByTime(110);
    expect(MockWebSocket.instances.length).toBe(2);

    unsubscribe();
    manager.reset();
  });
});
