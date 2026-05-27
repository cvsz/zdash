import {
  getAgents,
  getContentStatus,
  getHealth,
  getIoTStatus,
  getRiskStatus,
  getSchedulerStatus,
  getTradingStatus,
} from "../api/endpoints";
import type { Agent, HealthStatus, IoTActionResult } from "../api/types";
import { useApi } from "./useApi";

export type SystemStatusSnapshot = {
  health: HealthStatus;
  agents: Agent[];
  risk: Record<string, unknown>;
  scheduler: Record<string, unknown>;
  content: Record<string, unknown>;
  iot: IoTActionResult | Record<string, unknown>;
  trading: Record<string, unknown>;
};

export const useSystemStatus = () =>
  useApi<SystemStatusSnapshot>(
    async () => {
      const [health, agents, risk, scheduler, content, iot, trading] =
        await Promise.all([
          getHealth(),
          getAgents(),
          getRiskStatus(),
          getSchedulerStatus(),
          getContentStatus(),
          getIoTStatus(),
          getTradingStatus(),
        ]);

      return { health, agents, risk, scheduler, content, iot, trading };
    },
    [],
  );
