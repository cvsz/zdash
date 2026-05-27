import { type FormEvent, useMemo, useState } from "react";

import AgentsPagination from "../components/AgentsPagination";
import Button from "../components/common/Button";
import Badge from "../components/common/Badge";
import { CANONICAL_AGENTS, type AgentTier } from "../constants/agents";
import { useAgents } from "../hooks/useAgents";
import { useAgentsPagination } from "../hooks/useAgentsPagination";

const tierStyle: Record<AgentTier, string> = {
  Legendary: "border-amber-300/60 bg-amber-400/10 text-amber-100",
  Epic: "border-cyan-300/50 bg-cyan-400/10 text-cyan-100",
  Rare: "border-emerald-300/50 bg-emerald-400/10 text-emerald-100",
};

const tierAccent: Record<AgentTier, string> = {
  Legendary: "A",
  Epic: "E",
  Rare: "R",
};

export default function TeamRoster() {
  const [message, setMessage] = useState("");
  const [messageResult, setMessageResult] = useState<string | null>(null);
  const [messageError, setMessageError] = useState<string | null>(null);
  const [messageSending, setMessageSending] = useState(false);

  const agentsState = useAgents();
  const liveAgentsById = useMemo(() => {
    const map = new Map<string, { status: string; lastEvent?: string; health?: string }>();
    for (const agent of agentsState.data ?? []) {
      map.set(agent.id, {
        status: agent.status,
        lastEvent: agent.last_event,
        health: agent.health,
      });
    }
    return map;
  }, [agentsState.data]);

  const {
    agentsPerPage,
    currentPage,
    totalItems,
    totalPages,
    pageItems,
    pageStart,
    pageEnd,
    setAgentsPerPage,
    goToPage,
  } = useAgentsPagination(CANONICAL_AGENTS);

  const tierCounts = useMemo(() => {
    return CANONICAL_AGENTS.reduce(
      (counts, agent) => {
        counts[agent.tier] += 1;
        return counts;
      },
      { Legendary: 0, Epic: 0, Rare: 0 } as Record<AgentTier, number>,
    );
  }, []);

  async function onSendMessage(event: FormEvent) {
    event.preventDefault();
    setMessageError(null);
    setMessageResult(null);

    const trimmedMessage = message.trim();
    if (!trimmedMessage) {
      setMessageError("Message is required.");
      return;
    }

    setMessageSending(true);
    try {
      const response = await agentsState.sendMessage({
        from_agent: "ceo",
        to_agent: "janie",
        message: trimmedMessage,
        context: { source: "team_roster" },
      });
      const responseText =
        typeof response.response_text === "string"
          ? response.response_text
          : "Message delivered in simulation mode.";
      setMessageResult(responseText);
      setMessage("");
    } catch (error) {
      const messageText = error instanceof Error ? error.message : String(error);
      setMessageError(messageText);
    } finally {
      setMessageSending(false);
    }
  }

  return (
    <section className="mx-auto flex w-full max-w-[112rem] flex-col gap-6 px-1 py-2 text-slate-100 sm:px-2 lg:px-4">
      <div className="rounded-3xl border border-slate-700/70 bg-slate-950/60 p-6 shadow-2xl shadow-slate-950/30 backdrop-blur">
        <p className="text-xs font-bold uppercase tracking-[0.32em] text-cyan-300">zDash Command Roster</p>
        <div className="mt-3 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-3xl font-black tracking-tight text-white md:text-4xl">Team Roster</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
              Alexander Prime delegates execution to Sophia Lane. Sophia Lane coordinates Victor Hale, Isla Grant,
              Nathan Cole, Elena Voss, Julian Reed, Maya Quinn, and Damien Cross.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-2 text-center text-xs font-bold uppercase tracking-[0.16em] text-slate-300">
            <span className="rounded-2xl border border-amber-300/40 bg-amber-400/10 px-3 py-2">
              {tierCounts.Legendary} Legendary
            </span>
            <span className="rounded-2xl border border-cyan-300/40 bg-cyan-400/10 px-3 py-2">
              {tierCounts.Epic} Epic
            </span>
            <span className="rounded-2xl border border-emerald-300/40 bg-emerald-400/10 px-3 py-2">
              {tierCounts.Rare} Rare
            </span>
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <form
          className="rounded-2xl border border-slate-800 bg-slate-900/75 p-4"
          onSubmit={(event) => {
            void onSendMessage(event);
          }}
        >
          <h2 className="text-sm font-semibold text-white">Alexander Prime -&gt; Sophia Lane Message Panel</h2>
          <p className="mt-1 text-xs text-slate-400">Stable routing IDs preserved: ceo -&gt; janie.</p>
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            className="mt-3 min-h-[90px] w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-cyan-500/60 focus:ring"
            placeholder="Send execution guidance to Sophia Lane..."
          />
          <div className="mt-3 flex items-center gap-2">
            <Button type="submit" variant="primary" disabled={messageSending}>
              {messageSending ? "Sending..." : "Send message"}
            </Button>
            {messageResult ? <Badge variant="success">Delivered</Badge> : null}
            {messageError ? <Badge variant="danger">Failed</Badge> : null}
          </div>
          {messageResult ? <p className="mt-2 text-sm text-emerald-200">{messageResult}</p> : null}
          {messageError ? <p className="mt-2 text-sm text-rose-200">{messageError}</p> : null}
        </form>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/75 p-4">
          <h2 className="text-sm font-semibold text-white">Roster Health Snapshot</h2>
          <p className="mt-1 text-xs text-slate-400">Live agent statuses from backend APIs with mock-safe fallback.</p>
          <div className="mt-3 grid gap-2 sm:grid-cols-2">
            {CANONICAL_AGENTS.map((agent) => {
              const live = liveAgentsById.get(agent.id);
              const status = live?.status ?? "unknown";
              const statusVariant =
                status === "online"
                  ? "success"
                  : status === "offline"
                    ? "danger"
                    : status === "degraded"
                      ? "warning"
                      : "muted";
              return (
                <div key={`${agent.id}-health`} className="rounded-md border border-slate-800 bg-slate-950/70 p-2">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-xs font-semibold text-slate-200">{agent.name}</p>
                    <Badge variant={statusVariant}>{status.toUpperCase()}</Badge>
                  </div>
                  <p className="mt-1 text-[11px] text-slate-400">{live?.lastEvent ?? "No recent event."}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <AgentsPagination
        pageStart={pageStart}
        pageEnd={pageEnd}
        totalItems={totalItems}
        totalPages={totalPages}
        currentPage={currentPage}
        agentsPerPage={agentsPerPage}
        onPageSizeChange={setAgentsPerPage}
        onPageChange={goToPage}
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-5">
        {pageItems.map((agent) => {
          const live = liveAgentsById.get(agent.id);
          const status = live?.status ?? "unknown";
          const statusVariant =
            status === "online"
              ? "success"
              : status === "offline"
                ? "danger"
                : status === "degraded"
                  ? "warning"
                  : "muted";

          return (
            <article
              key={agent.id}
              className="rounded-3xl border border-slate-700/70 bg-slate-950/55 p-4 shadow-xl shadow-slate-950/25 transition hover:-translate-y-1 hover:border-cyan-300/60"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <span
                    className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-700 bg-slate-900 text-sm font-black text-cyan-200"
                    aria-hidden="true"
                  >
                    {tierAccent[agent.tier]}
                  </span>
                  <h2 className="mt-3 text-xl font-black text-white">{agent.name}</h2>
                  <p className="mt-1 text-sm font-semibold text-cyan-200">{agent.title}</p>
                </div>
                <span
                  className={`rounded-full border px-2.5 py-1 text-[0.65rem] font-bold uppercase tracking-[0.14em] ${tierStyle[agent.tier]}`}
                >
                  {agent.tier}
                </span>
              </div>

              <div className="mt-5 rounded-2xl border border-slate-800 bg-slate-950/70 p-3">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-400">Stable Agent ID</p>
                <p className="mt-2 text-sm text-slate-100">{agent.id}</p>
              </div>

              <div className="mt-3 rounded-2xl border border-slate-800 bg-slate-950/70 p-3">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-400">Primary Role</p>
                <p className="mt-2 text-sm text-slate-200">{agent.role}</p>
              </div>

              <p className="mt-4 text-sm leading-6 text-slate-300">{agent.summary}</p>

              <div className="mt-4 flex items-center justify-between gap-2">
                <Badge variant={statusVariant}>{status.toUpperCase()}</Badge>
                <span className="text-xs text-slate-400">{live?.health ?? "status: unknown"}</span>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
