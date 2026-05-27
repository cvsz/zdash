import { isRealtimeTestRuntime, type RealtimeClientManager } from "./client";
import { useRealtimeChannel } from "./useRealtimeChannel";

type UseRealtimeOptions = {
  enabled?: boolean;
  maxEvents?: number;
  manager?: RealtimeClientManager;
};

function defaultEnabled(enabled?: boolean): boolean {
  if (typeof enabled === "boolean") {
    return enabled;
  }
  return !isRealtimeTestRuntime();
}

export function useRealtime(options: UseRealtimeOptions = {}) {
  return useRealtimeChannel("events", {
    ...options,
    enabled: defaultEnabled(options.enabled),
  });
}

export function useRiskRealtime(options: UseRealtimeOptions = {}) {
  return useRealtimeChannel("risk", {
    ...options,
    enabled: defaultEnabled(options.enabled),
    eventTypes: ["risk."],
  });
}

export function useSchedulerRealtime(options: UseRealtimeOptions = {}) {
  return useRealtimeChannel("scheduler", {
    ...options,
    enabled: defaultEnabled(options.enabled),
    eventTypes: ["scheduler."],
  });
}

export function useContentRealtime(options: UseRealtimeOptions = {}) {
  return useRealtimeChannel("content", {
    ...options,
    enabled: defaultEnabled(options.enabled),
    eventTypes: ["content."],
  });
}
