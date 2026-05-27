import { getAgents, sendAgentMessage } from "../api/endpoints";
import type { Agent } from "../api/types";
import { useApi } from "./useApi";

type AgentMessagePayload = {
  from_agent: string;
  to_agent: string;
  message: string;
  context?: Record<string, unknown>;
};

export const useAgents = () => {
  const state = useApi<Agent[]>(getAgents, []);

  return {
    ...state,
    sendMessage: (payload: AgentMessagePayload) => sendAgentMessage(payload),
  };
};
