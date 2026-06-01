import { useState, type FormEvent } from "react";
import Button from "../components/common/Button";
import Badge from "../components/common/Badge";
import AgentAssignmentBoard from "../components/team/AgentAssignmentBoard";
import { useTeam } from "../hooks/useTeam";
import { useT } from "../hooks/useT";
import type { TeamMember } from "../api/types";

const TABS = ["Overview", "Members", "Invitations", "Workspace Access", "Agent Assignments", "Activity"] as const;
type TabName = (typeof TABS)[number];

const ROLE_OPTIONS = ["owner", "admin", "operator", "analyst", "developer", "viewer"];
const ACCESS_LEVELS = ["owner", "manage", "write", "read"];

const roleBadgeVariant = (role: string) => {
  switch (role) {
    case "owner": return "success" as const;
    case "admin": return "warning" as const;
    case "operator": return "normal" as const;
    case "analyst": return "normal" as const;
    case "developer": return "normal" as const;
    case "viewer": return "muted" as const;
    default: return "muted" as const;
  }
};

const statusBadgeVariant = (status: string) => {
  switch (status) {
    case "active": return "success" as const;
    case "invited": return "warning" as const;
    case "suspended": return "danger" as const;
    case "removed": return "muted" as const;
    default: return "muted" as const;
  }
};

