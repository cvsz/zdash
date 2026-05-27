import type { RealtimeConnectionState, RealtimeEnvelope } from "./types";

export type RealtimeStore = { events: RealtimeEnvelope[]; connection: RealtimeConnectionState | null; reconnects: number };
export const defaultRealtimeStore: RealtimeStore = { events: [], connection: null, reconnects: 0 };
