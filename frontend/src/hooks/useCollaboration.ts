import { useEffect, useMemo, useState } from "react";

import { readStoredSession } from "../api/auth";

const DEFAULT_API_BASE_URL = "http://localhost:8005";

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
  return trimmed || "ws://localhost:8005";
}

export function buildCollaborationWsUrl(
  workspaceId: string,
  options?: { apiBaseUrl?: string; wsBaseUrl?: string },
): string {
  const wsBaseFromEnv = options?.wsBaseUrl?.trim() || String(import.meta.env.VITE_WS_BASE_URL ?? "").trim();
  const apiBaseFromEnv = options?.apiBaseUrl?.trim() || String(import.meta.env.VITE_API_BASE_URL ?? "").trim();
  const baseSource = wsBaseFromEnv || apiBaseFromEnv || DEFAULT_API_BASE_URL;
  return `${toWsBaseUrl(baseSource)}/api/collaboration/ws/collaboration/${workspaceId}`;
}

export function useCollaboration(workspaceId: string) {
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let timer: number | undefined;
    try {
      const session = readStoredSession();
      const token = session?.accessToken?.trim();
      const wsUrl = buildCollaborationWsUrl(workspaceId);
      ws = token ? new WebSocket(wsUrl, ["bearer", token]) : new WebSocket(wsUrl);
      ws.onopen = () => setConnected(true);
      ws.onclose = () => setConnected(false);
      ws.onmessage = (evt) => {
        const msg = JSON.parse(String(evt.data));
        setEvents((prev) => [msg, ...prev].slice(0, 100));
      };
      timer = window.setInterval(() => ws?.readyState === WebSocket.OPEN && ws.send(JSON.stringify({ type: "presence.update" })), 30000);
    } catch {
      setConnected(false);
    }
    return () => {
      if (timer) window.clearInterval(timer);
      ws?.close();
    };
  }, [workspaceId]);

  return useMemo(() => ({ connected, events }), [connected, events]);
}
