export type RealtimeChannel = "events" | "risk" | "scheduler" | "content";

export type RealtimeSeverity = "info" | "warning" | "danger" | "success";

export type RealtimeEnvelope = {
  type: string;
  timestamp: string;
  source: string;
  severity: RealtimeSeverity;
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
