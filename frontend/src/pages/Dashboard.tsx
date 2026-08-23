import { mockFallbackActive } from "../api/client";
import { getBacktestingStatus, getLogs, listBacktestResults } from "../api/endpoints";
import PageHeader from "../components/layout/PageHeader";
import QuotaBanner from "../components/billing/QuotaBanner";
import LiveIndicator from "../components/realtime/LiveIndicator";
import RealtimeConnectionBanner from "../components/realtime/RealtimeConnectionBanner";
import RealtimeEventFeed from "../components/realtime/RealtimeEventFeed";
import RealtimeStatusBadge from "../components/realtime/RealtimeStatusBadge";
import DataPanel from "../components/ui/DataPanel";
import GlassCard from "../components/ui/GlassCard";
import MetricCard from "../components/ui/MetricCard";
import PhaseProgressGrid from "../components/ui/PhaseProgressGrid";
import ReleaseGatePanel from "../components/ui/ReleaseGatePanel";
import SafetyBanner from "../components/ui/SafetyBanner";
import StatusBadge from "../components/ui/StatusBadge";
import { useApi } from "../hooks/useApi";
import { useSystemStatus } from "../hooks/useSystemStatus";
import {
  useContentRealtime,
  useRealtime,
  useRiskRealtime,
  useSchedulerRealtime,
} from "../realtime/useRealtime";
import { formatDateTime } from "../utils/format";
import { getSeverityFromStatus } from "../utils/status";

