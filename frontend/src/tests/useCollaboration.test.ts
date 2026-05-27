import { renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { buildCollaborationWsUrl, useCollaboration } from "../hooks/useCollaboration";
import { readStoredSession } from "../api/auth";

vi.mock("../api/auth", () => ({
  readStoredSession: vi.fn(() => null),
}));

class MockWebSocket {
  static instances: MockWebSocket[] = [];
  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSING = 2;
  static readonly CLOSED = 3;

  public readyState = MockWebSocket.CONNECTING;
  public onopen: ((event: Event) => void) | null = null;
  public onmessage: ((event: MessageEvent) => void) | null = null;
  public onclose: ((event: CloseEvent) => void) | null = null;

  constructor(
    public readonly url: string,
    public readonly protocols?: string | string[],
  ) {
    MockWebSocket.instances.push(this);
  }

  send(): void {
    return;
  }

  close(): void {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.({} as CloseEvent);
  }

  static reset(): void {
    this.instances = [];
  }
}

const mockedReadStoredSession = vi.mocked(readStoredSession);

describe("useCollaboration", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    mockedReadStoredSession.mockReset();
    mockedReadStoredSession.mockReturnValue(null);
    MockWebSocket.reset();
  });

  it("derives ws URL from API base", () => {
    const url = buildCollaborationWsUrl("w1", {
      apiBaseUrl: "http://localhost:8005/",
      wsBaseUrl: "",
    });
    expect(url).toBe("ws://localhost:8005/api/collaboration/ws/collaboration/w1");
  });

  it("prefers explicit ws base URL when provided", () => {
    const url = buildCollaborationWsUrl("w1", {
      apiBaseUrl: "http://localhost:8005",
      wsBaseUrl: "wss://realtime.example.com/",
    });
    expect(url).toBe("wss://realtime.example.com/api/collaboration/ws/collaboration/w1");
  });

  it("passes bearer token as websocket subprotocol when session exists", () => {
    vi.stubGlobal("WebSocket", MockWebSocket as unknown as typeof WebSocket);
    mockedReadStoredSession.mockReturnValue({
      accessToken: "token-123",
      refreshToken: "refresh-123",
    });

    const { unmount } = renderHook(() => useCollaboration("workspace-a"));
    expect(MockWebSocket.instances).toHaveLength(1);
    const socket = MockWebSocket.instances[0];
    expect(socket.url.startsWith("ws://") || socket.url.startsWith("wss://")).toBe(true);
    expect(socket.url.endsWith("/api/collaboration/ws/collaboration/workspace-a")).toBe(
      true,
    );
    expect(socket.protocols).toEqual(["bearer", "token-123"]);

    unmount();
  });
});
