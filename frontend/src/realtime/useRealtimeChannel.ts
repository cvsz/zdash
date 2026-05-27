import { useEffect, useMemo, useState } from "react";

import {
  getRealtimeClientManager,
  type RealtimeClientManager,
} from "./client";
import type {
  RealtimeChannel,
  RealtimeConnectionState,
  RealtimeEnvelope,
} from "./types";

type UseRealtimeChannelOptions = {
  maxEvents?: number;
  enabled?: boolean;
  eventTypes?: readonly string[];
  manager?: RealtimeClientManager;
};

export type UseRealtimeChannelResult = {
  events: RealtimeEnvelope[];
  connection: RealtimeConnectionState;
  lastEvent: RealtimeEnvelope | null;
  clearEvents: () => void;
};

const DEFAULT_MAX_EVENTS = 120;

export function useRealtimeChannel(
  channel: RealtimeChannel,
  options: UseRealtimeChannelOptions = {},
): UseRealtimeChannelResult {
  const manager = useMemo(
    () => options.manager ?? getRealtimeClientManager(),
    [options.manager],
  );
  const enabled = options.enabled ?? true;
  const maxEvents = Math.max(10, options.maxEvents ?? DEFAULT_MAX_EVENTS);

  const [events, setEvents] = useState<RealtimeEnvelope[]>([]);
  const [connection, setConnection] = useState<RealtimeConnectionState>(() =>
    manager.getState(channel),
  );

  const eventTypesKey = useMemo(
    () => (options.eventTypes?.length ? options.eventTypes.join("|").toLowerCase() : ""),
    [options.eventTypes],
  );

  const normalizedTypes = useMemo(() => {
    if (!options.eventTypes?.length) {
      return null;
    }
    return options.eventTypes.map((value) => value.toLowerCase());
  }, [eventTypesKey]);

  useEffect(() => {
    setConnection(manager.getState(channel));

    if (!enabled) {
      return () => undefined;
    }

    const unsubscribeStatus = manager.subscribeStatus(channel, (next) => {
      setConnection(next);
    });

    const unsubscribeEvents = manager.subscribe(channel, (event) => {
      const eventType = event.type.toLowerCase();
      if (normalizedTypes && !normalizedTypes.some((type) => eventType.startsWith(type))) {
        return;
      }

      setEvents((previous) => {
        const combined = [event, ...previous];
        if (combined.length > maxEvents) {
          combined.length = maxEvents;
        }
        return combined;
      });
    });

    return () => {
      unsubscribeEvents();
      unsubscribeStatus();
    };
  }, [channel, enabled, manager, maxEvents, eventTypesKey, normalizedTypes]);

  return {
    events,
    connection,
    lastEvent: events[0] ?? null,
    clearEvents: () => setEvents([]),
  };
}
