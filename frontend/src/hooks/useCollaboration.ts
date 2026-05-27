import { useEffect, useMemo, useState } from "react";

export function useCollaboration(workspaceId: string) {
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let timer: number | undefined;
    try {
      ws = new WebSocket(`${window.location.origin.replace("http", "ws")}/api/collaboration/ws/collaboration/${workspaceId}`);
      ws.onopen = () => setConnected(true);
      ws.onclose = () => setConnected(false);
      ws.onmessage = (evt) => {
        const msg = JSON.parse(evt.data);
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
