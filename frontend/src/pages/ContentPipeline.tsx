import { useEffect, useMemo, useState } from "react";

import {
  approveContent,
  createContent,
  editContent,
  generateGraphic,
  getContentStatus,
  listContentItems,
  publishContent,
  runContentPipeline,
  scheduleContent,
} from "../api/endpoints";
import type { ContentItem } from "../api/types";
import Badge from "../components/common/Badge";
import Button from "../components/common/Button";
import MetricCard from "../components/common/MetricCard";
import PageHeader from "../components/layout/PageHeader";
import LiveIndicator from "../components/realtime/LiveIndicator";
import RealtimeConnectionBanner from "../components/realtime/RealtimeConnectionBanner";
import RealtimeEventFeed from "../components/realtime/RealtimeEventFeed";
import RealtimeStatusBadge from "../components/realtime/RealtimeStatusBadge";
import { AGENT_NAME_BY_ID } from "../constants/agents";
import { useApi } from "../hooks/useApi";
import { useContentRealtime } from "../realtime/useRealtime";
import { canPublishContent } from "../utils/safety";

const boardStatuses = [
  "draft",
  "edited",
  "graphic_ready",
  "scheduled",
  "approved",
  "posted",
  "failed",
  "rejected",
] as const;

export default function ContentPipeline() {
  const realtime = useContentRealtime({ maxEvents: 18 });
  const contentStatus = useApi(getContentStatus, []);
  const itemsState = useApi(listContentItems, []);

  const [items, setItems] = useState<ContentItem[]>([]);
  const [newTitle, setNewTitle] = useState("zDash Educational Simulation");
  const [newTopic, setNewTopic] = useState("Safety-first market operations");
  const [newType, setNewType] = useState("educational");
  const [busyItemId, setBusyItemId] = useState<string | null>(null);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!itemsState.data) {
      return;
    }
    setItems(itemsState.data);
  }, [itemsState.data]);

  const grouped = useMemo(() => {
    const groups: Record<string, ContentItem[]> = {};
    for (const status of boardStatuses) {
      groups[status] = [];
    }
    for (const item of items) {
      if (!groups[item.status]) {
        groups[item.status] = [];
      }
      groups[item.status].push(item);
    }
    return groups;
  }, [items]);

  function updateItemInState(nextItem: ContentItem) {
    setItems((previous) => {
      const without = previous.filter((item) => item.id !== nextItem.id);
      return [nextItem, ...without];
    });
  }

  async function withItemAction(itemId: string, action: () => Promise<ContentItem | void>) {
    setBusyItemId(itemId);
    setMessage(null);
    setError(null);
    try {
      const result = await action();
      if (result) {
        updateItemInState(result);
      }
    } catch (caught) {
      const text = caught instanceof Error ? caught.message : String(caught);
      setError(text);
    } finally {
      setBusyItemId(null);
    }
  }

  async function onCreateContent(event: React.FormEvent) {
    event.preventDefault();
    setMessage(null);
    setError(null);
    try {
      const created = await createContent({
        title: newTitle,
        topic: newTopic,
        content_type: newType,
      });
      updateItemInState(created);
      setMessage(`Content created: ${created.title}`);
    } catch (caught) {
      const text = caught instanceof Error ? caught.message : String(caught);
      setError(text);
    }
  }

  async function onRunPipeline() {
    setPipelineRunning(true);
    setMessage(null);
    setError(null);
    try {
      const run = await runContentPipeline({ dry_run: true });
      setMessage(`Pipeline run completed: ${run.message}`);
      await itemsState.refetch();
    } catch (caught) {
      const text = caught instanceof Error ? caught.message : String(caught);
      setError(text);
    } finally {
      setPipelineRunning(false);
    }
  }

  const approvalRequired = contentStatus.data?.approval_required !== false;
  const socialDryRun = contentStatus.data?.social_dry_run !== false;

  return (
    <div className="space-y-5">
      <PageHeader
        title="Content Pipeline"
        subtitle={`${AGENT_NAME_BY_ID.editor}, ${AGENT_NAME_BY_ID.graphic}, and ${AGENT_NAME_BY_ID.social} workflow control.`}
        actions={
          <>
            <RealtimeStatusBadge connection={realtime.connection} compact />
            <LiveIndicator connection={realtime.connection} label="Content WS" />
            <Badge variant="warning">APPROVAL GATED</Badge>
          </>
        }
      />

      <RealtimeConnectionBanner connection={realtime.connection} />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Pipeline Enabled" value={contentStatus.data?.enabled ? "YES" : "NO"} />
        <MetricCard label="Approval Required" value={approvalRequired ? "YES" : "NO"} />
        <MetricCard label="SOCIAL_DRY_RUN" value={socialDryRun ? "ON" : "OFF"} />
        <MetricCard label="Content Items" value={items.length} />
      </div>

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">Workflow</h3>
        <p className="mt-2 text-sm text-slate-300">
          Elena Voss drafts and edits content, Julian Reed prepares graphics, and Maya Quinn handles scheduling and
          approval-gated dry-run publishing.
        </p>
      </section>

      <form className="rounded-lg border border-slate-800 bg-slate-900/70 p-4" onSubmit={(event) => void onCreateContent(event)}>
        <h3 className="text-sm font-semibold text-white">Create Content</h3>
        <div className="mt-3 grid gap-3 md:grid-cols-3">
          <label className="text-xs text-slate-300">
            Title
            <input
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
              value={newTitle}
              onChange={(event) => setNewTitle(event.target.value)}
            />
          </label>
          <label className="text-xs text-slate-300">
            Topic
            <input
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
              value={newTopic}
              onChange={(event) => setNewTopic(event.target.value)}
            />
          </label>
          <label className="text-xs text-slate-300">
            Type
            <input
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
              value={newType}
              onChange={(event) => setNewType(event.target.value)}
            />
          </label>
        </div>
        <div className="mt-3 flex items-center gap-2">
          <Button type="submit" variant="primary">
            Create content
          </Button>
          <Button variant="secondary" onClick={() => void onRunPipeline()} disabled={pipelineRunning}>
            {pipelineRunning ? "Running pipeline..." : "Run full pipeline"}
          </Button>
        </div>
      </form>

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">Content Board</h3>
        <p className="mt-1 text-xs text-slate-400">
          Grouped by status: draft, edited, graphic_ready, scheduled, approved, posted, failed, rejected.
        </p>

        <div className="mt-4 space-y-4">
          {boardStatuses.map((status) => (
            <div key={status} className="rounded-md border border-slate-800 bg-slate-950/60 p-3">
              <div className="mb-3 flex items-center justify-between gap-2">
                <h4 className="text-sm font-semibold text-slate-100">{status}</h4>
                <Badge variant="muted">{grouped[status]?.length ?? 0}</Badge>
              </div>

              {grouped[status]?.length ? (
                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                  {grouped[status].map((item) => {
                    const busy = busyItemId === item.id;
                    const allowedToPublish = canPublishContent(item);

                    return (
                      <article key={item.id} className="rounded-md border border-slate-800 bg-slate-900/80 p-3">
                        <p className="text-sm font-semibold text-white">{item.title}</p>
                        <p className="mt-1 text-xs text-slate-400">{item.topic}</p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          <Badge variant={item.approval_required ? "warning" : "muted"}>
                            {item.approval_required ? "Approval required" : "Approval optional"}
                          </Badge>
                          <Badge variant={item.social_dry_run !== false ? "success" : "warning"}>
                            {item.social_dry_run !== false ? "SOCIAL_DRY_RUN" : "SOCIAL_REAL_MODE"}
                          </Badge>
                        </div>

                        <div className="mt-3 flex flex-wrap gap-2">
                          <Button
                            className="px-2 py-1 text-xs"
                            disabled={busy}
                            onClick={() =>
                              void withItemAction(item.id, () =>
                                editContent({ content_id: item.id, instructions: "Tighten copy for clarity." }),
                              )
                            }
                          >
                            Edit
                          </Button>
                          <Button
                            className="px-2 py-1 text-xs"
                            disabled={busy}
                            onClick={() =>
                              void withItemAction(item.id, () =>
                                generateGraphic({ content_id: item.id, style: "clean dashboard" }),
                              )
                            }
                          >
                            Generate graphic
                          </Button>
                          <Button
                            className="px-2 py-1 text-xs"
                            disabled={busy}
                            onClick={() =>
                              void withItemAction(item.id, () =>
                                scheduleContent({
                                  content_id: item.id,
                                  scheduled_at: new Date().toISOString(),
                                  platforms: ["x"],
                                }),
                              )
                            }
                          >
                            Schedule
                          </Button>
                          <Button
                            className="px-2 py-1 text-xs"
                            disabled={busy}
                            onClick={() =>
                              void withItemAction(item.id, () =>
                                approveContent({
                                  content_id: item.id,
                                  approved_by: AGENT_NAME_BY_ID.janie,
                                  notes: "Approved for dry-run publish.",
                                }),
                              )
                            }
                          >
                            Approve
                          </Button>
                          <Button
                            className="px-2 py-1 text-xs"
                            variant="secondary"
                            disabled={busy || !allowedToPublish}
                            onClick={() =>
                              void withItemAction(item.id, async () => {
                                const results = await publishContent({
                                  content_id: item.id,
                                  platforms: ["x"],
                                  confirmation: true,
                                });
                                setMessage(results[0]?.message ?? "Dry-run publish simulated.");
                                return { ...item, status: "posted", posted_at: new Date().toISOString() };
                              })
                            }
                          >
                            Dry-run publish
                          </Button>
                        </div>

                        <div className="mt-3">
                          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Policy notes</p>
                          {item.policy_notes?.length ? (
                            <ul className="mt-1 list-disc space-y-1 pl-4 text-xs text-amber-100">
                              {item.policy_notes.map((note) => (
                                <li key={note}>{note}</li>
                              ))}
                            </ul>
                          ) : (
                            <p className="mt-1 text-xs text-slate-400">No policy notes.</p>
                          )}
                          {item.policy_passed === false ? (
                            <p className="mt-1 text-xs font-semibold text-rose-200">Policy failed: action blocked until resolved.</p>
                          ) : null}
                        </div>
                      </article>
                    );
                  })}
                </div>
              ) : (
                <p className="text-xs text-slate-500">No items in this status.</p>
              )}
            </div>
          ))}
        </div>
      </section>

      {message ? <p className="text-sm text-emerald-200">{message}</p> : null}
      {error ? <p className="text-sm text-rose-200">{error}</p> : null}

      <RealtimeEventFeed
        title="Live Content Stream"
        events={realtime.events}
        maxItems={10}
        emptyMessage="No live content websocket events yet."
      />

      <div className="rounded-lg border border-amber-300/40 bg-amber-400/10 px-4 py-3 text-xs text-amber-100">
        Publishing remains approval-required and dry-run by default. Mock publishing does not create real social posts.
      </div>
    </div>
  );
}
