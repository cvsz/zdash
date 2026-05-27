import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import Admin from "../pages/Admin";
import {
  createAdminUser,
  deactivateAdminUser,
  getAdminSafetyCheck,
  listAdminUsers,
  listAuditLogs,
  updateAdminUser,
} from "../api/endpoints";
import { useAuth } from "../hooks/useAuth";

vi.mock("../hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("../api/endpoints", () => ({
  listAdminUsers: vi.fn(),
  listAuditLogs: vi.fn(),
  getAdminSafetyCheck: vi.fn(),
  createAdminUser: vi.fn(),
  deactivateAdminUser: vi.fn(),
  updateAdminUser: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);
const mockedListAdminUsers = vi.mocked(listAdminUsers);
const mockedListAuditLogs = vi.mocked(listAuditLogs);
const mockedGetAdminSafetyCheck = vi.mocked(getAdminSafetyCheck);
const mockedCreateAdminUser = vi.mocked(createAdminUser);
const mockedDeactivateAdminUser = vi.mocked(deactivateAdminUser);
const mockedUpdateAdminUser = vi.mocked(updateAdminUser);

describe("Admin page", () => {
  beforeEach(() => {
    mockedUseAuth.mockReturnValue({
      user: { username: "admin", role: "admin" },
      loading: false,
      isAuthenticated: true,
      isAdmin: true,
      isDevBypass: false,
      mode: "token",
      login: vi.fn(),
      logout: vi.fn(),
      refreshProfile: vi.fn(),
    });

    mockedListAdminUsers.mockResolvedValue([
      {
        id: "u1",
        email: "admin",
        display_name: "Admin",
        role: "admin",
        is_active: true,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
      {
        id: "u2",
        email: "operator@example.com",
        display_name: "Operator",
        role: "operator",
        is_active: true,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
    ]);

    mockedListAuditLogs.mockResolvedValue([
      {
        id: "a1",
        actor_user_id: "",
        actor_email: "admin",
        action: "admin.user.create",
        resource_type: "user",
        resource_id: "u2",
        result: "success",
        ip_address: "",
        user_agent: "",
        metadata: {},
        created_at: "2026-01-01T00:00:00Z",
      },
      {
        id: "a2",
        actor_user_id: "",
        actor_email: "admin",
        action: "auth.login.success",
        resource_type: "auth",
        resource_id: "admin",
        result: "success",
        ip_address: "",
        user_agent: "",
        metadata: {},
        created_at: "2026-01-01T00:01:00Z",
      },
    ]);

    mockedGetAdminSafetyCheck.mockResolvedValue({
      status: "safe",
      warnings: [],
      blockers: [],
      score: 100,
    });

    mockedCreateAdminUser.mockResolvedValue({
      id: "u3",
      email: "viewer@example.com",
      display_name: "Viewer",
      role: "viewer",
      is_active: true,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    });
    mockedDeactivateAdminUser.mockResolvedValue({ deactivated: true, user_id: "u2" });
    mockedUpdateAdminUser.mockResolvedValue({
      id: "u2",
      email: "operator@example.com",
      display_name: "Operator",
      role: "operator",
      is_active: true,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    });
  });

  it("renders admin controls and current user", async () => {
    render(<Admin />);

    await screen.findByText("Admin Session");

    expect(screen.getByText(/Current user: admin \(admin\)/)).toBeTruthy();
    expect(screen.getByText("Users")).toBeTruthy();
    expect(screen.getByText("Audit Logs")).toBeTruthy();
    expect(screen.getByText(/default admin credentials may still be in use/i)).toBeTruthy();
  });

  it("filters audit logs by action", async () => {
    render(<Admin />);

    await screen.findByText("auth.login.success");

    fireEvent.change(screen.getByPlaceholderText("Filter action"), {
      target: { value: "admin.user.create" },
    });

    await waitFor(() => {
      expect(screen.getByText("admin.user.create")).toBeTruthy();
      expect(screen.queryByText("auth.login.success")).toBeNull();
    });
  });
});
