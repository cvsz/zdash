import { vi } from "vitest";
import type { RealtimeConnectionState, RealtimeEnvelope } from "../../realtime/types";

const mockConnectionState: RealtimeConnectionState = {
  channel: "content",
  connected: false,
  connecting: false,
  stale: false,
  online: false,
  retryAttempt: 0,
  retryInMs: null,
  lastMessageAt: null,
  lastHeartbeatAt: null,
};

type UseRealtimeChannelResult = {
  events: RealtimeEnvelope[];
  connection: RealtimeConnectionState;
  lastEvent: RealtimeEnvelope | null;
  clearEvents: () => void;
};

const mockResult: UseRealtimeChannelResult = {
  events: [],
  connection: { ...mockConnectionState },
  lastEvent: null,
  clearEvents: vi.fn(),
};

export function buildMockRealtimeHooks() {
  return {
    useRealtime: vi.fn(() => ({ ...mockResult, connection: { ...mockConnectionState, channel: "events" as const } })),
    useRiskRealtime: vi.fn(() => ({ ...mockResult, connection: { ...mockConnectionState, channel: "risk" as const } })),
    useSchedulerRealtime: vi.fn(() => ({ ...mockResult, connection: { ...mockConnectionState, channel: "scheduler" as const } })),
    useContentRealtime: vi.fn(() => ({ ...mockResult, connection: { ...mockConnectionState, channel: "content" as const } })),
  };
}

export const mockRealtimeResult = mockResult;
