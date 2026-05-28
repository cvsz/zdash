import { useState, useEffect, useRef } from "react";
import { getLogs } from "../api/endpoints";
import type { EventLog } from "../api/types";

export function useRealtimeEvents() {
  const [events, setEvents] = useState<EventLog[]>([]);
  const [status, setStatus] = useState<"connecting" | "connected" | "polling" | "disconnected">("connecting");
  const statusRef = useRef(status);

  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  useEffect(() => {
    let mounted = true;
    const baseUrl = import.meta.env.VITE_WS_BASE_URL || import.meta.env.VITE_API_BASE_URL?.replace("http", "ws") || "ws://localhost:8005";
    const wsUrl = baseUrl + "/api/realtime/ws";
    let ws: WebSocket | null = null;
    let pollInterval: number | null = null;

    const startPolling = () => {
      if (!mounted) return;
      if (statusRef.current === "polling") return;
      setStatus("polling");
      const poll = async () => {
        try {
          const fetchedEvents = await getLogs();
          if (mounted) setEvents(fetchedEvents);
        } catch (e) {
          console.error("Polling error", e);
        }
      };
      poll();
      pollInterval = window.setInterval(poll, Number(import.meta.env.VITE_POLL_INTERVAL_MS || 5000));
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
          setEvents((prev) => [parsed, ...prev]);
        } catch (e) {}
      };
      ws.onerror = () => {
        if (mounted) {
           startPolling();
        }
      };
      ws.onclose = () => {
        if (mounted) {
           startPolling();
        }
      };
    } catch (e) {
       startPolling();
    }

    return () => {
      mounted = false;
      if (ws) ws.close();
      if (pollInterval !== null) clearInterval(pollInterval);
    };
  }, []);

  return { events, status };
}
