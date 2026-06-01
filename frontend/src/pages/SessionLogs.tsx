import { useEffect, useMemo, useState } from "react";

import type { EventLog } from "../api/types";
import Badge from "../components/common/Badge";
import Button from "../components/common/Button";
import DataTable from "../components/common/DataTable";
import PageHeader from "../components/layout/PageHeader";
import RealtimeConnectionBanner from "../components/realtime/RealtimeConnectionBanner";
import RealtimeEventFeed from "../components/realtime/RealtimeEventFeed";
import RealtimeStatusBadge from "../components/realtime/RealtimeStatusBadge";
import { useLogs } from "../hooks/useLogs";
import { usePolling } from "../hooks/usePolling";
import { useRealtime } from "../realtime/useRealtime";
import { useT } from "../hooks/useT";
import { formatDateTime } from "../utils/format";

const categories = ["all", "system", "agent", "trading", "risk", "scheduler", "iot", "backtest", "content"];

function matchesCategory(log: EventLog, category: string): boolean {
  if (category === "all") {
    return true;
  }

  const text = `${log.category ?? ""} ${log.type ?? ""} ${log.source}`.toLowerCase();
  return text.includes(category);
}

export default function SessionLogs() {
  const { t } = useT();
  const realtime = useRealtime({ maxEvents: 24 });
  const logsState = useLogs();
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [selectedLog, setSelectedLog] = useState<EventLog | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const pollIntervalMs = Number(import.meta.env.VITE_POLL_INTERVAL_MS ?? 5000);
  const poller = usePolling(() => {
    void logsState.refetch();
  }, pollIntervalMs);

  useEffect(() => {
    if (autoRefresh) {
      poller.resume();
    } else {
      poller.pause();
    }
  }, [autoRefresh, poller]);

  const filteredLogs = useMemo(
    () => logsState.logs.filter((entry) => matchesCategory(entry, categoryFilter)),
    [logsState.logs, categoryFilter],
  );

  useEffect(() => {
    if (!selectedLog && filteredLogs.length > 0) {
      setSelectedLog(filteredLogs[0]);
    }
    if (selectedLog && !filteredLogs.find((entry) => entry.id === selectedLog.id)) {
      setSelectedLog(filteredLogs[0] ?? null);
    }
  }, [filteredLogs, selectedLog]);

  const typeOptions = useMemo(() => {
    const values = new Set<string>(["all"]);
    for (const entry of logsState.data ?? []) {
      values.add(String(entry.type ?? entry.category ?? "unknown"));
    }
    return Array.from(values);
  }, [logsState.data]);

  const sourceOptions = useMemo(() => {
    const values = new Set<string>(["all"]);
    for (const entry of logsState.data ?? []) {
      values.add(String(entry.source));
    }
    return Array.from(values);
  }, [logsState.data]);

  const recentErrors = useMemo(() => {
    return filteredLogs
      .filter((entry) => {
        const level = String(entry.level ?? "").toLowerCase();
        const message = entry.message.toLowerCase();
        return level === "error" || message.includes("error") || message.includes("failed") || message.includes("rejected");
      })
      .slice(0, 5);
  }, [filteredLogs]);

  return (
    <div className="space-y-5">
      <PageHeader
        title={t('session_logs.title')}
        subtitle={t('session_logs.subtitle')}
        actions={
          <>
            <RealtimeStatusBadge connection={realtime.connection} compact />
            <Badge variant={autoRefresh ? "success" : "muted"}>{autoRefresh ? t('session_logs.auto_refresh_on') : t('session_logs.auto_refresh_off')}</Badge>
          </>
        }
      />

      <RealtimeConnectionBanner connection={realtime.connection} />

      <RealtimeEventFeed
        title={t('session_logs.live_websocket_feed')}
        events={realtime.events}
        maxItems={10}
        emptyMessage={t('session_logs.no_websocket_activity')}
      />

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('session_logs.filters')}</h3>
        <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <label className="text-xs text-text-secondary">
            {t('session_logs.category')}
            <select
              className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
              value={categoryFilter}
              onChange={(event) => setCategoryFilter(event.target.value)}
            >
              {categories.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </label>

          <label className="text-xs text-text-secondary">
            {t('session_logs.event_type')}
            <select
              className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
              value={logsState.filters.typeFilter}
              onChange={(event) => logsState.setTypeFilter(event.target.value)}
            >
              {typeOptions.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </label>

          <label className="text-xs text-text-secondary">
            {t('session_logs.log_source')}
            <select
              className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
              value={logsState.filters.sourceFilter}
              onChange={(event) => logsState.setSourceFilter(event.target.value)}
            >
              {sourceOptions.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </label>

          <label className="text-xs text-text-secondary">
            {t('session_logs.search')}
            <input
              className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
              value={logsState.filters.searchTerm}
              onChange={(event) => logsState.setSearchTerm(event.target.value)}
              placeholder={t('session_logs.search_logs')}
            />
          </label>
        </div>

        <div className="mt-3 flex items-center gap-2">
          <Button
            variant="secondary"
            onClick={() => setAutoRefresh((value) => !value)}
          >
            {autoRefresh ? t('session_logs.disable_auto_refresh') : t('session_logs.enable_auto_refresh')}
          </Button>
          <Button variant="ghost" onClick={() => poller.runNow()}>
            {t('session_logs.refresh_now')}
          </Button>
        </div>
      </section>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('session_logs.event_logs_table')}</h3>
        <div className="mt-3">
          <DataTable<EventLog>
            rows={filteredLogs}
            loading={logsState.loading}
            error={logsState.error}
            rowKey={(row) => row.id}
            emptyMessage={t('session_logs.no_logs_match')}
            columns={[
              {
                key: "time",
                header: t('session_logs.time'),
                render: (row) => formatDateTime(row.created_at ?? row.ts),
              },
              {
                key: "category",
                header: t('session_logs.category'),
                render: (row) => String(row.category ?? row.type ?? "system"),
              },
              {
                key: "source",
                header: t('session_logs.source'),
                render: (row) => row.source,
              },
              {
                key: "message",
                header: t('session_logs.message'),
                render: (row) => row.message,
              },
              {
                key: "json",
                header: t('session_logs.payload'),
                render: (row) => (
                  <Button className="px-2 py-1 text-xs" onClick={() => setSelectedLog(row)}>
                    {t('session_logs.view_json')}
                  </Button>
                ),
              },
            ]}
          />
        </div>
      </section>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('session_logs.json_payload_viewer')}</h3>
        <pre className="mt-3 overflow-x-auto rounded-md border border-border bg-canvas/80 p-3 text-xs text-text-secondary">
          {selectedLog?.payload ? JSON.stringify(selectedLog.payload, null, 2) : t('session_logs.no_payload_selected')}
        </pre>
      </section>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('session_logs.recent_errors')}</h3>
        {recentErrors.length === 0 ? (
          <p className="mt-2 text-sm text-text-dim">{t('session_logs.no_recent_errors')}</p>
        ) : (
          <ul className="mt-3 space-y-2">
            {recentErrors.map((entry) => (
              <li key={`error-${entry.id}`} className="rounded-md border border-state-danger/20 bg-state-danger/10 p-3">
                <p className="text-sm font-semibold text-state-danger">{entry.message}</p>
                <p className="mt-1 text-xs text-state-danger">
                  {String(entry.category ?? entry.type ?? "system")} · {entry.source}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
