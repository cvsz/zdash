import { useCallback, useEffect, useMemo, useState } from "react";

import {
  createJob,
  deleteJob,
  getSchedulerStatus,
  listJobs,
  listRuns,
  pauseJob,
  resumeJob,
  runJob,
} from "../api/endpoints";
import type { JobRunResult, ScheduledJob } from "../api/types";
import Badge from "../components/common/Badge";
import Button from "../components/common/Button";
import DataTable from "../components/common/DataTable";
import MetricCard from "../components/common/MetricCard";
import PageHeader from "../components/layout/PageHeader";
import LiveIndicator from "../components/realtime/LiveIndicator";
import RealtimeConnectionBanner from "../components/realtime/RealtimeConnectionBanner";
import RealtimeEventFeed from "../components/realtime/RealtimeEventFeed";
import RealtimeStatusBadge from "../components/realtime/RealtimeStatusBadge";
import { AGENT_NAME_BY_ID } from "../constants/agents";
import { useApi } from "../hooks/useApi";
import { useSchedulerRealtime } from "../realtime/useRealtime";
import { useT } from "../hooks/useT";
import { formatDateTime, formatDurationMs } from "../utils/format";

const jobTypes = [
  "trading_scan",
  "risk_check",
  "backtest",
  "content_pipeline",
  "health_check",
  "iot_power_cycle",
  "custom",
] as const;

