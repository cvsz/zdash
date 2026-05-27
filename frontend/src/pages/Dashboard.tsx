import { mockFallbackActive } from "../api/client";
import { getBacktestingStatus, getLogs, listBacktestResults } from "../api/endpoints";
import StatusCard from "../components/common/StatusCard";
import SectionCard from "../components/common/SectionCard";
import Badge from "../components/common/Badge";
import PageHeader from "../components/layout/PageHeader";
import LiveIndicator from "../components/realtime/LiveIndicator";
import RealtimeConnectionBanner from "../components/realtime/RealtimeConnectionBanner";
import RealtimeEventFeed from "../components/realtime/RealtimeEventFeed";
import RealtimeStatusBadge from "../components/realtime/RealtimeStatusBadge";
import { AGENT_NAME_BY_ID } from "../constants/agents";
import { useApi } from "../hooks/useApi";
import {
  useContentRealtime,
  useRealtime,
  useRiskRealtime,
  useSchedulerRealtime,
} from "../realtime/useRealtime";
import { useSystemStatus } from "../hooks/useSystemStatus";
import { formatDateTime, formatPercent } from "../utils/format";
import { getSeverityFromStatus } from "../utils/status";
import TeamRoster from "./TeamRoster";

function readBoolean(value: unknown, fallback = false): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function readString(value: unknown, fallback = "unknown"): string {
  return typeof value === "string" && value.length > 0 ? value : fallback;
}

function readNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

