import { useEffect, useRef, useState } from "react";

import { getLogs } from "../api/endpoints";
import type { EventLog } from "../api/types";

type RealtimeStatus =
  | "connecting"
  | "connected"
  | "polling"
  | "disconnected";

export function resolveRealtimeBaseUrl(): string {
  const configuredWsBase = import.meta.env.VITE_WS_BASE_URL?.trim();
  if (configuredWsBase && /^wss?:\/\//i.test(configuredWsBase)) {
    return configuredWsBase.replace(/\/+$/, "");
  }

  const configuredApiBase = import.meta.env.VITE_API_BASE_URL?.trim();
  if (configuredApiBase && /^https?:\/\//i.test(configuredApiBase)) {
    return configuredApiBase.replace(/^http/i, "ws").replace(/\/+$/, "");
  }

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}`;
}

export function useRealtimeEvents() {
  const [events, setEvents] = useState<EventLog[]>([]);
  const [status, setStatus] = useState<RealtimeStatus>("connecting");
  const statusRef = useRef(status);

  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  useEffect(() => {
    let mounted = true;
    const wsUrl = `${resolveRealtimeBaseUrl()}/api/realtime/ws`;
    let ws: WebSocket | null = null;
    let pollInterval: number | null = null;

    const startPolling = () => {
      if (!mounted || statusRef.current === "polling") return;

      setStatus("polling");
      const poll = async () => {
        try {
          const fetchedEvents = await getLogs();
          if (mounted) setEvents(fetchedEvents);
        } catch (error) {
          console.error("Polling error", error);
        }
      };

      void poll();
      pollInterval = window.setInterval(
        poll,
        Number(import.meta.env.VITE_POLL_INTERVAL_MS || 5000),
      );
    };

    try {
      ws = new WebSocket(wsUrl);
      ws.onopen = () => {
        if (mounted) setStatus("connected");
      };
      ws.onmessage = (event) => {
        if (!mounted) return;

        try {
          const parsed = JSON.parse(event.data) as EventLog;
          setEvents((previous) => [parsed, ...previous]);
        } catch {
          console.warn("Ignored malformed realtime event");
        }
      };
      ws.onerror = startPolling;
      ws.onclose = startPolling;
    } catch {
      startPolling();
    }

    return () => {
      mounted = false;
      ws?.close();
      if (pollInterval !== null) clearInterval(pollInterval);
    };
  }, []);

  return { events, status };
}
