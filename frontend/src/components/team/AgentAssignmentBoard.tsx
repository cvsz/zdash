import { useMemo, useState } from "react";
import Badge from "../common/Badge";
import { CANONICAL_AGENTS } from "../../constants/agents";
import { useAgents } from "../../hooks/useAgents";
import { useAgentsPagination } from "../../hooks/useAgentsPagination";
import AgentsPagination from "../AgentsPagination";
import type { TeamMember, TeamAgentAssignment } from "../../api/types";

interface AgentAssignmentBoardProps {
  assignments: TeamAgentAssignment[];
  members: TeamMember[];
  onAssign: (agentId: string, memberId: string | null, role: string) => void;
  onUnassign: (assignmentId: string) => void;
}

const ASSIGNMENT_ROLES = ["owner", "reviewer", "runner", "observer"];

export default function AgentAssignmentBoard({
  assignments,
  members,
  onAssign,
  onUnassign,
}: AgentAssignmentBoardProps) {
  const agentsState = useAgents();
  const [assignAgentId, setAssignAgentId] = useState<string | null>(null);
  const [assignMemberId, setAssignMemberId] = useState<string>("");
  const [assignRole, setAssignRole] = useState<string>("observer");
  const [actionError, setActionError] = useState<string | null>(null);

  const liveAgentsById = useMemo(() => {
    const map = new Map<string, { status: string; lastEvent?: string; health?: string }>();
    const agentData = agentsState.data ?? [];
    if (Array.isArray(agentData)) {
      for (const agent of agentData) {
        map.set(agent.id, {
          status: agent.status,
          lastEvent: agent.last_event,
          health: agent.health,
        });
      }
    }
    return map;
  }, [agentsState.data]);

  const assignmentByAgentId = useMemo(() => {
    const map = new Map<string, TeamAgentAssignment>();
    if (Array.isArray(assignments)) {
      for (const a of assignments) {
        map.set(a.agent_id, a);
      }
    }
    return map;
  }, [assignments]);

  const {
    currentPage,
    totalItems,
    totalPages,
    pageItems,
    pageStart,
    pageEnd,
    agentsPerPage,
    setAgentsPerPage,
    goToPage,
  } = useAgentsPagination(CANONICAL_AGENTS);

  const activeMembers = useMemo(() => {
    if (!Array.isArray(members)) return [];
    return members.filter((m) => m.status === "active");
  }, [members]);

  function handleStartAssign(agentId: string) {
    setAssignAgentId(agentId);
    setAssignMemberId("");
    setAssignRole("observer");
    setActionError(null);
  }

  function handleCancelAssign() {
    setAssignAgentId(null);
    setActionError(null);
  }

  function handleConfirmAssign() {
    if (!assignAgentId) return;
    if (!assignMemberId && assignMemberId !== "") {
      setActionError("Please select a member.");
      return;
    }
    try {
      onAssign(assignAgentId, assignMemberId || null, assignRole);
      setAssignAgentId(null);
    } catch {
      setActionError("Failed to assign agent.");
    }
  }

  function handleUnassign(assignmentId: string) {
    setActionError(null);
    try {
      onUnassign(assignmentId);
    } catch {
      setActionError("Failed to unassign agent.");
    }
  }

  return (
    <div>
      {actionError ? (
        <div className="mb-4 rounded-md border border-rose-500/40 bg-rose-500/10 px-4 py-2 text-sm text-rose-200">
          {actionError}
        </div>
      ) : null}

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

      <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-5">
        {Array.isArray(pageItems) && pageItems.map((agent) => {
          const live = liveAgentsById.get(agent.id);
          const status = live?.status ?? "unknown";
          const statusVariant =
            status === "online" ? "success"
            : status === "offline" ? "danger"
            : status === "degraded" ? "warning"
            : "muted";
          const assignment = assignmentByAgentId.get(agent.id);
          const assignedMember = assignment
            ? (Array.isArray(members) ? members.find((m) => m.id === assignment.member_id) : undefined)
            : undefined;

          return (
            <article
              key={agent.id}
              className="rounded-3xl border border-border/70 bg-canvas/55 p-4 shadow-xl shadow-canvas/25 transition hover:-translate-y-1 hover:border-cyan-300/60"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-xl font-black text-text-primary">{agent.name}</h2>
                  <p className="mt-1 text-sm font-semibold text-accent-cyan">{agent.title}</p>
                </div>
                <Badge variant={statusVariant}>{status.toUpperCase()}</Badge>
              </div>

              <div className="mt-3 rounded-2xl border border-border bg-canvas/80 p-3">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-text-dim">Role</p>
                <p className="mt-1 text-sm text-text-secondary">{agent.role}</p>
              </div>

              <div className="mt-3 rounded-2xl border border-border bg-canvas/80 p-3">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-text-dim">Assignment</p>
                {assignment ? (
                  <div className="mt-1 flex items-center gap-2">
                    <span className="text-sm text-text-primary">
                      {assignedMember?.display_name ?? "Unnamed"}
                    </span>
                    <Badge variant="normal">{assignment.assignment_role}</Badge>
                  </div>
                ) : (
                  <p className="mt-1 text-sm text-text-dim">Unassigned</p>
                )}
              </div>

              <p className="mt-3 text-xs leading-5 text-text-dim">{agent.summary}</p>

              <div className="mt-4 flex items-center gap-2">
                {assignAgentId === agent.id ? (
                  <div className="flex w-full flex-col gap-2">
                    <select
                      id={`assign-member-${agent.id}`}
                      name={`assign-member-${agent.id}`}
                      value={assignMemberId}
                      onChange={(e) => setAssignMemberId(e.target.value)}
                      className="w-full rounded-md border border-border bg-canvas px-2 py-1 text-sm text-text-primary outline-none ring-cyan-500/60 focus:ring"
                    >
                      <option value="">Select member...</option>
                      {Array.isArray(activeMembers) && activeMembers.map((m) => (
                        <option key={m.id} value={m.id}>{m.display_name}</option>
                      ))}
                    </select>
                    <select
                      id={`assign-role-${agent.id}`}
                      name={`assign-role-${agent.id}`}
                      value={assignRole}
                      onChange={(e) => setAssignRole(e.target.value)}
                      className="w-full rounded-md border border-border bg-canvas px-2 py-1 text-sm text-text-primary outline-none ring-cyan-500/60 focus:ring"
                    >
                      {ASSIGNMENT_ROLES.map((r) => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={handleConfirmAssign}
                        className="inline-flex items-center justify-center rounded-md border border-emerald-500/40 bg-emerald-500/20 px-2 py-1 text-xs font-semibold text-emerald-50 hover:bg-emerald-500/30"
                      >
                        Assign
                      </button>
                      <button
                        type="button"
                        onClick={handleCancelAssign}
                        className="inline-flex items-center justify-center rounded-md border border-slate-700 bg-slate-800 px-2 py-1 text-xs font-semibold text-slate-100 hover:bg-slate-700/80"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : assignment ? (
                  <div className="flex w-full gap-2">
                    <button
                      type="button"
                      onClick={() => handleStartAssign(agent.id)}
                      className="inline-flex items-center justify-center rounded-md border border-cyan-500/40 bg-cyan-500/20 px-2 py-1 text-xs font-semibold text-cyan-50 hover:bg-cyan-500/30"
                    >
                      Reassign
                    </button>
                    <button
                      type="button"
                      onClick={() => handleUnassign(assignment.id)}
                      className="inline-flex items-center justify-center rounded-md border border-rose-500/40 bg-rose-500/25 px-2 py-1 text-xs font-semibold text-rose-50 hover:bg-rose-500/35"
                    >
                      Unassign
                    </button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => handleStartAssign(agent.id)}
                    className="inline-flex items-center justify-center rounded-md border border-cyan-500/40 bg-cyan-500/20 px-3 py-1 text-xs font-semibold text-cyan-50 hover:bg-cyan-500/30"
                  >
                    Assign
                  </button>
                )}
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}
