import { Link } from "react-router-dom";

import { getMarketingDashboard, type DataSource, type StageStatus } from "../api/marketing";
import Badge from "../components/common/Badge";
import MetricCard from "../components/common/MetricCard";
import PageHeader from "../components/layout/PageHeader";
import { useApi } from "../hooks/useApi";

function sourceBadge(source: DataSource) {
  return source === "live" ? (
    <Badge variant="success">live</Badge>
  ) : (
    <Badge variant="warning">sample</Badge>
  );
}

function statusVariant(status: StageStatus): "success" | "warning" | "muted" {
  if (status === "ready") return "success";
  if (status === "attention") return "warning";
  return "muted";
}

function EmptyState({ children }: { children: string }) {
  return <p className="rounded-md border border-dashed border-border p-4 text-sm text-text-dim">{children}</p>;
}

export default function MarketingDashboard() {
  const dashboard = useApi(getMarketingDashboard, []);
  const data = dashboard.data;

  return (
    <div className="space-y-5">
      <PageHeader
        title="Marketing Intelligence"
        subtitle="Governed content operations from source signals to approved distribution."
        actions={
          <>
            <Link
              to="/content"
              className="rounded-md border border-border bg-panel px-3 py-2 text-sm font-semibold text-text-primary transition hover:bg-panel-hover"
            >
              Open Content Pipeline
            </Link>
            <Link
              to="/scheduler"
              className="rounded-md bg-accent-cyan px-3 py-2 text-sm font-semibold text-canvas transition hover:opacity-90"
            >
              Open Scheduler
            </Link>
          </>
        }
      />

      {dashboard.loading ? (
        <div className="rounded-card border border-border bg-panel p-6 text-sm text-text-secondary">
          Loading marketing operations snapshot…
        </div>
      ) : null}

      {dashboard.error ? (
        <div className="rounded-card border border-state-danger/40 bg-state-danger/10 p-4 text-sm text-state-danger">
          {dashboard.error}
        </div>
      ) : null}

      {data ? (
        <>
          <section className="rounded-card border border-amber-300/40 bg-amber-400/10 px-4 py-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm font-semibold text-state-warning">Data provenance</p>
              <Badge variant={data.source_mode.includes("offline") ? "warning" : "muted"}>
                {data.source_mode}
              </Badge>
            </div>
            <p className="mt-1 text-xs leading-5 text-text-secondary">{data.disclaimer}</p>
          </section>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {data.metrics.map((metric) => (
              <div key={metric.key} className="relative">
                <MetricCard label={metric.label} value={metric.value} hint={metric.detail} />
                <div className="absolute right-3 top-3">{sourceBadge(metric.source)}</div>
              </div>
            ))}
          </div>

          <section className="rounded-card border border-border bg-panel p-4">
            <div className="flex flex-wrap items-end justify-between gap-2">
              <div>
                <h2 className="text-base font-semibold text-white">System map</h2>
                <p className="mt-1 text-xs text-text-dim">Follow the operational path and resolve attention points before publishing.</p>
              </div>
              <p className="text-xs text-text-dim">Generated {new Date(data.generated_at).toLocaleString()}</p>
            </div>

            <div className="mt-4 grid gap-3 lg:grid-cols-3">
              {data.system_map.map((stage, index) => {
                const body = (
                  <article className="h-full rounded-md border border-border bg-canvas-lighter/60 p-4 transition hover:border-accent-cyan/40">
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-xs font-semibold uppercase tracking-wide text-text-dim">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      <Badge variant={statusVariant(stage.status)}>{stage.status}</Badge>
                    </div>
                    <h3 className="mt-3 text-sm font-semibold text-text-primary">{stage.label}</h3>
                    <p className="mt-1 text-xs leading-5 text-text-secondary">{stage.description}</p>
                  </article>
                );
                return stage.route ? (
                  <Link key={stage.key} to={stage.route} className="block">
                    {body}
                  </Link>
                ) : (
                  <div key={stage.key}>{body}</div>
                );
              })}
            </div>
          </section>

          <div className="grid gap-5 xl:grid-cols-2">
            <section className="rounded-card border border-border bg-panel p-4">
              <div className="flex items-center justify-between gap-2">
                <div>
                  <h2 className="text-base font-semibold text-white">Hook vault</h2>
                  <p className="mt-1 text-xs text-text-dim">Reusable openings with explicit evidence status.</p>
                </div>
                <Link to="/content" className="text-xs font-semibold text-accent-cyan hover:underline">Create content</Link>
              </div>
              <div className="mt-4 space-y-3">
                {data.hooks.length ? data.hooks.map((hook) => (
                  <article key={hook.id} className="rounded-md border border-border bg-canvas-lighter/60 p-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant="muted">{hook.category}</Badge>
                      {sourceBadge(hook.source)}
                      <span className="text-xs text-text-dim">used {hook.usage_count} times</span>
                    </div>
                    <p className="mt-3 text-sm font-medium leading-6 text-text-primary">{hook.hook}</p>
                    <p className="mt-2 text-xs text-text-dim">{hook.performance_note}</p>
                  </article>
                )) : <EmptyState>No hooks are available.</EmptyState>}
              </div>
            </section>

            <section className="rounded-card border border-border bg-panel p-4">
              <h2 className="text-base font-semibold text-white">Competitor intelligence</h2>
              <p className="mt-1 text-xs text-text-dim">Opportunity framing only; connect verified sources before operational use.</p>
              <div className="mt-4 space-y-3">
                {data.competitors.length ? data.competitors.map((competitor) => (
                  <article key={competitor.id} className="rounded-md border border-border bg-canvas-lighter/60 p-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div>
                        <p className="text-sm font-semibold text-text-primary">{competitor.name}</p>
                        <p className="text-xs text-text-dim">{competitor.platform}</p>
                      </div>
                      {sourceBadge(competitor.source)}
                    </div>
                    <p className="mt-3 text-xs text-text-secondary"><span className="font-semibold text-text-primary">Momentum:</span> {competitor.momentum}</p>
                    <p className="mt-2 text-xs leading-5 text-text-secondary"><span className="font-semibold text-text-primary">Opportunity:</span> {competitor.opportunity}</p>
                  </article>
                )) : <EmptyState>Connect a competitor source to populate this module.</EmptyState>}
              </div>
            </section>
          </div>

          <div className="grid gap-5 xl:grid-cols-3">
            <section className="rounded-card border border-border bg-panel p-4 xl:col-span-2">
              <h2 className="text-base font-semibold text-white">Trend opportunities</h2>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                {data.trends.length ? data.trends.map((trend) => (
                  <article key={trend.id} className="rounded-md border border-border bg-canvas-lighter/60 p-3">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-semibold text-text-primary">{trend.topic}</p>
                      {sourceBadge(trend.source)}
                    </div>
                    <p className="mt-2 text-xs text-text-dim">{trend.signal}</p>
                    <p className="mt-3 text-xs leading-5 text-text-secondary">{trend.recommended_angle}</p>
                  </article>
                )) : <EmptyState>Connect trend providers to discover current opportunities.</EmptyState>}
              </div>
            </section>

            <section className="rounded-card border border-border bg-panel p-4">
              <div className="flex items-center justify-between gap-2">
                <h2 className="text-base font-semibold text-white">Calendar</h2>
                <Link to="/scheduler" className="text-xs font-semibold text-accent-cyan hover:underline">Manage</Link>
              </div>
              <div className="mt-4 space-y-3">
                {data.schedule.length ? data.schedule.map((item) => (
                  <article key={item.id} className="rounded-md border border-border bg-canvas-lighter/60 p-3">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-semibold text-text-primary">{item.title}</p>
                      {sourceBadge(item.source)}
                    </div>
                    <p className="mt-2 text-xs text-text-secondary">{item.platform}</p>
                    <p className="mt-1 text-xs text-text-dim">{item.scheduled_for}</p>
                  </article>
                )) : <EmptyState>No content is currently scheduled.</EmptyState>}
              </div>
            </section>
          </div>

          <section className="rounded-card border border-border bg-panel p-4">
            <h2 className="text-base font-semibold text-white">Campaign recommendations</h2>
            <p className="mt-1 text-xs text-text-dim">Budget and campaign mutations remain approval-gated.</p>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {data.campaign_recommendations.map((recommendation) => (
                <article key={recommendation.id} className="rounded-md border border-border bg-canvas-lighter/60 p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-text-primary">{recommendation.campaign}</p>
                    <div className="flex gap-2">
                      {sourceBadge(recommendation.source)}
                      {recommendation.approval_required ? <Badge variant="warning">approval required</Badge> : null}
                    </div>
                  </div>
                  <p className="mt-3 text-sm font-medium text-accent-cyan">{recommendation.recommendation}</p>
                  <p className="mt-2 text-xs leading-5 text-text-secondary">{recommendation.rationale}</p>
                </article>
              ))}
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
