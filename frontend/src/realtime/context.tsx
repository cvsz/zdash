import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { useRealtime } from "./useRealtime";

type RealtimeContextValue = {
  state: "connected" | "disconnected" | "reconnecting" | "polling";
  events: ReturnType<typeof useRealtime>["events"];
  unread: number;
  clearUnread: () => void;
};

export const RealtimeContext = createContext<RealtimeContextValue | null>(null);

export function RealtimeProvider({ children }: { children: ReactNode }) {
  const realtime = useRealtime({ maxEvents: 200, enabled: true });
  const [seenCount, setSeenCount] = useState(0);

  const state: RealtimeContextValue["state"] = realtime.connection.connected
    ? "connected"
    : realtime.connection.connecting
      ? "reconnecting"
      : realtime.connection.online
        ? "polling"
        : "disconnected";

  const unread = Math.max(0, realtime.events.length - seenCount);
  const value = useMemo(
    () => ({
      state,
      events: realtime.events,
      unread,
      clearUnread: () => setSeenCount(realtime.events.length),
    }),
    [state, realtime.events, unread],
  );

  return <RealtimeContext.Provider value={value}>{children}</RealtimeContext.Provider>;
}

export function useRealtimeContext() {
  const value = useContext(RealtimeContext);
  if (!value) throw new Error("useRealtimeContext must be used inside RealtimeProvider");
  return value;
}
