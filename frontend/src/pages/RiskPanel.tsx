import { useMemo, useState } from "react";

import { getDrawdown, getLogs, getRiskStatus, haltRisk, resumeRisk } from "../api/endpoints";
import type { EventLog } from "../api/types";
import Badge from "../components/common/Badge";
import Button from "../components/common/Button";
import ConfirmDialog from "../components/common/ConfirmDialog";
import DataTable from "../components/common/DataTable";
import MetricCard from "../components/common/MetricCard";
import PageHeader from "../components/layout/PageHeader";
import LiveIndicator from "../components/realtime/LiveIndicator";
import RealtimeConnectionBanner from "../components/realtime/RealtimeConnectionBanner";
import RealtimeEventFeed from "../components/realtime/RealtimeEventFeed";
import RealtimeStatusBadge from "../components/realtime/RealtimeStatusBadge";
import { AGENT_NAME_BY_ID } from "../constants/agents";
import { useApi } from "../hooks/useApi";
import { useRiskRealtime } from "../realtime/useRealtime";
import { formatDateTime, formatPercent } from "../utils/format";

function readBoolean(value: unknown, fallback = false): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function readString(value: unknown, fallback = "unknown"): string {
  return typeof value === "string" && value.length > 0 ? value : fallback;
}

function readNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

