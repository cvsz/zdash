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
import { useT } from "../hooks/useT";
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
  const { t } = useT();
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
      setActionMessage(t('risk.halt_set', { reason: state.reason ?? "manual" }));
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
      setActionMessage(t('risk.trading_resumed', { reason: state.resume_reason ?? reason }));
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
        title={t('risk.title')}
        subtitle={t('risk.panel_subtitle', { agent: AGENT_NAME_BY_ID.guardian })}
        actions={
          <>
            <RealtimeStatusBadge connection={realtime.connection} compact />
            <LiveIndicator connection={realtime.connection} label="Risk WS" />
            <Badge variant={emergencyState ? "danger" : "success"}>{emergencyState ? t('risk.emergency') : t('risk.normal')}</Badge>
          </>
        }
      />

      <RealtimeConnectionBanner connection={realtime.connection} />

      {emergencyState ? (
        <div className="rounded-card border border-state-danger/20 bg-state-danger/20 px-4 py-3 text-sm font-semibold text-state-danger">
          {t('risk.emergency_active_message')}
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label={t('risk.guardian_enabled')} value={guardianEnabled ? t('common.yes') : t('common.no')} />
        <MetricCard label={t('risk.kill_switch')} value={killSwitchActive ? t('risk.active') : t('risk.inactive')} severity={killSwitchActive ? "danger" : "success"} />
        <MetricCard label={t('risk.halt_state')} value={halted ? t('risk.halted') : t('risk.running')} severity={halted ? "danger" : "success"} />
        <MetricCard label={t('risk.risk_level')} value={riskLevel.toUpperCase()} severity={emergencyState ? "danger" : "warning"} />
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label={t('risk.total_drawdown')}
          value={formatPercent(totalDrawdown)}
          delta={`${t('risk.threshold_total')} ${formatPercent(thresholds.total)}`}
          severity={totalDrawdown >= thresholds.total ? "danger" : "muted"}
        />
        <MetricCard
          label={t('risk.daily_drawdown')}
          value={formatPercent(dailyDrawdown)}
          delta={`${t('risk.threshold_daily')} ${formatPercent(thresholds.daily)}`}
          severity={dailyDrawdown >= thresholds.daily ? "danger" : "muted"}
        />
        <MetricCard label={t('risk.threshold_total')} value={formatPercent(thresholds.total)} />
        <MetricCard label={t('risk.threshold_daily')} value={formatPercent(thresholds.daily)} />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <section className="rounded-card border border-border bg-panel p-4">
          <h3 className="text-sm font-semibold text-white">{t('risk.manual_halt')}</h3>
          <p className="mt-1 text-xs text-text-dim">{t('risk.manual_halt_subtitle')}</p>
          <input
            className="mt-3 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none ring-cyan-500/60 focus:ring"
            value={haltReason}
            onChange={(event) => setHaltReason(event.target.value)}
            placeholder={t('risk.halt_reason')}
          />
          <div className="mt-3">
            <Button variant="danger" disabled={processing} onClick={() => void onManualHalt()}>
              {processing ? t('risk.applying') : t('risk.manual_halt_btn')}
            </Button>
          </div>
        </section>

        <section className="rounded-card border border-border bg-panel p-4">
          <h3 className="text-sm font-semibold text-white">{t('risk.manual_resume')}</h3>
          <p className="mt-1 text-xs text-text-dim">{t('risk.manual_resume_subtitle')}</p>
          <input
            className="mt-3 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none ring-cyan-500/60 focus:ring"
            value={resumeReason}
            onChange={(event) => setResumeReason(event.target.value)}
            placeholder={t('risk.resume_reason')}
          />
          <div className="mt-3">
            <Button
              variant="primary"
              disabled={processing || resumeReason.trim().length === 0}
              onClick={() => setResumeConfirmOpen(true)}
            >
              {t('risk.resume_trading')}
            </Button>
          </div>
        </section>
      </div>

      {actionMessage ? <p className="text-sm text-state-success">{actionMessage}</p> : null}
      {actionError ? <p className="text-sm text-state-danger">{actionError}</p> : null}

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('risk.risk_event_log')}</h3>
        <p className="mt-1 text-xs text-text-dim">{t('risk.risk_event_log_subtitle')}</p>
        <div className="mt-3">
          <DataTable<EventLog>
            rows={riskEvents}
            loading={logsState.loading}
            error={logsState.error}
            rowKey={(row) => row.id}
            emptyMessage={t('risk.no_risk_events')}
            columns={[
              {
                key: "time",
                header: t('risk.time'),
                render: (row) => formatDateTime(row.created_at ?? row.ts),
              },
              {
                key: "category",
                header: t('risk.category'),
                render: (row) => String(row.category ?? row.type ?? "risk"),
              },
              {
                key: "source",
                header: t('risk.source'),
                render: (row) => row.source,
              },
              {
                key: "message",
                header: t('risk.message'),
                render: (row) => row.message,
              },
            ]}
          />
        </div>
      </section>

      <RealtimeEventFeed
        title={t('risk.live_risk_stream')}
        events={realtime.events}
        maxItems={10}
        emptyMessage={t('risk.no_risk_websocket_events')}
      />

      <ConfirmDialog
        open={resumeConfirmOpen}
        title={t('risk.confirm_resume')}
        message={t('risk.confirm_resume_message')}
        confirmLabel={t('risk.confirm_resume_label')}
        onConfirm={() => void onConfirmResume()}
        onCancel={() => setResumeConfirmOpen(false)}
        isConfirming={processing}
      />
    </div>
  );
}
