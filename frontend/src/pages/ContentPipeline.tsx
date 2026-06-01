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
import { useT } from "../hooks/useT";
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
  const { t } = useT();
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
        title={t('content.title')}
        subtitle={t('content.subtitle_agents', { editor: AGENT_NAME_BY_ID.editor, graphic: AGENT_NAME_BY_ID.graphic, social: AGENT_NAME_BY_ID.social })}
        actions={
          <>
            <RealtimeStatusBadge connection={realtime.connection} compact />
            <LiveIndicator connection={realtime.connection} label={t('content.content_ws')} />
            <Badge variant="warning">{t('content.approval_gated')}</Badge>
          </>
        }
      />

      <RealtimeConnectionBanner connection={realtime.connection} />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label={t('content.pipeline_enabled')} value={contentStatus.data?.enabled ? "YES" : "NO"} />
        <MetricCard label={t('content.approval_required')} value={approvalRequired ? "YES" : "NO"} />
        <MetricCard label={t('content.social_dry_run')} value={socialDryRun ? "ON" : "OFF"} />
        <MetricCard label={t('content.content_items')} value={items.length} />
      </div>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('content.workflow')}</h3>
        <p className="mt-2 text-sm text-text-secondary">{t('content.workflow_description')}</p>
      </section>

      <form className="rounded-card border border-border bg-panel p-4" onSubmit={(event) => void onCreateContent(event)}>
        <h3 className="text-sm font-semibold text-white">{t('content.create_content')}</h3>
        <div className="mt-3 grid gap-3 md:grid-cols-3">
          <label className="text-xs text-text-secondary">
            {t('content.content_title')}
            <input
              className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
              value={newTitle}
              onChange={(event) => setNewTitle(event.target.value)}
            />
          </label>
          <label className="text-xs text-text-secondary">
            {t('content.content_topic')}
            <input
              className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
              value={newTopic}
              onChange={(event) => setNewTopic(event.target.value)}
            />
          </label>
          <label className="text-xs text-text-secondary">
            {t('content.content_type')}
            <input
              className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
              value={newType}
              onChange={(event) => setNewType(event.target.value)}
            />
          </label>
        </div>
        <div className="mt-3 flex items-center gap-2">
          <Button type="submit" variant="primary">
            {t('content.create_content_btn')}
          </Button>
          <Button variant="secondary" onClick={() => void onRunPipeline()} disabled={pipelineRunning}>
            {pipelineRunning ? t('content.running_pipeline') : t('content.run_full_pipeline')}
          </Button>
        </div>
      </form>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('content.content_board')}</h3>
        <p className="mt-1 text-xs text-text-dim">{t('content.content_board_subtitle')}</p>

        <div className="mt-4 space-y-4">
          {boardStatuses.map((status) => (
            <div key={status} className="rounded-md border border-border bg-canvas-lighter/60 p-3">
              <div className="mb-3 flex items-center justify-between gap-2">
                <h4 className="text-sm font-semibold text-text-primary">{status}</h4>
                <Badge variant="muted">{grouped[status]?.length ?? 0}</Badge>
              </div>

              {grouped[status]?.length ? (
                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                  {grouped[status].map((item) => {
                    const busy = busyItemId === item.id;
                    const allowedToPublish = canPublishContent(item);

                    return (
                      <article key={item.id} className="rounded-md border border-border bg-panel-hover p-3">
                        <p className="text-sm font-semibold text-white">{item.title}</p>
                        <p className="mt-1 text-xs text-text-dim">{item.topic}</p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          <Badge variant={item.approval_required ? "warning" : "muted"}>
                            {item.approval_required ? t('content.approval_required_badge') : t('content.approval_optional')}
                          </Badge>
                          <Badge variant={item.social_dry_run !== false ? "success" : "warning"}>
                            {item.social_dry_run !== false ? t('content.social_dry_run') : t('content.social_real_mode')}
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
                            {t('content.edit')}
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
                            {t('content.generate_graphic')}
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
                            {t('content.schedule')}
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
                            {t('content.approve')}
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
                            {t('content.dry_run_publish')}
                          </Button>
                        </div>

                        <div className="mt-3">
                          <p className="text-xs font-semibold uppercase tracking-wide text-text-dim">{t('content.policy_notes')}</p>
                          {item.policy_notes?.length ? (
                            <ul className="mt-1 list-disc space-y-1 pl-4 text-xs text-state-warning">
                              {item.policy_notes.map((note) => (
                                <li key={note}>{note}</li>
                              ))}
                            </ul>
                          ) : (
                            <p className="mt-1 text-xs text-text-dim">{t('content.no_policy_notes')}</p>
                          )}
                          {item.policy_passed === false ? (
                            <p className="mt-1 text-xs font-semibold text-state-danger">{t('content.policy_failed')}</p>
                          ) : null}
                        </div>
                      </article>
                    );
                  })}
                </div>
              ) : (
                <p className="text-xs text-text-dim">{t('content.no_items_in_status')}</p>
              )}
            </div>
          ))}
        </div>
      </section>

      {message ? <p className="text-sm text-state-success">{message}</p> : null}
      {error ? <p className="text-sm text-state-danger">{error}</p> : null}

      <RealtimeEventFeed
        title={t('content.live_content_stream')}
        events={realtime.events}
        maxItems={10}
        emptyMessage={t('content.no_content_websocket_events')}
      />

      <div className="rounded-card border border-amber-300/40 bg-amber-400/10 px-4 py-3 text-xs text-state-warning">
        {t('content.publishing_disclaimer')}
      </div>
    </div>
  );
}
