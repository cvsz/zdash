import { apiClient } from "./client";

export type VoiceIntegrationStatus = {
  enabled: boolean;
  configured: boolean;
  model: string;
  subject: string;
};

export type VoiceSessionGrant = {
  ticket: string;
  websocket_url: string;
  expires_at: string;
  ticket_transport: "sec-websocket-protocol";
  model: string;
  instructions: string;
};

export function getVoiceIntegrationStatus() {
  return apiClient.get<VoiceIntegrationStatus>("/api/voice/status", undefined, {
    timeoutMs: 5000,
  });
}

export function createVoiceSession(instructions: string) {
  return apiClient.post<VoiceSessionGrant>(
    "/api/voice/session",
    { instructions },
    undefined,
    { timeoutMs: 8000 },
  );
}
