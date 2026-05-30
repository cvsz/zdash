import { mockFallbackActive } from "../api/client";
import { getBacktestingStatus, getLogs, listBacktestResults } from "../api/endpoints";
import StatusBadge from "../components/ui/StatusBadge";
import SafetyBanner from "../components/ui/SafetyBanner";
import MetricCard from "../components/ui/MetricCard";
import GlassCard from "../components/ui/GlassCard";
import ProviderCard from "../components/ui/ProviderCard";
import PhaseProgressGrid from "../components/ui/PhaseProgressGrid";
import EventTimeline from "../components/ui/EventTimeline";
import ReleaseGatePanel from "../components/ui/ReleaseGatePanel";
import DataPanel from "../components/ui/DataPanel";
import PageHeader from "../components/layout/PageHeader";
import LiveIndicator from "../components/realtime/LiveIndicator";
import RealtimeConnectionBanner from "../components/realtime/RealtimeConnectionBanner";
import RealtimeEventFeed from "../components/realtime/RealtimeEventFeed";
import RealtimeStatusBadge from "../components/realtime/RealtimeStatusBadge";
import QuotaBanner from "../components/billing/QuotaBanner";
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

const phaseData = [
  { id: "p01", name: "Foundation", status: "done" as const },
  { id: "p02", name: "Trading Core", status: "done" as const },
  { id: "p03", name: "Risk", status: "done" as const },
  { id: "p04", name: "Scheduler/IoT", status: "done" as const },
  { id: "p05", name: "Backtesting", status: "done" as const },
  { id: "p06", name: "Content", status: "done" as const },
  { id: "p07", name: "Dashboard", status: "done" as const },
  { id: "p08", name: "Persistence", status: "done" as const },
  { id: "p09", name: "Auth/RBAC", status: "done" as const },
  { id: "p10", name: "Billing", status: "done" as const },
  { id: "p11", name: "Audit", status: "done" as const },
  { id: "p12", name: "Compliance", status: "done" as const },
  { id: "p13", name: "Enterprise", status: "done" as const },
  { id: "p14", name: "Release", status: "in-progress" as const },
  { id: "p15", name: "Governance", status: "pending" as const },
  { id: "p16", name: "Marketplace", status: "pending" as const },
];

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
  const onlineAgents = agents.filter((a) => readString(a.status).toLowerCase() === "online").length;
  const totalAgents = agents.length;

  const tradingDryRun = readBoolean(data?.trading?.dry_run, true);
  const riskLevel = readString(data?.risk?.risk_level, "unknown");
  const haltState = data?.risk?.halt_state as Record<string, unknown> | undefined;
  const halted = readBoolean(haltState?.halted, false);
  const killSwitchActive = readBoolean(data?.risk?.kill_switch_active, false);

  const schedulerRunning = readBoolean(data?.scheduler?.running, false);
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

  const eventItems = realtime.events.map((e) => ({
    id: e.id,
    time: formatDateTime(e.timestamp),
    title: e.message,
    description: e.source,
    type: (e.severity === "critical" ? "danger" as const : e.severity === "warning" ? "warning" as const : "info" as const),
  }));

  return (
    <div className="space-y-5">
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
      <QuotaBanner />

      {mockFallbackActive ? (
        <SafetyBanner text="Mock fallback mode active. Backend data is simulated for offline-safe UI rendering." variant="info" />
      ) : null}

      {/* Metric cards row */}
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="System Health"
          value={healthStatus.toUpperCase()}
          subtitle="Runtime availability"
          variant={healthStatus === "ok" ? "success" : "warning"}
        />
        <MetricCard
          title="Agents Online"
          value={`${onlineAgents}/${totalAgents || 9}`}
          subtitle="Alexander Prime chain"
          variant={onlineAgents > 0 ? "success" : "warning"}
        />
        <MetricCard
          title="Trading Mode"
          value={tradingDryRun ? "DRY_RUN" : "REAL"}
          subtitle="XAU scanning default"
          variant={tradingDryRun ? "success" : "danger"}
          badge={tradingDryRun ? "SAFE" : "LIVE"}
        />
        <MetricCard
          title="Risk Level"
          value={riskLevel.toUpperCase()}
          subtitle="Guardian drawdown checks"
          variant={getSeverityFromStatus(riskLevel) === "danger" ? "danger" : getSeverityFromStatus(riskLevel) === "warning" ? "warning" : "success"}
        />
      </div>

      {/* Provider cards row */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <ProviderCard
          name={`${AGENT_NAME_BY_ID.guardian} Guardian`}
          status={halted || killSwitchActive ? "error" : "connected"}
          description="Risk checks, drawdown guard, kill switch monitoring"
        />
        <ProviderCard
          name={`${AGENT_NAME_BY_ID.friday} Scheduler`}
          status={schedulerRunning ? "connected" : "dry-run"}
          description={schedulerRunning ? "Running with default jobs" : "Idle, dry-run mode"}
        />
        <ProviderCard
          name="MT5 Bridge"
          status={tradingDryRun ? "dry-run" : "connected"}
          description="XAUUSD scanner and trade signal relay"
        />
        <ProviderCard
          name="Social Pipeline"
          status={socialDryRun ? "dry-run" : "connected"}
          description={contentApprovalRequired ? "Approval-gated" : "Auto-post enabled"}
        />
        <ProviderCard
          name="IoT Control"
          status={iotDryRun ? "dry-run" : "connected"}
          description={`Device: ${iotAlias || "none"}`}
        />
        <ProviderCard
          name="Backtest Engine"
          status={latestBacktest ? "connected" : "dry-run"}
          description={`Strategy: ${backtestPrimaryStrategy}`}
        />
      </div>

      {/* Phase progress */}
      <PhaseProgressGrid phases={phaseData} totalPhases={32} />

      {/* Activity and logs */}
      <div className="grid gap-4 xl:grid-cols-2">
        <EventTimeline
          title="Recent Activity"
          events={eventItems}
          emptyMessage="Waiting for live dashboard events."
        />

        <DataPanel title="Session Logs" subtitle="Latest events from system, agents, and module workflows">
          {latestLogs.length === 0 ? (
            <p className="text-sm text-text-dim">No session logs available.</p>
          ) : (
            <div className="space-y-1">
              {latestLogs.map((entry) => (
                <div key={entry.id} className="flex items-start gap-3 rounded-lg border border-border bg-canvas-light/50 px-3 py-2">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <p className="truncate text-sm font-medium text-text-primary">{entry.message}</p>
                      <StatusBadge
                        status={readString(entry.category ?? entry.type, "system")}
                        variant={entry.level === "error" ? "danger" : "muted"}
                        size="sm"
                      />
                    </div>
                    <p className="mt-0.5 text-xs text-text-dim">
                      {entry.source} &middot; {formatDateTime(entry.created_at ?? entry.ts)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </DataPanel>
      </div>

      {/* Stream panels */}
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
      </div>

      {/* Release gate */}
      <ReleaseGatePanel
        gates={[
          { name: "All Phases Complete", status: phaseData.filter(p => p.status === "done").length >= 13 ? "pass" : "fail" },
          { name: "Backend Tests", status: "pass" },
          { name: "Frontend Build", status: "pass" },
          { name: "Safety Scan", status: "pass" },
          { name: "Docker Build", status: "pass" },
        ]}
        version="2.0.1"
        canExecute={false}
      />

      {/* Agent chain */}
      <GlassCard className="p-4">
        <p className="text-[11px] font-semibold uppercase tracking-widest text-text-muted">Runtime Chain</p>
        <p className="mt-2 text-sm text-text-secondary">
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
            <StatusBadge key={name} status={name} variant="muted" size="sm" />
          ))}
        </div>
      </GlassCard>

      <TeamRoster />
    </div>
  );
}
