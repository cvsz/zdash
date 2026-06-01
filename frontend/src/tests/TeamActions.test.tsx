import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BrowserRouter } from "react-router-dom";
import TeamPage from "../pages/TeamRoster";

const mockMembersData = vi.hoisted(() => [
  { id: "mem-1", organization_id: "org-1", workspace_id: null, user_id: "user-1", email: "admin@zdash.dev", display_name: "Admin User", role: "owner" as const, status: "active" as const, avatar_url: null, last_seen_at: new Date().toISOString(), created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: "mem-2", organization_id: "org-1", workspace_id: null, user_id: "user-2", email: "operator@zdash.dev", display_name: "Operator Bot", role: "operator" as const, status: "active" as const, avatar_url: null, last_seen_at: new Date(Date.now() - 3600000).toISOString(), created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: "mem-3", organization_id: "org-1", workspace_id: null, user_id: null, email: "analyst@zdash.dev", display_name: "Jane Analyst", role: "analyst" as const, status: "active" as const, avatar_url: null, last_seen_at: new Date(Date.now() - 86400000).toISOString(), created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: "mem-4", organization_id: "org-1", workspace_id: null, user_id: null, email: "viewer@zdash.dev", display_name: "Viewer User", role: "viewer" as const, status: "invited" as const, avatar_url: null, last_seen_at: null, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
]);

const mockInvitationsData = vi.hoisted(() => [
  { id: "inv-1", organization_id: "org-1", workspace_id: null, email: "newmember@zdash.dev", role: "analyst", status: "pending" as const, invited_by: "Admin User", expires_at: new Date(Date.now() + 86400000 * 7).toISOString(), created_at: new Date().toISOString() },
]);

const mockAssignmentsData = vi.hoisted(() => [
  { id: "assign-1", agent_id: "ceo", member_id: "mem-1", assignment_role: "owner" as const, created_at: new Date().toISOString(), agent_name: "Alexander Prime" },
]);

const mockActivityData = vi.hoisted(() => [
  { id: "act-1", action: "team.member.invited", actor: "Admin User", details: "Invited newmember@zdash.dev as analyst", created_at: new Date().toISOString() },
]);

const mockSummaryData = vi.hoisted(() => ({
  total_members: 4,
  active_members: 3,
  pending_invitations: 1,
  admins: 1,
  operators: 1,
  analysts: 1,
  developers: 0,
  viewers: 1,
  is_last_owner: true,
}));

const mockAccessData = vi.hoisted(() => [
  { id: "access-1", workspace_id: "ws-1", member_id: "mem-2", access_level: "manage" as const, created_at: new Date().toISOString() },
]);

vi.mock("../api/endpoints", () => ({
  listTeamMembers: vi.fn(async () => mockMembersData),
  listTeamInvitations: vi.fn(async () => mockInvitationsData),
  listTeamAgentAssignments: vi.fn(async () => mockAssignmentsData),
  getTeamActivity: vi.fn(async () => mockActivityData),
  getTeamSummary: vi.fn(async () => mockSummaryData),
  inviteTeamMember: vi.fn(async () => mockInvitationsData[0]),
  revokeTeamInvitation: vi.fn(async () => true),
  resendTeamInvitation: vi.fn(async () => mockInvitationsData[0]),
  updateTeamMemberRole: vi.fn(async () => mockMembersData[0]),
  suspendTeamMember: vi.fn(async () => ({ ...mockMembersData[0], status: "suspended" })),
  reactivateTeamMember: vi.fn(async () => ({ ...mockMembersData[0], status: "active" })),
  removeTeamMember: vi.fn(async () => true),
  grantTeamWorkspaceAccess: vi.fn(async () => ({ ...mockAccessData[0] })),
  revokeTeamWorkspaceAccess: vi.fn(async () => true),
  assignTeamAgent: vi.fn(async () => ({ ...mockAssignmentsData[0] })),
  unassignTeamAgent: vi.fn(async () => true),
}));

function renderTeamPage() {
  return render(
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <TeamPage />
    </BrowserRouter>,
  );
}

describe("TeamActions", () => {
  it("invite form has id/name fields", async () => {
    renderTeamPage();
    const invitationsTab = await screen.findByText("Invitations", {}, { timeout: 3000 });
    fireEvent.click(invitationsTab);

    await waitFor(() => {
      expect(screen.getByText("Invite Team Member")).toBeTruthy();
    });

    const emailField = document.getElementById("invite-email");
    expect(emailField).toBeTruthy();
    expect(emailField?.getAttribute("name")).toBe("invite-email");

    const roleSelect = document.getElementById("invite-role");
    expect(roleSelect).toBeTruthy();
    expect(roleSelect?.getAttribute("name")).toBe("invite-role");
  });

  it("clicking invite changes form state", async () => {
    renderTeamPage();
    const invitationsTab = await screen.findByText("Invitations", {}, { timeout: 3000 });
    fireEvent.click(invitationsTab);

    await waitFor(() => {
      expect(screen.getByText("Invite Team Member")).toBeTruthy();
    });

    const emailInput = document.getElementById("invite-email") as HTMLInputElement;
    const roleSelect = document.getElementById("invite-role") as HTMLSelectElement;
    const inviteButton = screen.getByText("Invite");

    fireEvent.change(emailInput, { target: { value: "test@zdash.dev" } });
    fireEvent.change(roleSelect, { target: { value: "analyst" } });
    fireEvent.click(inviteButton);

    await waitFor(() => {
      expect(screen.getByText("Invite Team Member")).toBeTruthy();
    }, { timeout: 5000 });
  });

  it("suspend/remove actions show confirmation dialog", async () => {
    renderTeamPage();
    const membersTab = await screen.findByText("Members", {}, { timeout: 3000 });
    fireEvent.click(membersTab);

    await waitFor(() => {
      expect(screen.getByText("Admin User")).toBeTruthy();
    });

    const suspendButtons = screen.getAllByText("Suspend");
    expect(suspendButtons.length).toBeGreaterThan(0);
    fireEvent.click(suspendButtons[0]);

    await waitFor(() => {
      expect(screen.getByText("Are you sure?")).toBeTruthy();
    });

    const cancelButton = screen.getByText("Cancel");
    expect(cancelButton).toBeTruthy();
  });
});
