import { useEffect, useMemo, useState } from "react";

import type { EventLog } from "../api/types";
import Badge from "../components/common/Badge";
import Button from "../components/common/Button";
import DataTable from "../components/common/DataTable";
import PageHeader from "../components/layout/PageHeader";
import { useLogs } from "../hooks/useLogs";
import { usePolling } from "../hooks/usePolling";
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
        title="Session Logs"
        subtitle="Event logs with category/source/type filters, payload inspection, and auto-refresh control."
        actions={<Badge variant={autoRefresh ? "success" : "muted"}>{autoRefresh ? "AUTO REFRESH ON" : "AUTO REFRESH OFF"}</Badge>}
      />

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">Filters</h3>
        <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <label className="text-xs text-slate-300">
            Category
            <select
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
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

          <label className="text-xs text-slate-300">
            Event type
            <select
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
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

          <label className="text-xs text-slate-300">
            Source
            <select
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
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

          <label className="text-xs text-slate-300">
            Search
            <input
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
              value={logsState.filters.searchTerm}
              onChange={(event) => logsState.setSearchTerm(event.target.value)}
              placeholder="Search logs"
            />
          </label>
        </div>

        <div className="mt-3 flex items-center gap-2">
          <Button
            variant="secondary"
            onClick={() => setAutoRefresh((value) => !value)}
          >
            {autoRefresh ? "Disable auto-refresh" : "Enable auto-refresh"}
          </Button>
          <Button variant="ghost" onClick={() => poller.runNow()}>
            Refresh now
          </Button>
        </div>
      </section>

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">Event Logs Table</h3>
        <div className="mt-3">
          <DataTable<EventLog>
            rows={filteredLogs}
            loading={logsState.loading}
            error={logsState.error}
            rowKey={(row) => row.id}
            emptyMessage="No logs match current filters."
            columns={[
              {
                key: "time",
                header: "Time",
                render: (row) => formatDateTime(row.created_at ?? row.ts),
              },
              {
                key: "category",
                header: "Category",
                render: (row) => String(row.category ?? row.type ?? "system"),
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
              {
                key: "json",
                header: "Payload",
                render: (row) => (
                  <Button className="px-2 py-1 text-xs" onClick={() => setSelectedLog(row)}>
                    View JSON
                  </Button>
                ),
              },
            ]}
          />
        </div>
      </section>

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">JSON Payload Viewer</h3>
        <pre className="mt-3 overflow-x-auto rounded-md border border-slate-800 bg-slate-950/70 p-3 text-xs text-slate-200">
          {selectedLog?.payload ? JSON.stringify(selectedLog.payload, null, 2) : "No payload selected."}
        </pre>
      </section>

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">Recent Errors</h3>
        {recentErrors.length === 0 ? (
          <p className="mt-2 text-sm text-slate-400">No recent errors in current filter set.</p>
        ) : (
          <ul className="mt-3 space-y-2">
            {recentErrors.map((entry) => (
              <li key={`error-${entry.id}`} className="rounded-md border border-rose-500/40 bg-rose-500/10 p-3">
                <p className="text-sm font-semibold text-rose-100">{entry.message}</p>
                <p className="mt-1 text-xs text-rose-200">
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
