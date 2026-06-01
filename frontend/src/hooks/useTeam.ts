import { useState, useEffect, useCallback } from 'react';
import type { TeamMember, TeamInvitation, TeamWorkspaceAccess, TeamAgentAssignment, TeamActivity, TeamSummary } from '../api/types';
import {
  listTeamMembers, listTeamInvitations, listTeamWorkspaceAccess,
  listTeamAgentAssignments, getTeamActivity, getTeamSummary,
  inviteTeamMember, revokeTeamInvitation, resendTeamInvitation,
  updateTeamMemberRole, suspendTeamMember, reactivateTeamMember, removeTeamMember,
  grantTeamWorkspaceAccess, revokeTeamWorkspaceAccess,
  assignTeamAgent, unassignTeamAgent,
} from '../api/endpoints';

export function useTeam(workspaceId?: string) {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [invitations, setInvitations] = useState<TeamInvitation[]>([]);
  const [workspaceAccess, setWorkspaceAccess] = useState<TeamWorkspaceAccess[]>([]);
  const [agentAssignments, setAgentAssignments] = useState<TeamAgentAssignment[]>([]);
  const [activity, setActivity] = useState<TeamActivity[]>([]);
  const [summary, setSummary] = useState<TeamSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [membersRes, invitationsRes, assignmentsRes, activityRes, summaryRes] = await Promise.all([
        listTeamMembers(workspaceId),
        listTeamInvitations(workspaceId),
        listTeamAgentAssignments(),
        getTeamActivity(),
        getTeamSummary(),
      ]);
      setMembers(Array.isArray(membersRes) ? membersRes : []);
      setInvitations(Array.isArray(invitationsRes) ? invitationsRes : []);
      setAgentAssignments(Array.isArray(assignmentsRes) ? assignmentsRes : []);
      setActivity(Array.isArray(activityRes) ? activityRes : []);
      if (summaryRes) setSummary(summaryRes);
    } catch (err: any) {
      setError(err?.message || 'Failed to load team data');
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const setErrorWrapper = (fn: (...args: any[]) => Promise<any>) => async (...args: any[]) => {
    setError(null);
    try {
      const result = await fn(...args);
      await fetchAll();
      return result;
    } catch (err: any) {
      setError(err?.message || 'Operation failed');
      throw err;
    }
  };

  const invite = setErrorWrapper((email: string, role: string, wsId?: string) =>
    inviteTeamMember(email, role, wsId));
  const revokeInvite = setErrorWrapper((id: string) => revokeTeamInvitation(id));
  const resendInvite = setErrorWrapper((id: string) => resendTeamInvitation(id));
  const updateRole = setErrorWrapper((id: string, role: string) => updateTeamMemberRole(id, role));
  const suspend = setErrorWrapper((id: string) => suspendTeamMember(id));
  const reactivate = setErrorWrapper((id: string) => reactivateTeamMember(id));
  const remove = setErrorWrapper((id: string) => removeTeamMember(id));
  const grantAccess = setErrorWrapper((wsId: string, memberId: string, level: string) =>
    grantTeamWorkspaceAccess(wsId, memberId, level));
  const revokeAccess = setErrorWrapper((id: string) => revokeTeamWorkspaceAccess(id));
  const assignAgent = setErrorWrapper((wsId: string, agentId: string, memberId: string | null, role: string) =>
    assignTeamAgent(wsId, agentId, memberId, role));
  const unassignAgent = setErrorWrapper((id: string) => unassignTeamAgent(id));

  return {
    members, invitations, workspaceAccess, agentAssignments, activity, summary,
    loading, error,
    invite, revokeInvite, resendInvite, updateRole,
    suspend, reactivate, remove,
    grantAccess, revokeAccess,
    assignAgent, unassignAgent,
    refetch: fetchAll,
  };
}