export default function Dashboard() {
  const { data } = useSystemStatus();
  const realtime = useRealtime({ maxEvents: 20 });
  const riskRealtime = useRiskRealtime({ maxEvents: 6 });
  const schedulerRealtime = useSchedulerRealtime({ maxEvents: 6 });
  const contentRealtime = useContentRealtime({ maxEvents: 6 });
  const backtestingStatus = useApi(getBacktestingStatus, []);
  const backtestResults = useApi(listBacktestResults, []);
  const logsState = useApi(getLogs, []);

  const healthStatus = readString(data?.health?.status, "loading");
  const backendConnected = healthStatus.toLowerCase() === "ok" && !mockFallbackActive;

  const agents = data?.agents ?? [];
  const onlineAgents = agents.filter((agent) => readString(agent.status).toLowerCase() === "online").length;
  const totalAgents = agents.length;

  const tradingDryRun = readBoolean(data?.trading?.dry_run, true);
  const riskLevel = readString(data?.risk?.risk_level, "unknown");
  const haltState = data?.risk?.halt_state as Record<string, unknown> | undefined;
  const halted = readBoolean(haltState?.halted, false);
  const killSwitchActive = readBoolean(data?.risk?.kill_switch_active, false);

  const schedulerRunning = readBoolean(data?.scheduler?.running, false);
  const schedulerEnabled = readBoolean(data?.scheduler?.enabled, false);

  const contentApprovalRequired = readBoolean(data?.content?.approval_required, true);
  const socialDryRun = readBoolean(data?.content?.social_dry_run, true);

  const iotDryRun = readBoolean((data?.iot as Record<string, unknown> | undefined)?.dry_run, true);
  const iotAlias = readString(
    (data?.iot as Record<string, unknown> | undefined)?.device_alias,
    "-",
  );

  const backtestPrimaryStrategy = readString(backtestingStatus.data?.primary_strategy, "ob_aggressive");
  const latestBacktest = backtestResults.data?.[0] ?? null;

  const latestLogs = (logsState.data ?? []).slice(0, 6);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        subtitle="Live session overview with dry-run-safe defaults and guardrails enabled."
        actions={
          <>
            <RealtimeStatusBadge connection={realtime.connection} compact />
            <LiveIndicator connection={realtime.connection} label="Stream" />
          </>
        }
      />

      <RealtimeConnectionBanner connection={realtime.connection} />

      {mockFallbackActive ? (
        <div className="rounded-2xl border border-amber-300/40 bg-amber-400/10 px-4 py-3 text-sm font-semibold text-amber-100">
          Mock fallback mode active. Backend fallback data is being used for offline-safe UI rendering.
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <StatusCard
          title="System Health"
          status={healthStatus.toUpperCase()}
          description="Janie Server health status and runtime availability."
          severity={getSeverityFromStatus(healthStatus)}
        />
        <StatusCard
          title="Backend Connection"
          status={backendConnected ? "CONNECTED" : "SIMULATED"}
          description={
            backendConnected
              ? "Backend API reachable and returning live envelopes."
              : "Using mock-safe fallback or degraded backend connectivity."
          }
          severity={backendConnected ? "success" : "warning"}
        />
        <StatusCard
          title="Agent Status Summary"
          status={`${onlineAgents}/${totalAgents || 9} ONLINE`}
          description="Alexander Prime command chain and coordinated module agents."
          severity={onlineAgents > 0 ? "success" : "warning"}
        />
        <StatusCard
          title={`${AGENT_NAME_BY_ID.trading} Trading Dry-Run`}
          status={tradingDryRun ? "DRY_RUN" : "REAL_MODE"}
          description="XAU scanning and execution controls remain simulation-first by default."
          severity={tradingDryRun ? "success" : "danger"}
        />
        <StatusCard
          title={`${AGENT_NAME_BY_ID.guardian} Risk Status`}
          status={riskLevel.toUpperCase()}
          description="Guardian checks total drawdown, daily drawdown, and execution risk state."
          severity={getSeverityFromStatus(riskLevel)}
        />
        <StatusCard
          title="Kill Switch / Halt"
          status={killSwitchActive ? "KILL SWITCH ACTIVE" : halted ? "HALTED" : "CLEAR"}
          description="Global stop gates for risky operations and automation safety enforcement."
          severity={killSwitchActive || halted ? "danger" : "success"}
        />
        <StatusCard
          title={`${AGENT_NAME_BY_ID.friday} Scheduler`}
          status={schedulerRunning ? "RUNNING" : "IDLE"}
          description={schedulerEnabled ? "Scheduler enabled with default jobs." : "Scheduler disabled."}
          severity={schedulerRunning ? "success" : "warning"}
        />
        <StatusCard
          title={`${AGENT_NAME_BY_ID.joe} Backtest Summary`}
          status={latestBacktest ? latestBacktest.strategy.toUpperCase() : "NO_RESULTS"}
          description={
            latestBacktest
              ? `Latest net: ${formatPercent(latestBacktest.metrics.net_profit_percent)} · primary ${backtestPrimaryStrategy}`
              : `Primary strategy ${backtestPrimaryStrategy} ready for simulation runs.`
          }
          severity={latestBacktest ? "success" : "warning"}
        />
        <StatusCard
          title="Content Pipeline Summary"
          status={socialDryRun ? "SOCIAL_DRY_RUN" : "READY"}
          description={
            contentApprovalRequired
              ? "Approval required before publish actions can proceed."
              : "Approval gate disabled."
          }
          severity={contentApprovalRequired ? "warning" : "success"}
        />
        <StatusCard
          title="IoT Dry-Run Status"
          status={iotDryRun ? "IOT_DRY_RUN" : "REAL_MODE"}
          description={`Device alias: ${iotAlias}. Confirmation remains required for power-cycle flows.`}
          severity={iotDryRun ? "success" : "warning"}
        />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <RealtimeEventFeed
          title="Realtime Activity Feed"
          events={realtime.events}
          emptyMessage="Waiting for live dashboard events."
        />

        <SectionCard title="Recent Session Logs" subtitle="Latest events from system, agents, and module workflows.">
          {latestLogs.length === 0 ? (
            <p className="text-sm text-slate-400">No session logs available.</p>
          ) : (
            <ul className="space-y-2">
              {latestLogs.map((entry) => (
                <li key={entry.id} className="rounded-md border border-slate-800 bg-slate-950/60 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-slate-100">{entry.message}</p>
                    <Badge variant={entry.level === "error" ? "danger" : "muted"}>
                      {readString(entry.category ?? entry.type, "system")}
                    </Badge>
                  </div>
                  <p className="mt-1 text-xs text-slate-400">
                    {entry.source} · {formatDateTime(entry.created_at ?? entry.ts)}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </SectionCard>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <RealtimeEventFeed
          title="Risk Stream"
          events={riskRealtime.events}
          maxItems={4}
          emptyMessage="No live risk alerts."
        />
        <RealtimeEventFeed
          title="Scheduler Stream"
          events={schedulerRealtime.events}
          maxItems={4}
          emptyMessage="No live scheduler activity."
        />
        <RealtimeEventFeed
          title="Content Stream"
          events={contentRealtime.events}
          maxItems={4}
          emptyMessage="No live content pipeline activity."
        />

        <SectionCard title="Runtime Chain" subtitle="Canonical leadership and module ownership map.">
          <p className="text-sm text-slate-300">
            Alexander Prime delegates execution to Sophia Lane, coordinating Victor Hale (Risk), Isla Grant
            (Scheduler + IoT), Nathan Cole (Backtesting), Elena Voss, Julian Reed, Maya Quinn (Content), and Damien
            Cross (Trading).
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {[
              AGENT_NAME_BY_ID.ceo,
              AGENT_NAME_BY_ID.janie,
              AGENT_NAME_BY_ID.guardian,
              AGENT_NAME_BY_ID.friday,
              AGENT_NAME_BY_ID.joe,
              AGENT_NAME_BY_ID.editor,
              AGENT_NAME_BY_ID.graphic,
              AGENT_NAME_BY_ID.social,
              AGENT_NAME_BY_ID.trading,
            ].map((name) => (
              <Badge key={name} variant="normal">
                {name}
              </Badge>
            ))}
          </div>
        </SectionCard>
      </div>

      <TeamRoster />
    </div>
  );
}
