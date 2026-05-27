export type RealtimeChannel = "events" | "risk" | "scheduler" | "content";
export type RealtimeSeverity = "info" | "warning" | "critical";

export type RealtimeEnvelope = {
  id: string;
  category: "system" | "trading" | "risk" | "scheduler" | "content" | "iot" | "admin" | "audit";
  type: string;
  timestamp: string;
  source: string;
  severity: RealtimeSeverity;
  message: string;
  data: Record<string, unknown>;
  payload: Record<string, unknown>;
};

export type RealtimeConnectionState = {
  channel: RealtimeChannel;
  connected: boolean;
  connecting: boolean;
  stale: boolean;
  online: boolean;
  retryAttempt: number;
  retryInMs: number | null;
  lastMessageAt: string | null;
  lastHeartbeatAt: string | null;
};

export type RealtimeSubscription = (event: RealtimeEnvelope) => void;
export type RealtimeStatusSubscription = (state: RealtimeConnectionState) => void;
