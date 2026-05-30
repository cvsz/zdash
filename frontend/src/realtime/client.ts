import { apiClientConfig } from "../api/client";
import { computeReconnectDelay } from "./reconnect";
import type {
  RealtimeChannel,
  RealtimeConnectionState,
  RealtimeEnvelope,
  RealtimeStatusSubscription,
  RealtimeSubscription,
} from "./types";

function isTestRuntime(): boolean {
  const meta = import.meta as ImportMeta & {
    vitest?: unknown;
    env?: Record<string, string | boolean | undefined>;
  };
  const processEnv = (
    globalThis as {
      process?: { env?: Record<string, string | undefined> };
    }
  ).process?.env;

  return Boolean(
    meta.vitest ||
      meta.env?.VITEST ||
      meta.env?.MODE === "test" ||
      processEnv?.VITEST ||
      processEnv?.NODE_ENV === "test",
  );
}

export function isRealtimeTestRuntime(): boolean {
  return isTestRuntime();
}

const CHANNEL_PATHS: Record<RealtimeChannel, string> = {
  events: "/api/realtime/ws/events",
  risk: "/api/realtime/ws/risk",
  scheduler: "/api/realtime/ws/scheduler",
  content: "/api/realtime/ws/content",
};

type RealtimeClientOptions = {
  enabled?: boolean;
  staleThresholdMs?: number;
  pingIntervalMs?: number;
  reconnectBaseDelayMs?: number;
  reconnectMaxDelayMs?: number;
};

type ChannelRuntime = {
  channel: RealtimeChannel;
  socket: WebSocket | null;
  subscribers: Set<RealtimeSubscription>;
  statusSubscribers: Set<RealtimeStatusSubscription>;
  state: RealtimeConnectionState;
  reconnectTimer: ReturnType<typeof setTimeout> | null;
  countdownTimer: ReturnType<typeof setInterval> | null;
  staleTimer: ReturnType<typeof setInterval> | null;
  pingTimer: ReturnType<typeof setInterval> | null;
  manualClose: boolean;
};

function toWsBaseUrl(rawBaseUrl: string): string {
  const trimmed = rawBaseUrl.trim().replace(/\/+$/, "");
  if (trimmed.startsWith("ws://") || trimmed.startsWith("wss://")) {
    return trimmed;
  }
  if (trimmed.startsWith("http://")) {
    return `ws://${trimmed.slice("http://".length)}`;
  }
  if (trimmed.startsWith("https://")) {
    return `wss://${trimmed.slice("https://".length)}`;
  }

  if (typeof window !== "undefined") {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const host = window.location.host;
    return `${protocol}://${host}`;
  }

  return "ws://localhost:8005";
}

function nowIso(): string {
  return new Date().toISOString();
}

function cloneState(state: RealtimeConnectionState): RealtimeConnectionState {
  return { ...state };
}

export class RealtimeClientManager {
  private readonly enabled: boolean;
  private readonly staleThresholdMs: number;
  private readonly pingIntervalMs: number;
  private readonly reconnectBaseDelayMs: number;
  private readonly reconnectMaxDelayMs: number;
  private readonly wsBaseUrl: string;
  private readonly runtimes = new Map<RealtimeChannel, ChannelRuntime>();

  constructor(options: RealtimeClientOptions = {}) {
    const testDefaultEnabled = isTestRuntime() ? "false" : "true";
    const enabledFromEnv = String(import.meta.env.VITE_REALTIME_ENABLED ?? testDefaultEnabled).toLowerCase() === "true";

    this.enabled = options.enabled ?? enabledFromEnv;
    this.staleThresholdMs = options.staleThresholdMs ?? 20000;
    this.pingIntervalMs = options.pingIntervalMs ?? 10000;
    this.reconnectBaseDelayMs = options.reconnectBaseDelayMs ?? 750;
    this.reconnectMaxDelayMs = options.reconnectMaxDelayMs ?? 15000;

    const wsBaseFromEnv = String(import.meta.env.VITE_WS_BASE_URL ?? "").trim();
    const baseSource = wsBaseFromEnv || apiClientConfig.baseUrl;
    this.wsBaseUrl = toWsBaseUrl(baseSource);

    if (typeof window !== "undefined") {
      window.addEventListener("online", () => this.handleNetworkState(true));
      window.addEventListener("offline", () => this.handleNetworkState(false));
    }
  }

  subscribe(channel: RealtimeChannel, listener: RealtimeSubscription): () => void {
    const runtime = this.ensureRuntime(channel);
    runtime.subscribers.add(listener);

    if (this.enabled) {
      this.openSocket(runtime);
    }

    return () => {
      runtime.subscribers.delete(listener);
      this.cleanupIdleRuntime(runtime);
    };
  }

  subscribeStatus(channel: RealtimeChannel, listener: RealtimeStatusSubscription): () => void {
    const runtime = this.ensureRuntime(channel);
    runtime.statusSubscribers.add(listener);
    listener(cloneState(runtime.state));

    if (this.enabled) {
      this.openSocket(runtime);
    }

    return () => {
      runtime.statusSubscribers.delete(listener);
      this.cleanupIdleRuntime(runtime);
    };
  }