export default function RiskPanel() {
  const realtime = useRiskRealtime({ maxEvents: 14 });
  const riskStatus = useApi(getRiskStatus, []);
  const drawdownState = useApi(getDrawdown, []);
  const logsState = useApi(getLogs, []);

  const [haltReason, setHaltReason] = useState("");
  const [resumeReason, setResumeReason] = useState("");
  const [resumeConfirmOpen, setResumeConfirmOpen] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  const riskLevel = readString(riskStatus.data?.risk_level, "unknown");
  const haltState = riskStatus.data?.halt_state as Record<string, unknown> | undefined;
  const halted = readBoolean(haltState?.halted, false);
  const killSwitchActive = readBoolean(riskStatus.data?.kill_switch_active, false);
  const guardianEnabled = readBoolean(riskStatus.data?.guardian_enabled, false);

  const totalDrawdown = readNumber(drawdownState.data?.total_drawdown_percent, 0);
  const dailyDrawdown = readNumber(drawdownState.data?.daily_drawdown_percent, 0);

  const thresholds = {
    total: readNumber((riskStatus.data?.thresholds as Record<string, unknown> | undefined)?.total_drawdown_percent, 10),
    daily: readNumber((riskStatus.data?.thresholds as Record<string, unknown> | undefined)?.daily_drawdown_percent, 5),
  };

  const emergencyState =
    killSwitchActive ||
    halted ||
    riskLevel.toLowerCase() === "danger" ||
    riskLevel.toLowerCase() === "emergency";

  const riskEvents = useMemo(() => {
    const source = logsState.data ?? [];
    return source
      .filter((entry) => {
        const category = String(entry.category ?? "").toLowerCase();
        const type = String(entry.type ?? "").toLowerCase();
        const origin = String(entry.source ?? "").toLowerCase();
        return (
          category.includes("risk") ||
          category.includes("guardian") ||
          type.includes("risk") ||
          type.includes("guardian") ||
          origin.includes("risk") ||
          origin.includes("guardian")
        );
      })
      .slice(0, 10);
  }, [logsState.data]);

  async function onManualHalt() {
    setProcessing(true);
    setActionError(null);
    setActionMessage(null);

    try {
      const reason = haltReason.trim() || "Manual halt requested from Risk Panel.";
      const state = await haltRisk(reason);
      setActionMessage(`Halt set: ${state.reason ?? "manual"}`);
      setHaltReason("");
      await Promise.all([riskStatus.refetch(), drawdownState.refetch(), logsState.refetch()]);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setActionError(message);
    } finally {
      setProcessing(false);
    }
  }

  async function onConfirmResume() {
    setProcessing(true);
    setActionError(null);
    setActionMessage(null);

    try {
      const reason = resumeReason.trim();
      const state = await resumeRisk(reason, true);
      setActionMessage(`Trading resumed: ${state.resume_reason ?? reason}`);
      setResumeReason("");
      setResumeConfirmOpen(false);
      await Promise.all([riskStatus.refetch(), drawdownState.refetch(), logsState.refetch()]);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setActionError(message);
    } finally {
      setProcessing(false);
    }
  }

  return (
    <div className="space-y-5">
      <PageHeader
        title="Risk Panel"
        subtitle={`${AGENT_NAME_BY_ID.guardian} Guardian risk oversight, halt controls, and drawdown monitoring.`}
        actions={
          <>
            <RealtimeStatusBadge connection={realtime.connection} compact />
            <LiveIndicator connection={realtime.connection} label="Risk WS" />
            <Badge variant={emergencyState ? "danger" : "success"}>{emergencyState ? "EMERGENCY" : "NORMAL"}</Badge>
          </>
        }
      />

      <RealtimeConnectionBanner connection={realtime.connection} />

      {emergencyState ? (
        <div className="rounded-lg border border-rose-500/60 bg-rose-500/20 px-4 py-3 text-sm font-semibold text-rose-100">
          Emergency state active. Kill switch or halt protection is engaged.
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Guardian Enabled" value={guardianEnabled ? "YES" : "NO"} />
        <MetricCard label="Kill Switch" value={killSwitchActive ? "ACTIVE" : "INACTIVE"} severity={killSwitchActive ? "danger" : "success"} />
        <MetricCard label="Halt State" value={halted ? "HALTED" : "RUNNING"} severity={halted ? "danger" : "success"} />
        <MetricCard label="Risk Level" value={riskLevel.toUpperCase()} severity={emergencyState ? "danger" : "warning"} />
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Total Drawdown"
          value={formatPercent(totalDrawdown)}
          delta={`Threshold ${formatPercent(thresholds.total)}`}
          severity={totalDrawdown >= thresholds.total ? "danger" : "muted"}
        />
        <MetricCard
          label="Daily Drawdown"
          value={formatPercent(dailyDrawdown)}
          delta={`Threshold ${formatPercent(thresholds.daily)}`}
          severity={dailyDrawdown >= thresholds.daily ? "danger" : "muted"}
        />
        <MetricCard label="Threshold - Total" value={formatPercent(thresholds.total)} />
        <MetricCard label="Threshold - Daily" value={formatPercent(thresholds.daily)} />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
          <h3 className="text-sm font-semibold text-white">Manual Halt</h3>
          <p className="mt-1 text-xs text-slate-400">Immediately halt execution paths using Guardian controls.</p>
          <input
            className="mt-3 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-cyan-500/60 focus:ring"
            value={haltReason}
            onChange={(event) => setHaltReason(event.target.value)}
            placeholder="Halt reason"
          />
          <div className="mt-3">
            <Button variant="danger" disabled={processing} onClick={() => void onManualHalt()}>
              {processing ? "Applying..." : "Manual halt"}
            </Button>
          </div>
        </section>

        <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
          <h3 className="text-sm font-semibold text-white">Manual Resume</h3>
          <p className="mt-1 text-xs text-slate-400">Resume requires explicit reason and confirmation dialog.</p>
          <input
            className="mt-3 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-cyan-500/60 focus:ring"
            value={resumeReason}
            onChange={(event) => setResumeReason(event.target.value)}
            placeholder="Resume reason"
          />
          <div className="mt-3">
            <Button
              variant="primary"
              disabled={processing || resumeReason.trim().length === 0}
              onClick={() => setResumeConfirmOpen(true)}
            >
              Resume trading
            </Button>
          </div>
        </section>
      </div>

      {actionMessage ? <p className="text-sm text-emerald-200">{actionMessage}</p> : null}
      {actionError ? <p className="text-sm text-rose-200">{actionError}</p> : null}

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">Risk Event Log (Subset)</h3>
        <p className="mt-1 text-xs text-slate-400">Recent events related to risk, Guardian, halt, and kill-switch state.</p>
        <div className="mt-3">
          <DataTable<EventLog>
            rows={riskEvents}
            loading={logsState.loading}
            error={logsState.error}
            rowKey={(row) => row.id}
            emptyMessage="No risk events available."
            columns={[
              {
                key: "time",
                header: "Time",
                render: (row) => formatDateTime(row.created_at ?? row.ts),
              },
              {
                key: "category",
                header: "Category",
                render: (row) => String(row.category ?? row.type ?? "risk"),
              },
              {
                key: "source",
                header: "Source",
                render: (row) => row.source,
              },
              {
                key: "message",
                header: "Message",
                render: (row) => row.message,
              },
            ]}
          />
        </div>
      </section>

      <RealtimeEventFeed
        title="Live Risk Stream"
        events={realtime.events}
        maxItems={10}
        emptyMessage="No live risk websocket events yet."
      />

      <ConfirmDialog
        open={resumeConfirmOpen}
        title="Confirm manual resume"
        message="Resume is guarded and will be audited. Confirm to continue with the provided reason."
        confirmLabel="Confirm resume"
        onConfirm={() => void onConfirmResume()}
        onCancel={() => setResumeConfirmOpen(false)}
        isConfirming={processing}
      />
    </div>
  );
}
