import { useMemo } from "react";
import { useRealtime } from "./useRealtime";

export function useRealtimeChannel() { return useRealtime(); }
export function useIncidentFeed() {
  const rt = useRealtime();
  return useMemo(() => rt.events.filter((e) => e.type.startsWith("incident.")), [rt.events]);
}
export function useOperatorPresence() {
  const rt = useRealtime();
  return useMemo(() => rt.events.filter((e) => e.type === "operator.presence"), [rt.events]);
}
export function useLiveMetrics() {
  const rt = useRealtime();
  return useMemo(() => rt.events.filter((e) => e.type.startsWith("system.")), [rt.events]);
}