  getState(channel: RealtimeChannel): RealtimeConnectionState {
    const runtime = this.runtimes.get(channel);
    if (runtime) {
      return cloneState(runtime.state);
    }
    return this.createDefaultState(channel);
  }

  disconnect(channel: RealtimeChannel): void {
    const runtime = this.runtimes.get(channel);
    if (!runtime) {
      return;
    }

    runtime.manualClose = true;
    this.clearReconnectTimers(runtime);
    this.clearPeriodicTimers(runtime);

    const socket = runtime.socket;
    runtime.socket = null;

    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
      socket.close(1000);
    }

    runtime.state.connected = false;
    runtime.state.connecting = false;
    runtime.state.retryInMs = null;
    this.emitStatus(runtime);
  }

  reset(): void {
    for (const channel of this.runtimes.keys()) {
      this.disconnect(channel);
    }
    this.runtimes.clear();
  }

  private ensureRuntime(channel: RealtimeChannel): ChannelRuntime {
    const existing = this.runtimes.get(channel);
    if (existing) {
      return existing;
    }

    const online = typeof navigator === "undefined" ? true : navigator.onLine !== false;
    const runtime: ChannelRuntime = {
      channel,
      socket: null,
      subscribers: new Set<RealtimeSubscription>(),
      statusSubscribers: new Set<RealtimeStatusSubscription>(),
      state: this.createDefaultState(channel, online),
      reconnectTimer: null,
      countdownTimer: null,
      staleTimer: null,
      pingTimer: null,
      manualClose: false,
    };

    runtime.staleTimer = setInterval(() => {
      if (!runtime.state.connected || !runtime.state.lastMessageAt) {
        return;
      }

      const elapsedMs = Date.now() - Date.parse(runtime.state.lastMessageAt);
      const stale = elapsedMs > this.staleThresholdMs;
      if (stale !== runtime.state.stale) {
        runtime.state.stale = stale;
        this.emitStatus(runtime);
      }

      if (stale && runtime.socket && runtime.socket.readyState === WebSocket.OPEN) {
        runtime.socket.close(1011, "stale");
      }
    }, 1500);

    this.runtimes.set(channel, runtime);
    return runtime;
  }

  private createDefaultState(
    channel: RealtimeChannel,
    online: boolean | null = null,
  ): RealtimeConnectionState {
    const onlineState =
      online ??
      (typeof navigator === "undefined" ? true : navigator.onLine !== false);
    return {
      channel,
      connected: false,
      connecting: false,
      stale: false,
      online: onlineState,
      retryAttempt: 0,
      retryInMs: null,
      lastMessageAt: null,
      lastHeartbeatAt: null,
    };
  }

  private cleanupIdleRuntime(runtime: ChannelRuntime): void {
    const hasSubscribers = runtime.subscribers.size > 0 || runtime.statusSubscribers.size > 0;
    if (hasSubscribers) {
      return;
    }

    this.disconnect(runtime.channel);
    this.runtimes.delete(runtime.channel);
  }

  private openSocket(runtime: ChannelRuntime): void {
    if (!this.enabled) {
      return;
    }

    if (typeof WebSocket === "undefined") {
      runtime.state.connected = false;
      runtime.state.connecting = false;
      runtime.state.retryInMs = null;
      this.emitStatus(runtime);
      return;
    }

    if (runtime.socket && (runtime.socket.readyState === WebSocket.OPEN || runtime.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    runtime.manualClose = false;
    runtime.state.connecting = true;
    runtime.state.stale = false;
    runtime.state.retryInMs = null;
    this.clearReconnectTimers(runtime);
    this.emitStatus(runtime);

    const socket = new WebSocket(`${this.wsBaseUrl}${CHANNEL_PATHS[runtime.channel]}`);
    runtime.socket = socket;

    socket.onopen = () => {
      runtime.state.connected = true;
      runtime.state.connecting = false;
      runtime.state.stale = false;
      runtime.state.retryAttempt = 0;
      runtime.state.retryInMs = null;
      runtime.state.lastMessageAt = nowIso();
      this.emitStatus(runtime);

      this.clearPingTimer(runtime);
      runtime.pingTimer = setInterval(() => {
        if (!runtime.socket || runtime.socket.readyState !== WebSocket.OPEN) {
          return;
        }
        runtime.socket.send(JSON.stringify({ type: "system.ping" }));
      }, this.pingIntervalMs);
    };

    socket.onmessage = (event) => {
      const parsed = this.parseEnvelope(event.data);
      if (!parsed) {
        return;
      }

      runtime.state.lastMessageAt = nowIso();
      runtime.state.stale = false;

      if (parsed.type === "system.ping") {
        runtime.state.lastHeartbeatAt = nowIso();
        if (runtime.socket && runtime.socket.readyState === WebSocket.OPEN) {
          runtime.socket.send(JSON.stringify({ type: "system.pong" }));
        }
      }

      this.emitStatus(runtime);
      for (const subscriber of runtime.subscribers) {
        subscriber(parsed);
      }
    };

    socket.onerror = () => {
      runtime.state.connecting = false;
      this.emitStatus(runtime);
    };

    socket.onclose = () => {
      runtime.socket = null;
      this.clearPingTimer(runtime);
      runtime.state.connected = false;
      runtime.state.connecting = false;
      this.emitStatus(runtime);

      if (runtime.manualClose) {
        return;
      }
      if (runtime.subscribers.size === 0 && runtime.statusSubscribers.size === 0) {
        return;
      }
      this.scheduleReconnect(runtime);
    };
  }

  private scheduleReconnect(runtime: ChannelRuntime): void {
    runtime.state.retryAttempt += 1;

    const delay = computeReconnectDelay(runtime.state.retryAttempt - 1, {
      baseDelayMs: this.reconnectBaseDelayMs,
      maxDelayMs: this.reconnectMaxDelayMs,
      jitterRatio: 0,
    });

    runtime.state.retryInMs = delay;
    this.emitStatus(runtime);

    this.clearReconnectTimers(runtime);

    const startedAt = Date.now();
    runtime.countdownTimer = setInterval(() => {
      const elapsed = Date.now() - startedAt;
      const remaining = Math.max(0, delay - elapsed);
      runtime.state.retryInMs = remaining;
      this.emitStatus(runtime);
      if (remaining === 0 && runtime.countdownTimer) {
        clearInterval(runtime.countdownTimer);
        runtime.countdownTimer = null;
      }
    }, 200);

    runtime.reconnectTimer = setTimeout(() => {
      runtime.reconnectTimer = null;
      this.openSocket(runtime);
    }, delay);
  }

  private parseEnvelope(raw: unknown): RealtimeEnvelope | null {
    try {
      const parsed = typeof raw === "string" ? JSON.parse(raw) : raw;
      if (!parsed || typeof parsed !== "object") {
        return null;
      }

      const candidate = parsed as Partial<RealtimeEnvelope>;
      if (typeof candidate.type !== "string") {
        return null;
      }

      const payload =
        candidate.payload && typeof candidate.payload === "object"
          ? (candidate.payload as Record<string, unknown>)
          : {};

      return {
        id: typeof candidate.id === "string" ? candidate.id : `local-${Date.now()}`,
        category: typeof candidate.category === "string" ? (candidate.category as RealtimeEnvelope["category"]) : "system",
        type: candidate.type,
        source: typeof candidate.source === "string" ? candidate.source : "system",
        timestamp: typeof candidate.timestamp === "string" ? candidate.timestamp : nowIso(),
        severity:
          candidate.severity === "critical"
            ? "critical"
            : candidate.severity === "warning"
              ? "warning"
              : "info",
        message: typeof candidate.message === "string" ? candidate.message : String(payload.message ?? ""),
        data: candidate.data && typeof candidate.data === "object" ? (candidate.data as Record<string, unknown>) : payload,
        payload,
      };
    } catch {
      return null;
    }
  }

  private handleNetworkState(online: boolean): void {
    for (const runtime of this.runtimes.values()) {
      runtime.state.online = online;
      this.emitStatus(runtime);
      if (online && !runtime.state.connected) {
        this.openSocket(runtime);
      }
    }
  }

  private emitStatus(runtime: ChannelRuntime): void {
    const snapshot = cloneState(runtime.state);
    for (const subscriber of runtime.statusSubscribers) {
      subscriber(snapshot);
    }
  }

  private clearReconnectTimers(runtime: ChannelRuntime): void {
    if (runtime.reconnectTimer) {
      clearTimeout(runtime.reconnectTimer);
      runtime.reconnectTimer = null;
    }
    if (runtime.countdownTimer) {
      clearInterval(runtime.countdownTimer);
      runtime.countdownTimer = null;
    }
  }

  private clearPingTimer(runtime: ChannelRuntime): void {
    if (runtime.pingTimer) {
      clearInterval(runtime.pingTimer);
      runtime.pingTimer = null;
    }
  }

  private clearPeriodicTimers(runtime: ChannelRuntime): void {
    if (runtime.staleTimer) {
      clearInterval(runtime.staleTimer);
      runtime.staleTimer = null;
    }
    this.clearPingTimer(runtime);
  }
}

let singletonRealtimeManager: RealtimeClientManager | null = null;

export function getRealtimeClientManager(): RealtimeClientManager {
  if (!singletonRealtimeManager) {
    singletonRealtimeManager = new RealtimeClientManager();
  }
  return singletonRealtimeManager;
}

export function resetRealtimeClientManager(): void {
  singletonRealtimeManager?.reset();
  singletonRealtimeManager = null;
}

export function createRealtimeClientManager(
  options: RealtimeClientOptions = {},
): RealtimeClientManager {
  return new RealtimeClientManager(options);
}