export default function TeamRoster() {
  const { t } = useT();
  const [activeTab, setActiveTab] = useState<TabName>("Overview");
  const [searchQuery, setSearchQuery] = useState("");
  const {
    members, invitations, workspaceAccess, agentAssignments, activity, summary,
    loading, error,
    invite, revokeInvite, resendInvite, updateRole,
    suspend, reactivate, remove,
    grantAccess, revokeAccess,
    assignAgent, unassignAgent,
  } = useTeam();

  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("analyst");
  const [inviteError, setInviteError] = useState<string | null>(null);
  const [inviteSending, setInviteSending] = useState(false);

  const [confirmMemberId, setConfirmMemberId] = useState<string | null>(null);
  const [confirmAction, setConfirmAction] = useState<"suspend" | "reactivate" | "remove" | null>(null);

  const [grantMemberId, setGrantMemberId] = useState("");
  const [grantAccessLevel, setGrantAccessLevel] = useState("read");
  const [grantError, setGrantError] = useState<string | null>(null);

  const filteredMembers = Array.isArray(members)
    ? members.filter((m) => {
        if (!searchQuery) return true;
        const q = searchQuery.toLowerCase();
        return (
          (m.display_name ?? "").toLowerCase().includes(q) ||
          (m.email ?? "").toLowerCase().includes(q) ||
          (m.role ?? "").toLowerCase().includes(q) ||
          (m.status ?? "").toLowerCase().includes(q)
        );
      })
    : [];

  const activeMembers = Array.isArray(members)
    ? members.filter((m) => m.status === "active")
    : [];

  async function handleInvite(e: FormEvent) {
    e.preventDefault();
    setInviteError(null);
    if (!inviteEmail.trim()) {
      setInviteError("Email is required.");
      return;
    }
    setInviteSending(true);
    try {
      await invite(inviteEmail.trim(), inviteRole);
      setInviteEmail("");
      setInviteRole("analyst");
    } catch (err: any) {
      setInviteError(err?.message ?? "Failed to send invitation.");
    } finally {
      setInviteSending(false);
    }
  }

  function handleConfirmAction() {
    if (!confirmMemberId || !confirmAction) return;
    const actionFn = confirmAction === "suspend" ? suspend
      : confirmAction === "reactivate" ? reactivate
      : remove;
    actionFn(confirmMemberId).catch(() => {});
    setConfirmMemberId(null);
    setConfirmAction(null);
  }

  async function handleGrantAccess() {
    if (!grantMemberId) {
      setGrantError(t('team.please_select_member'));
      return;
    }
    setGrantError(null);
    try {
      await grantAccess("ws-1", grantMemberId, grantAccessLevel);
      setGrantMemberId("");
      setGrantAccessLevel("read");
    } catch (err: any) {
      setGrantError(err?.message ?? t('team.failed_to_grant_access'));
    }
  }

  if (loading) {
    return (
      <section className="mx-auto flex w-full max-w-[112rem] flex-col gap-6 px-1 py-2 text-text-primary sm:px-2 lg:px-4">
        <div className="flex items-center justify-center py-20">
          <div className="text-sm text-text-dim">Loading team workspace...</div>
        </div>
      </section>
    );
  }

  return (
    <section className="mx-auto flex w-full max-w-[112rem] flex-col gap-6 px-1 py-2 text-text-primary sm:px-2 lg:px-4">
      <div className="rounded-3xl border border-border/70 bg-canvas-lighter/60 p-6 shadow-glass-lg backdrop-blur">
        <p className="text-xs font-bold uppercase tracking-[0.32em] text-cyan-300">zDash</p>
        <div className="mt-3 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-3xl font-black tracking-tight text-text-primary md:text-4xl">Team Workspace</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-text-secondary">
              Manage team members, invitations, workspace access, and AI agent assignments.
            </p>
          </div>
        </div>
        {error ? (
          <div className="mt-4 rounded-md border border-rose-500/40 bg-rose-500/10 px-4 py-2 text-sm text-rose-200">
            {error}
          </div>
        ) : null}
      </div>

      <div className="flex flex-wrap gap-1 rounded-2xl border border-border bg-panel-hover p-1">
        {TABS.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={`rounded-xl px-4 py-2 text-xs font-bold uppercase tracking-[0.16em] transition ${
              activeTab === tab
                ? "bg-cyan-500/20 text-cyan-100"
                : "text-text-dim hover:text-text-secondary"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === "Overview" && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {summary ? (
            <>
              <div className="rounded-2xl border border-border bg-panel-hover p-4">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-text-dim">Total Members</p>
                <p className="mt-2 text-3xl font-black text-text-primary">{summary.total_members ?? 0}</p>
              </div>
              <div className="rounded-2xl border border-border bg-panel-hover p-4">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-text-dim">Active Members</p>
                <p className="mt-2 text-3xl font-black text-emerald-400">{summary.active_members ?? 0}</p>
              </div>
              <div className="rounded-2xl border border-border bg-panel-hover p-4">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-text-dim">Pending Invitations</p>
                <p className="mt-2 text-3xl font-black text-amber-400">{summary.pending_invitations ?? 0}</p>
              </div>
              <div className="rounded-2xl border border-border bg-panel-hover p-4">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-text-dim">Admins</p>
                <p className="mt-2 text-3xl font-black text-text-primary">{summary.admins ?? 0}</p>
              </div>
              {summary.is_last_owner ? (
                <div className="col-span-full rounded-2xl border border-amber-500/40 bg-amber-500/10 p-4">
                  <p className="text-sm font-semibold text-amber-200">
                    You are the last owner. Transfer ownership or add another admin before removing yourself.
                  </p>
                </div>
              ) : null}
            </>
          ) : (
            <div className="col-span-full flex items-center justify-center py-10 text-sm text-text-dim">
              No summary data available.
            </div>
          )}
        </div>
      )}

      {activeTab === "Members" && (
        <div className="rounded-2xl border border-border bg-panel-hover">
          <div className="border-b border-border p-4">
            <input
              id="member-search"
              name="member-search"
              type="text"
              placeholder="Search members..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none ring-cyan-500/60 focus:ring"
            />
          </div>
          {Array.isArray(filteredMembers) && filteredMembers.length > 0 ? (
            <div className="divide-y divide-border">
              {filteredMembers.map((m) => (
                <div key={m.id} className="flex flex-col gap-2 p-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-semibold text-text-primary">{m.display_name ?? "Unnamed"}</p>
                      <Badge variant={roleBadgeVariant(m.role)}>{m.role ?? "viewer"}</Badge>
                    </div>
                    <p className="mt-1 text-xs text-text-dim">{m.email ?? ""}</p>
                    <div className="mt-1 flex items-center gap-2">
                      <Badge variant={statusBadgeVariant(m.status)}>{m.status ?? "unknown"}</Badge>
                      {m.last_seen_at ? (
                        <span className="text-[11px] text-text-dim">
                          Last seen: {new Date(m.last_seen_at).toLocaleDateString()}
                        </span>
                      ) : null}
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(["admin", "operator", "analyst", "developer", "viewer"] as const).map((r) => (
                      <button
                        key={r}
                        type="button"
                        onClick={() => updateRole(m.id, r).catch(() => {})}
                        className={`rounded-md border px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.1em] transition ${
                          m.role === r
                            ? "border-cyan-500/40 bg-cyan-500/20 text-cyan-100"
                            : "border-border text-text-dim hover:text-text-secondary"
                        }`}
                      >
                        {r}
                      </button>
                    ))}
                    {m.status === "active" ? (
                      <Button variant="danger" onClick={() => { setConfirmMemberId(m.id); setConfirmAction("suspend"); }}>
                        Suspend
                      </Button>
                    ) : m.status === "suspended" ? (
                      <Button variant="primary" onClick={() => reactivate(m.id).catch(() => {})}>
                        Reactivate
                      </Button>
                    ) : null}
                    <Button variant="danger" onClick={() => { setConfirmMemberId(m.id); setConfirmAction("remove"); }}>
                      Remove
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center py-8 text-sm text-text-dim">
              No members found.
            </div>
          )}
        </div>
      )}

      {activeTab === "Invitations" && (
        <div className="flex flex-col gap-4">
          <form
            onSubmit={(e) => { void handleInvite(e); }}
            className="rounded-2xl border border-border bg-panel-hover p-4"
          >
            <h2 className="text-sm font-semibold text-text-primary">Invite Team Member</h2>
            <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-end">
              <div className="flex-1">
                <label htmlFor="invite-email" className="text-xs font-semibold text-text-dim">Email</label>
                <input
                  id="invite-email"
                  name="invite-email"
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="email@example.com"
                  className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none ring-cyan-500/60 focus:ring"
                />
              </div>
              <div>
                <label htmlFor="invite-role" className="text-xs font-semibold text-text-dim">Role</label>
                <select
                  id="invite-role"
                  name="invite-role"
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value)}
                  className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none ring-cyan-500/60 focus:ring"
                >
                  {ROLE_OPTIONS.map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>
              <Button type="submit" variant="primary" disabled={inviteSending}>
                {inviteSending ? "Sending..." : "Invite"}
              </Button>
            </div>
            {inviteError ? (
              <p className="mt-2 text-xs text-state-danger">{inviteError}</p>
            ) : null}
          </form>

          <div className="rounded-2xl border border-border bg-panel-hover">
            <div className="border-b border-border px-4 py-3">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-text-dim">
                Pending Invitations ({invitations?.length ?? 0})
              </p>
            </div>
            {Array.isArray(invitations) && invitations.length > 0 ? (
              <div className="divide-y divide-border">
                {invitations.map((inv) => (
                  <div key={inv.id} className="flex flex-col gap-2 p-4 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm font-semibold text-text-primary">{inv.email ?? ""}</p>
                      <div className="mt-1 flex items-center gap-2">
                        <Badge variant={roleBadgeVariant(inv.role)}>{inv.role}</Badge>
                        <Badge variant={inv.status === "pending" ? "warning" : inv.status === "accepted" ? "success" : "muted"}>
                          {inv.status ?? "unknown"}
                        </Badge>
                        <span className="text-xs text-text-dim">by {inv.invited_by ?? "system"}</span>
                      </div>
                      {inv.expires_at ? (
                        <p className="mt-1 text-[11px] text-text-dim">
                          Expires: {new Date(inv.expires_at).toLocaleDateString()}
                        </p>
                      ) : null}
                    </div>
                    <div className="flex gap-2">
                      <Button variant="primary" onClick={() => resendInvite(inv.id).catch(() => {})}>
                        Resend
                      </Button>
                      <Button variant="danger" onClick={() => revokeInvite(inv.id).catch(() => {})}>
                        Revoke
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center py-8 text-sm text-text-dim">
                No pending invitations.
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "Workspace Access" && (
        <div className="flex flex-col gap-4">
          <div className="rounded-2xl border border-border bg-panel-hover p-4">
            <h2 className="text-sm font-semibold text-text-primary">Grant Workspace Access</h2>
            <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-end">
              <div className="flex-1">
                <label htmlFor="grant-member" className="text-xs font-semibold text-text-dim">Member</label>
                <select
                  id="grant-member"
                  name="grant-member"
                  value={grantMemberId}
                  onChange={(e) => setGrantMemberId(e.target.value)}
                  className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none ring-cyan-500/60 focus:ring"
                >
                  <option value="">Select member...</option>
                  {Array.isArray(activeMembers) && activeMembers.map((m) => (
                    <option key={m.id} value={m.id}>{m.display_name} ({m.email})</option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="grant-level" className="text-xs font-semibold text-text-dim">Access Level</label>
                <select
                  id="grant-level"
                  name="grant-level"
                  value={grantAccessLevel}
                  onChange={(e) => setGrantAccessLevel(e.target.value)}
                  className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none ring-cyan-500/60 focus:ring"
                >
                  {ACCESS_LEVELS.map((l) => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </div>
              <Button variant="primary" onClick={() => { void handleGrantAccess(); }}>
                Grant Access
              </Button>
            </div>
            {grantError ? (
              <p className="mt-2 text-xs text-state-danger">{grantError}</p>
            ) : null}
          </div>

          <div className="rounded-2xl border border-border bg-panel-hover">
            <div className="border-b border-border px-4 py-3">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-text-dim">
                Current Access ({workspaceAccess?.length ?? 0})
              </p>
            </div>
            {Array.isArray(workspaceAccess) && workspaceAccess.length > 0 ? (
              <div className="divide-y divide-border">
                {workspaceAccess.map((acc) => {
                  const member = Array.isArray(members)
                    ? members.find((m) => m.id === acc.member_id)
                    : undefined;
                  return (
                    <div key={acc.id} className="flex items-center justify-between p-4">
                      <div>
                        <p className="text-sm text-text-primary">{member?.display_name ?? acc.member_id}</p>
                        <Badge variant={roleBadgeVariant(acc.access_level)}>{acc.access_level}</Badge>
                      </div>
                      <Button variant="danger" onClick={() => revokeAccess(acc.id).catch(() => {})}>
                        Revoke
                      </Button>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="flex items-center justify-center py-8 text-sm text-text-dim">
                {t('team.no_workspace_access')}
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "Agent Assignments" && (
        <AgentAssignmentBoard
          assignments={agentAssignments}
          members={members}
          onAssign={(agentId, memberId, role) => {
            assignAgent("ws-1", agentId, memberId, role).catch(() => {});
          }}
          onUnassign={(assignmentId) => {
            unassignAgent(assignmentId).catch(() => {});
          }}
        />
      )}

      {activeTab === "Activity" && (
        <div className="rounded-2xl border border-border bg-panel-hover">
          <div className="border-b border-border px-4 py-3">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-text-dim">
              Team Activity ({activity?.length ?? 0})
            </p>
          </div>
          {Array.isArray(activity) && activity.length > 0 ? (
            <div className="divide-y divide-border">
              {activity.map((act) => (
                <div key={act.id} className="p-4">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-text-primary">{act.actor ?? "system"}</span>
                    <span className="text-xs text-text-dim">{act.action ?? ""}</span>
                  </div>
                  <p className="mt-1 text-sm text-text-secondary">{act.details ?? ""}</p>
                  {act.created_at ? (
                    <p className="mt-1 text-[11px] text-text-dim">
                      {new Date(act.created_at).toLocaleString()}
                    </p>
                  ) : null}
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center py-8 text-sm text-text-dim">
              No activity recorded.
            </div>
          )}
        </div>
      )}

      {confirmMemberId && confirmAction ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl border border-border bg-panel-solid p-6 shadow-2xl">
            <p className="text-sm font-semibold text-text-primary">{t('common.are_you_sure')}</p>
            <p className="mt-2 text-sm text-text-secondary">
              {t('team.this_will')} {confirmAction} {t('team.member')}. {confirmAction === "remove" ? t('common.this_action_cannot_be_undone') : ""}
            </p>
            <div className="mt-4 flex gap-3">
              <Button variant="danger" onClick={handleConfirmAction}>
                {t('team.yes_' + confirmAction)}
              </Button>
              <Button variant="secondary" onClick={() => { setConfirmMemberId(null); setConfirmAction(null); }}>
                {t('common.cancel')}
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
