import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  getRealtimeClientManager,
  resetRealtimeClientManager,
} from "../realtime/client";
import type { RealtimeChannel } from "../realtime/types";

class FakeWebSocket {
  static instances: FakeWebSocket[] = [];
  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSING = 2;
  static readonly CLOSED = 3;
  readyState = FakeWebSocket.CONNECTING;
  url: string;
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    FakeWebSocket.instances.push(this);
  }
  send() {}
  close() {
    this.readyState = FakeWebSocket.CLOSED;
    this.onclose?.();
  }
  static reset() {
    FakeWebSocket.instances = [];
  }
}

type MockGlobal = typeof globalThis & { WebSocket: unknown };

const channels: RealtimeChannel[] = ["events", "risk", "scheduler", "content"];

beforeEach(() => {
  vi.stubEnv("VITE_API_BASE_URL", "http://localhost:8005");
  vi.stubEnv("VITE_REALTIME_ENABLED", "true");
  FakeWebSocket.reset();
  (globalThis as MockGlobal).WebSocket = FakeWebSocket as unknown as typeof WebSocket;
  resetRealtimeClientManager();
});

afterEach(() => {
  resetRealtimeClientManager();
  vi.unstubAllEnvs();
});

describe("RealtimeClient", () => {
  it("maps events channel to /api/realtime/ws/events", () => {
    const mgr = getRealtimeClientManager();
    mgr.subscribe("events", vi.fn());
    expect(FakeWebSocket.instances[0]?.url).toMatch(/\/api\/realtime\/ws\/events$/);
  });

  it("maps risk channel to /api/realtime/ws/risk", () => {
    const mgr = getRealtimeClientManager();
    mgr.subscribe("risk", vi.fn());
    expect(FakeWebSocket.instances[0]?.url).toMatch(/\/api\/realtime\/ws\/risk$/);
  });

  it("maps scheduler channel to /api/realtime/ws/scheduler", () => {
    const mgr = getRealtimeClientManager();
    mgr.subscribe("scheduler", vi.fn());
    expect(FakeWebSocket.instances[0]?.url).toMatch(/\/api\/realtime\/ws\/scheduler$/);
  });

  it("maps content channel to /api/realtime/ws/content", () => {
    const mgr = getRealtimeClientManager();
    mgr.subscribe("content", vi.fn());
    expect(FakeWebSocket.instances[0]?.url).toMatch(/\/api\/realtime\/ws\/content$/);
  });

  it("returns disabled state when VITE_REALTIME_ENABLED=false", () => {
    vi.stubEnv("VITE_REALTIME_ENABLED", "false");
    resetRealtimeClientManager();
    const mgr = getRealtimeClientManager();
    const state = mgr.getState("events");
    expect(state.connected).toBe(false);
    expect(state.connecting).toBe(false);
    expect(state.retryInMs).toBeNull();
  });

  it("tracks connection state changes", () => {
    const mgr = getRealtimeClientManager();
    mgr.subscribeStatus("events", vi.fn());
    const socket = FakeWebSocket.instances[0];
    expect(socket).toBeDefined();
  });

  it("uses ping interval to send keepalive pings", () => {
    const originalSetInterval = globalThis.setInterval;
    const captured: Array<{ delay: number }> = [];
    vi.spyOn(globalThis, "setInterval").mockImplementation(((fn: TimerHandler, delay: number, ...args: unknown[]) => {
      captured.push({ delay });
      return 123 as unknown as ReturnType<typeof setInterval>;
    }) as typeof globalThis.setInterval);
    const mgr = getRealtimeClientManager();
    mgr.subscribe("events", vi.fn());
    const socket = FakeWebSocket.instances[0];
    socket.onopen?.();
    const pingInterval = captured.find((c) => c.delay === 10000);
    expect(pingInterval).toBeDefined();
    vi.restoreAllMocks();
  });

  it("reset clears all channels", () => {
    const mgr = getRealtimeClientManager();
    for (const ch of channels) {
      mgr.subscribe(ch, vi.fn());
    }
    expect(FakeWebSocket.instances.length).toBeGreaterThanOrEqual(channels.length);
    mgr.reset();
    for (const ch of channels) {
      const state = mgr.getState(ch);
      expect(state.connected).toBe(false);
      expect(state.connecting).toBe(false);
    }
  });
});
