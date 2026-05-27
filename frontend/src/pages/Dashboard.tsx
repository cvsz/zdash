import { mockFallbackActive } from "../api/client";
import StatusCard from "../components/common/StatusCard";
import PageHeader from "../components/layout/PageHeader";
import { useSystemStatus } from "../hooks/useSystemStatus";
import { getSeverityFromStatus } from "../utils/status";
import TeamRoster from "./TeamRoster";

export default function Dashboard() {
  const { data } = useSystemStatus();
  const healthStatus = String(data?.health?.status ?? "loading");
  const riskStatus = String((data?.risk?.risk_level as string | undefined) ?? "loading");
  const schedulerRunning = Boolean(data?.scheduler?.running);
  const contentEnabled = data?.content?.enabled === true;

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Live session overview with safety-first defaults."
      />

      {mockFallbackActive && (
        <div className="mx-auto mb-4 max-w-7xl rounded-2xl border border-amber-300/40 bg-amber-400/10 px-4 py-3 text-sm font-semibold text-amber-100">
          Mock fallback mode active. Values below are simulated for offline-safe UI rendering.
        </div>
      )}

      <div className="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatusCard
          title="Janie Server"
          status={healthStatus.toUpperCase()}
          description="Backend and runtime availability."
          severity={getSeverityFromStatus(healthStatus)}
        />
        <StatusCard
          title="Guardian Risk"
          status={riskStatus.toUpperCase()}
          description="Kill switch and halt guard status."
          severity={getSeverityFromStatus(riskStatus)}
        />
        <StatusCard
          title="Scheduler"
          status={schedulerRunning ? "RUNNING" : "IDLE"}
          description="Automation loop and job dispatch engine."
          severity={schedulerRunning ? "success" : "warning"}
        />
        <StatusCard
          title="Content Pipeline"
          status={contentEnabled ? "ENABLED" : "DISABLED"}
          description="Approval-gated publishing workflow."
          severity={contentEnabled ? "success" : "warning"}
        />
      </div>

      <TeamRoster />
    </div>
  );
}
