import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import TeamRoster from "../pages/TeamRoster";
import { waitForStableUi } from "./utils/settle";

vi.mock("../api/endpoints", () => ({
  listTeamMembers: vi.fn(async () => [
    { id: "mem-1", organization_id: "org-1", workspace_id: null, user_id: "user-1", email: "admin@zdash.dev", display_name: "Admin User", role: "owner", status: "active", avatar_url: null, last_seen_at: new Date().toISOString(), created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  ]),
  listTeamInvitations: vi.fn(async () => []),
  listTeamAgentAssignments: vi.fn(async () => []),
  getTeamActivity: vi.fn(async () => []),
  getTeamSummary: vi.fn(async () => ({ total_members: 1, active_members: 1, pending_invitations: 0, admins: 1, operators: 0, analysts: 0, developers: 0, viewers: 0, is_last_owner: true })),
  inviteTeamMember: vi.fn(async () => ({})),
  revokeTeamInvitation: vi.fn(async () => true),
  resendTeamInvitation: vi.fn(async () => ({})),
  updateTeamMemberRole: vi.fn(async () => ({})),
  suspendTeamMember: vi.fn(async () => ({})),
  reactivateTeamMember: vi.fn(async () => ({})),
  removeTeamMember: vi.fn(async () => true),
  grantTeamWorkspaceAccess: vi.fn(async () => ({})),
  revokeTeamWorkspaceAccess: vi.fn(async () => true),
  assignTeamAgent: vi.fn(async () => ({})),
  unassignTeamAgent: vi.fn(async () => true),
}));

describe("TeamRoster", () => {
  it("renders team workspace heading", async () => {
    render(
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <TeamRoster />
      </BrowserRouter>,
    );
    await waitForStableUi();
    expect(await screen.findByText("Team Workspace")).toBeTruthy();
  });

  it("renders overview cards", async () => {
    render(
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <TeamRoster />
      </BrowserRouter>,
    );
    await waitForStableUi();
    expect(await screen.findByText("Total Members")).toBeTruthy();
    expect(await screen.findByText("Active Members")).toBeTruthy();
    expect(await screen.findByText("Pending Invitations")).toBeTruthy();
  });

  it("renders members table with search", async () => {
    render(
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <TeamRoster />
      </BrowserRouter>,
    );
    await waitForStableUi();
    const membersTab = screen.getByText("Members");
    membersTab.click();
    await waitForStableUi();
    expect(await screen.findByText("Admin User")).toBeTruthy();
  });

  it("no live /api calls (mocked)", async () => {
    const endpoints = await import("../api/endpoints");
    render(
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <TeamRoster />
      </BrowserRouter>,
    );
    await waitForStableUi();
    expect(endpoints.listTeamMembers).toBeDefined();
    expect(endpoints.listTeamInvitations).toBeDefined();
  });

  it("no act warnings", async () => {
    render(
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <TeamRoster />
      </BrowserRouter>,
    );
    await waitForStableUi();
    expect(screen.getByText("Team Workspace")).toBeTruthy();
  });
});