export default function Scheduler() {
  const { t } = useT();
  const realtime = useSchedulerRealtime({ maxEvents: 16 });
  const schedulerStatus = useApi(getSchedulerStatus, []);

  const [jobs, setJobs] = useState<ScheduledJob[]>([]);
  const [runs, setRuns] = useState<JobRunResult[]>([]);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [loadingRuns, setLoadingRuns] = useState(true);
  const [jobsError, setJobsError] = useState<string | null>(null);
  const [runsError, setRunsError] = useState<string | null>(null);
  const [busyJobId, setBusyJobId] = useState<string | null>(null);

  const [newJobName, setNewJobName] = useState("custom");
  const [newJobType, setNewJobType] = useState<(typeof jobTypes)[number]>("custom");
  const [newJobScheduleType, setNewJobScheduleType] = useState("manual");
  const [newJobIntervalSeconds, setNewJobIntervalSeconds] = useState(300);
  const [creating, setCreating] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const loadJobs = useCallback(async () => {
    setLoadingJobs(true);
    setJobsError(null);
    try {
      const response = await listJobs();
      setJobs(response);
    } catch (error) {
      const text = error instanceof Error ? error.message : String(error);
      setJobsError(text);
    } finally {
      setLoadingJobs(false);
    }
  }, []);

  const loadRuns = useCallback(async () => {
    setLoadingRuns(true);
    setRunsError(null);
    try {
      const response = await listRuns();
      setRuns(response);
    } catch (error) {
      const text = error instanceof Error ? error.message : String(error);
      setRunsError(text);
    } finally {
      setLoadingRuns(false);
    }
  }, []);

  useEffect(() => {
    void loadJobs();
    void loadRuns();
  }, [loadJobs, loadRuns]);

  async function withJobAction(jobId: string, action: () => Promise<void>) {
    setBusyJobId(jobId);
    setMessage(null);
    try {
      await action();
      await Promise.all([loadJobs(), loadRuns()]);
    } finally {
      setBusyJobId(null);
    }
  }

  async function onCreateJob(event: React.FormEvent) {
    event.preventDefault();
    setCreating(true);
    setMessage(null);
    try {
      await createJob({
        name: newJobName,
        job_type: newJobType,
        schedule_type: newJobScheduleType,
        interval_seconds: newJobScheduleType === "interval" ? newJobIntervalSeconds : null,
        payload: {
          dry_run: true,
        },
      });
      setMessage(`Job created: ${newJobName}`);
      await loadJobs();
    } catch (error) {
      const text = error instanceof Error ? error.message : String(error);
      setMessage(`Create failed: ${text}`);
    } finally {
      setCreating(false);
    }
  }

  const schedulerRunning = schedulerStatus.data?.running === true;
  const schedulerEnabled = schedulerStatus.data?.enabled !== false;

  const defaultJobs = useMemo(
    () => [
      { id: "trading_scan", note: "Risk-guarded label" },
      { id: "risk_check", note: "Guardian safety polling" },
      { id: "backtest", note: "Strategy lab batch runs" },
      { id: "content_pipeline", note: "Approval required, no auto-publish" },
      { id: "health_check", note: "Service readiness verification" },
      { id: "iot_power_cycle", note: "Confirmation warning" },
    ],
    [],
  );

  return (
    <div className="space-y-5">
      <PageHeader
        title={t('scheduler.title')}
        subtitle={t('scheduler.subtitle')}
        actions={
          <>
            <RealtimeStatusBadge connection={realtime.connection} compact />
            <LiveIndicator connection={realtime.connection} label={t('scheduler.scheduler_ws')} />
            <Badge variant={schedulerRunning ? "success" : "warning"}>
              {schedulerRunning ? t('scheduler.running') : t('scheduler.idle')}
            </Badge>
          </>
        }
      />

      <RealtimeConnectionBanner connection={realtime.connection} />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label={t('scheduler.scheduler_enabled')} value={schedulerEnabled ? "YES" : "NO"} />
        <MetricCard label={t('scheduler.scheduler_running')} value={schedulerRunning ? "YES" : "NO"} />
        <MetricCard label={t('scheduler.configured_jobs')} value={jobs.length} />
        <MetricCard label={t('scheduler.run_history')} value={runs.length} />
      </div>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('scheduler.default_jobs')}</h3>
        <p className="mt-1 text-xs text-text-dim">{t('scheduler.default_jobs_subtitle')}</p>
        <div className="mt-3 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
          {defaultJobs.map((job) => (
            <div key={job.id} className="rounded-md border border-border bg-canvas-lighter/60 p-3">
              <p className="text-sm font-semibold text-text-primary">{job.id}</p>
              <p className="mt-1 text-xs text-text-dim">{job.note}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('scheduler.create_job')}</h3>
        <form className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4" onSubmit={(event) => void onCreateJob(event)}>
          <label className="text-xs text-text-secondary">
            {t('scheduler.name')}
            <input
              className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
              value={newJobName}
              onChange={(event) => setNewJobName(event.target.value)}
            />
          </label>
          <label className="text-xs text-text-secondary">
            {t('scheduler.job_type')}
            <select
              className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
              value={newJobType}
              onChange={(event) => setNewJobType(event.target.value as (typeof jobTypes)[number])}
            >
              {jobTypes.map((jobType) => (
                <option key={jobType} value={jobType}>
                  {jobType}
                </option>
              ))}
            </select>
          </label>
          <label className="text-xs text-text-secondary">
            {t('scheduler.schedule')}
            <select
              className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
              value={newJobScheduleType}
              onChange={(event) => setNewJobScheduleType(event.target.value)}
            >
              <option value="manual">manual</option>
              <option value="interval">interval</option>
              <option value="cron">cron</option>
            </select>
          </label>
          <label className="text-xs text-text-secondary">
            {t('scheduler.interval_seconds')}
            <input
              type="number"
              min={10}
              className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
              value={newJobIntervalSeconds}
              onChange={(event) => setNewJobIntervalSeconds(Number(event.target.value))}
            />
          </label>
          <div className="md:col-span-2 xl:col-span-4">
            <Button type="submit" variant="primary" disabled={creating}>
              {creating ? t('scheduler.creating') : t('scheduler.create')}
            </Button>
          </div>
        </form>
        {message ? <p className="mt-2 text-sm text-text-secondary">{message}</p> : null}
      </section>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('scheduler.job_table')}</h3>
        <p className="mt-1 text-xs text-text-dim">{t('scheduler.job_table_subtitle')}</p>
        <div className="mt-3">
          <DataTable<ScheduledJob>
            rows={jobs}
            loading={loadingJobs}
            error={jobsError}
            rowKey={(row) => row.id}
            emptyMessage={t('scheduler.no_jobs_found')}
            columns={[
              {
                key: "name",
                header: t('scheduler.job'),
                render: (row) => row.name,
              },
              {
                key: "type",
                header: t('scheduler.type'),
                render: (row) => row.job_type,
              },
              {
                key: "status",
                header: t('scheduler.status'),
                render: (row) => (
                  <Badge
                    variant={
                      row.status === "completed"
                        ? "success"
                        : row.status === "failed"
                          ? "danger"
                          : row.status === "paused"
                            ? "warning"
                            : "muted"
                    }
                  >
                    {row.status.toUpperCase()}
                  </Badge>
                ),
              },
              {
                key: "safety",
                header: t('scheduler.safety'),
                render: (row) => {
                  if (row.job_type === "trading_scan") {
                    return <Badge variant="warning">{t('scheduler.risk_guarded')}</Badge>;
                  }
                  if (row.job_type === "content_pipeline") {
                    return <Badge variant="warning">{t('scheduler.approval_no_auto_publish')}</Badge>;
                  }
                  if (row.job_type === "iot_power_cycle") {
                    return <Badge variant="danger">{t('scheduler.confirmation_required')}</Badge>;
                  }
                  return <Badge variant="muted">{t('scheduler.standard')}</Badge>;
                },
              },
              {
                key: "controls",
                header: t('scheduler.controls'),
                render: (row) => {
                  const busy = busyJobId === row.id;
                  return (
                    <div className="flex flex-wrap gap-2">
                      <Button
                        className="px-2 py-1 text-xs"
                        disabled={busy}
                        onClick={() =>
                          void withJobAction(row.id, async () => {
                            const result = await runJob(row.id);
                            setRuns((previous) => [result, ...previous]);
                          })
                        }
                      >
                        {t('common.run')}
                      </Button>
                      <Button
                        className="px-2 py-1 text-xs"
                        variant="secondary"
                        disabled={busy}
                        onClick={() =>
                          void withJobAction(row.id, async () => {
                            await pauseJob(row.id);
                          })
                        }
                      >
                        {t('common.pause')}
                      </Button>
                      <Button
                        className="px-2 py-1 text-xs"
                        variant="secondary"
                        disabled={busy}
                        onClick={() =>
                          void withJobAction(row.id, async () => {
                            await resumeJob(row.id);
                          })
                        }
                      >
                        {t('common.resume')}
                      </Button>
                      <Button
                        className="px-2 py-1 text-xs"
                        variant="danger"
                        disabled={busy}
                        onClick={() =>
                          void withJobAction(row.id, async () => {
                            await deleteJob(row.id);
                          })
                        }
                      >
                        {t('common.delete')}
                      </Button>
                    </div>
                  );
                },
              },
            ]}
          />
        </div>
      </section>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('scheduler.job_run_history')}</h3>
        <div className="mt-3">
          <DataTable<JobRunResult>
            rows={runs}
            loading={loadingRuns}
            error={runsError}
            rowKey={(row, index) => `${row.job_id}-${row.started_at}-${index}`}
            emptyMessage={t('scheduler.no_scheduler_runs')}
            columns={[
              {
                key: "job",
                header: t('scheduler.job'),
                render: (row) => row.job_id,
              },
              {
                key: "type",
                header: t('scheduler.type'),
                render: (row) => row.job_type,
              },
              {
                key: "status",
                header: t('scheduler.status'),
                render: (row) => row.status,
              },
              {
                key: "started",
                header: t('scheduler.started'),
                render: (row) => formatDateTime(row.started_at),
              },
              {
                key: "duration",
                header: t('scheduler.duration'),
                render: (row) => formatDurationMs(row.duration_ms),
              },
            ]}
          />
        </div>
      </section>

      <RealtimeEventFeed
        title={t('scheduler.live_scheduler_stream')}
        events={realtime.events}
        maxItems={10}
        emptyMessage={t('scheduler.no_scheduler_websocket_events')}
      />
    </div>
  );
}
