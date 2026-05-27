import { useRealtime } from "../realtime/useRealtime";

export function useRealtimeEvents() {
  const realtime = useRealtime();
  return {
    events: realtime.events,
    connected: realtime.connection.connected && !realtime.connection.stale,
  };
}
