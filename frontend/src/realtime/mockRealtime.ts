import type { RealtimeEnvelope } from "./types";

export function getMockRealtimeEvents(): RealtimeEnvelope[] {
  return [{ id: "evt_mock_1", category: "system", type: "system.alert", timestamp: new Date().toISOString(), source: "mock.realtime", severity: "warning", message: "Mock fallback mode", data: { mock: true }, payload: { mock: true } }];
}
