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
import { AGENT_NAME_BY_ID } from "../constants/agents";
import { useApi } from "../hooks/useApi";
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
        title="Scheduler"
        subtitle={`${AGENT_NAME_BY_ID.friday} scheduler management, job safety labels, and run controls.`}
        actions={
          <Badge variant={schedulerRunning ? "success" : "warning"}>
            {schedulerRunning ? "RUNNING" : "IDLE"}
          </Badge>
        }
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Scheduler Enabled" value={schedulerEnabled ? "YES" : "NO"} />
        <MetricCard label="Scheduler Running" value={schedulerRunning ? "YES" : "NO"} />
        <MetricCard label="Configured Jobs" value={jobs.length} />
        <MetricCard label="Run History" value={runs.length} />
      </div>

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">Default Jobs</h3>
        <p className="mt-1 text-xs text-slate-400">Baseline jobs exposed by scheduler and safety policy.</p>
        <div className="mt-3 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
          {defaultJobs.map((job) => (
            <div key={job.id} className="rounded-md border border-slate-800 bg-slate-950/60 p-3">
              <p className="text-sm font-semibold text-slate-100">{job.id}</p>
              <p className="mt-1 text-xs text-slate-400">{job.note}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">Create Job</h3>
        <form className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4" onSubmit={(event) => void onCreateJob(event)}>
          <label className="text-xs text-slate-300">
            Name
            <input
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
              value={newJobName}
              onChange={(event) => setNewJobName(event.target.value)}
            />
          </label>
          <label className="text-xs text-slate-300">
            Job type
            <select
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
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
          <label className="text-xs text-slate-300">
            Schedule
            <select
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
              value={newJobScheduleType}
              onChange={(event) => setNewJobScheduleType(event.target.value)}
            >
              <option value="manual">manual</option>
              <option value="interval">interval</option>
              <option value="cron">cron</option>
            </select>
          </label>
          <label className="text-xs text-slate-300">
            Interval (sec)
            <input
              type="number"
              min={10}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
              value={newJobIntervalSeconds}
              onChange={(event) => setNewJobIntervalSeconds(Number(event.target.value))}
            />
          </label>
          <div className="md:col-span-2 xl:col-span-4">
            <Button type="submit" variant="primary" disabled={creating}>
              {creating ? "Creating..." : "Create job"}
            </Button>
          </div>
        </form>
        {message ? <p className="mt-2 text-sm text-slate-300">{message}</p> : null}
      </section>

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">Job Table</h3>
        <p className="mt-1 text-xs text-slate-400">
          `trading_scan` is risk-guarded, `content_pipeline` is approval/no-auto-publish, `iot_power_cycle` requires confirmation.
        </p>
        <div className="mt-3">
          <DataTable<ScheduledJob>
            rows={jobs}
            loading={loadingJobs}
            error={jobsError}
            rowKey={(row) => row.id}
            emptyMessage="No scheduler jobs found."
            columns={[
              {
                key: "name",
                header: "Job",
                render: (row) => row.name,
              },
              {
                key: "type",
                header: "Type",
                render: (row) => row.job_type,
              },
              {
                key: "status",
                header: "Status",
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
                header: "Safety",
                render: (row) => {
                  if (row.job_type === "trading_scan") {
                    return <Badge variant="warning">Risk-guarded</Badge>;
                  }
                  if (row.job_type === "content_pipeline") {
                    return <Badge variant="warning">Approval / no auto-publish</Badge>;
                  }
                  if (row.job_type === "iot_power_cycle") {
                    return <Badge variant="danger">Confirmation required</Badge>;
                  }
                  return <Badge variant="muted">Standard</Badge>;
                },
              },
              {
                key: "controls",
                header: "Controls",
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
                        Run
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
                        Pause
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
                        Resume
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
                        Delete
                      </Button>
                    </div>
                  );
                },
              },
            ]}
          />
        </div>
      </section>

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">Job Run History</h3>
        <div className="mt-3">
          <DataTable<JobRunResult>
            rows={runs}
            loading={loadingRuns}
            error={runsError}
            rowKey={(row, index) => `${row.job_id}-${row.started_at}-${index}`}
            emptyMessage="No scheduler runs available."
            columns={[
              {
                key: "job",
                header: "Job",
                render: (row) => row.job_id,
              },
              {
                key: "type",
                header: "Type",
                render: (row) => row.job_type,
              },
              {
                key: "status",
                header: "Status",
                render: (row) => row.status,
              },
              {
                key: "started",
                header: "Started",
                render: (row) => formatDateTime(row.started_at),
              },
              {
                key: "duration",
                header: "Duration",
                render: (row) => formatDurationMs(row.duration_ms),
              },
            ]}
          />
        </div>
      </section>
    </div>
  );
}