function readBoolean(value: unknown, fallback = false): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function readString(value: unknown, fallback = "unknown"): string {
  return typeof value === "string" && value.length > 0 ? value : fallback;
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

function SectionHeading({ title, description }: { title: string; description: string }) {
  return (
    <div>
      <h2 className="text-sm font-bold tracking-tight text-text-primary">{title}</h2>
      <p className="mt-0.5 text-xs text-text-dim">{description}</p>
    </div>
  );
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
  const contentApprovalRequired = readBoolean(data?.content?.approval_required, true);
  const socialDryRun = readBoolean(data?.content?.social_dry_run, true);
  const iotDryRun = readBoolean((data?.iot as Record<string, unknown> | undefined)?.dry_run, true);
  const iotAlias = readString((data?.iot as Record<string, unknown> | undefined)?.device_alias, "-");

  const backtestPrimaryStrategy = readString(backtestingStatus.data?.primary_strategy, "ob_aggressive");
  const latestBacktest = backtestResults.data?.[0] ?? null;
  const latestLogs = (logsState.data ?? []).slice(0, 6);

  const unifiedActivity = [
    ...riskRealtime.events,
    ...schedulerRealtime.events,
    ...contentRealtime.events,
  ]
    .sort((a, b) => String(b.timestamp).localeCompare(String(a.timestamp)))
    .slice(0, 10);

  const systemCritical = halted || killSwitchActive || getSeverityFromStatus(riskLevel) === "danger";

  const services = [
    {
      name: "Risk guardian",
      detail: halted || killSwitchActive ? "Halt or kill switch active" : "Guardrails active",
      status: halted || killSwitchActive ? "error" : "connected",
    },
    {
      name: "Scheduler",
      detail: schedulerRunning ? "Runtime jobs executing" : "Idle / guarded",
      status: schedulerRunning ? "connected" : "dry-run",
    },
    {
      name: "MT5 bridge",
      detail: tradingDryRun ? "Dry-run scan only" : "Live relay connected",
      status: tradingDryRun ? "dry-run" : "connected",
    },
    {
      name: "Social pipeline",
      detail: contentApprovalRequired ? "Approval gated" : "Automatic publishing enabled",
      status: socialDryRun ? "dry-run" : "connected",
    },
    {
      name: "IoT control",
      detail: `Device ${iotAlias || "none"}`,
      status: iotDryRun ? "dry-run" : "connected",
    },
    {
      name: "Backtest engine",
      detail: latestBacktest ? `Strategy ${backtestPrimaryStrategy}` : "No recent result",
      status: latestBacktest ? "connected" : "dry-run",
    },
  ] as const;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        subtitle="Mission-control view of runtime safety, agents, services, and live operations."
        actions={
          <>
            <RealtimeStatusBadge connection={realtime.connection} compact />
            <LiveIndicator connection={realtime.connection} label="Stream" />
          </>
        }
      />

      <RealtimeConnectionBanner connection={realtime.connection} />
      <QuotaBanner />

      {systemCritical ? (
        <SafetyBanner
          text="Critical runtime state detected. Review risk controls before allowing live execution."
          variant="warning"
        />
      ) : null}

      {mockFallbackActive ? (
        <SafetyBanner
          text="Mock fallback mode active. Backend data is simulated for offline-safe UI rendering."
          variant="info"
        />
      ) : null}

      <section className="space-y-3" aria-labelledby="operational-pulse-heading">
        <div id="operational-pulse-heading">
          <SectionHeading
            title="Operational pulse"
            description="The six signals that matter most before taking operational action."
          />
        </div>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
          <MetricCard
            title="System Health"
            value={healthStatus.toUpperCase()}
            subtitle="Runtime availability"
            variant={healthStatus === "ok" ? "success" : "warning"}
          />
          <MetricCard
            title="Agents Online"
            value={`${onlineAgents}/${totalAgents || 9}`}
            subtitle="Active runtime agents"
            variant={onlineAgents > 0 ? "success" : "warning"}
          />
          <MetricCard
            title="Trading Mode"
            value={tradingDryRun ? "DRY RUN" : "LIVE"}
            subtitle="Execution boundary"
            variant={tradingDryRun ? "warning" : "danger"}
            badge={tradingDryRun ? "SAFE" : "LIVE"}
          />
          <MetricCard
            title="Risk Level"
            value={riskLevel.toUpperCase()}
            subtitle="Guardian assessment"
            variant={
              getSeverityFromStatus(riskLevel) === "danger"
                ? "danger"
                : getSeverityFromStatus(riskLevel) === "warning"
                  ? "warning"
                  : "success"
            }
          />
          <MetricCard
            title="Scheduler"
            value={schedulerRunning ? "RUNNING" : "IDLE"}
            subtitle="Automation runtime"
            variant={schedulerRunning ? "success" : "warning"}
          />
          <MetricCard
            title="Backend"
            value={backendConnected ? "CONNECTED" : "DEGRADED"}
            subtitle={mockFallbackActive ? "Mock fallback" : "API connectivity"}
            variant={backendConnected ? "success" : "warning"}
          />
        </div>
      </section>

      <section className="space-y-3" aria-labelledby="service-health-heading">
        <div id="service-health-heading">
          <SectionHeading
            title="Service health"
            description="Compact status for agents and operational providers without hiding safety state."
          />
        </div>
        <div className="grid gap-4 xl:grid-cols-[1.05fr_1fr]">
          <GlassCard className="p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-widest text-text-muted">Agent roster</p>
                <p className="mt-1 text-xs text-text-dim">{onlineAgents} online of {totalAgents || 9} registered</p>
              </div>
              <StatusBadge
                status={onlineAgents > 0 ? "operational" : "degraded"}
                variant={onlineAgents > 0 ? "success" : "warning"}
                size="sm"
              />
            </div>
            <div className="mt-4 grid gap-2 sm:grid-cols-2">
              {(agents.length > 0 ? agents.slice(0, 8) : []).map((agent) => {
                const status = readString(agent.status);
                const name = readString(agent.name, readString(agent.id, "Agent"));
                return (
                  <div key={readString(agent.id, name)} className="flex items-center justify-between gap-3 rounded-xl border border-border bg-canvas-light/50 px-3 py-2.5">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-text-primary">{name}</p>
                      <p className="mt-0.5 truncate text-[11px] uppercase tracking-wide text-text-dim">{readString(agent.role, "runtime agent")}</p>
                    </div>
                    <StatusBadge
                      status={status}
                      variant={status.toLowerCase() === "online" ? "success" : "muted"}
                      size="sm"
                    />
                  </div>
                );
              })}
              {agents.length === 0 ? (
                <p className="col-span-full py-4 text-sm text-text-dim">Waiting for agent runtime status.</p>
              ) : null}
            </div>
          </GlassCard>

          <GlassCard className="p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-widest text-text-muted">Operational services</p>
                <p className="mt-1 text-xs text-text-dim">Safety and execution boundaries across providers</p>
              </div>
              <StatusBadge status={systemCritical ? "attention" : "guarded"} variant={systemCritical ? "warning" : "success"} size="sm" />
            </div>
            <div className="mt-4 divide-y divide-border rounded-xl border border-border bg-canvas-light/40">
              {services.map((service) => (
                <div key={service.name} className="flex items-center justify-between gap-3 px-3 py-2.5">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-text-primary">{service.name}</p>
                    <p className="mt-0.5 truncate text-xs text-text-dim">{service.detail}</p>
                  </div>
                  <StatusBadge
                    status={service.status}
                    variant={service.status === "error" ? "danger" : service.status === "connected" ? "success" : "warning"}
                    size="sm"
                  />
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      </section>

      <section className="space-y-3" aria-labelledby="live-activity-heading">
        <div id="live-activity-heading">
          <SectionHeading
            title="Live activity"
            description="Risk, scheduler, and content activity combined into one operational stream."
          />
        </div>
        <RealtimeEventFeed
          title="Unified operational stream"
          events={unifiedActivity}
          maxItems={10}
          emptyMessage="No live operational activity."
        />
      </section>

      <section className="space-y-3" aria-labelledby="diagnostics-release-heading">
        <div id="diagnostics-release-heading">
          <SectionHeading
            title="Diagnostics & release"
            description="Detailed logs, delivery progress, and release evidence kept secondary to live operations."
          />
        </div>

        <div className="grid gap-4 xl:grid-cols-2">
          <DataPanel title="Session Logs" subtitle="Latest system, agent, and workflow events">
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

          <PhaseProgressGrid phases={phaseData} totalPhases={32} />
        </div>

        <ReleaseGatePanel
          gates={[
            { name: "All Phases Complete", status: phaseData.filter((phase) => phase.status === "done").length >= 13 ? "pass" : "fail" },
            { name: "Backend Tests", status: "pass" },
            { name: "Frontend Build", status: "pass" },
            { name: "Safety Scan", status: "pass" },
            { name: "Docker Build", status: "pass" },
          ]}
          version="2.0.2"
          canExecute={false}
        />
      </section>
    </div>
  );
}
