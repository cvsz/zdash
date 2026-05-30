import { useCallback, useEffect, useMemo, useState } from "react";

import { DEFAULT_ADMIN_USERNAME } from "../api/auth";
import {
  createAdminUser,
  deactivateAdminUser,
  getAdminSafetyCheck,
  listAdminUsers,
  listAuditLogs,
  updateAdminUser,
} from "../api/endpoints";
import type { AdminSafetyCheck, AdminUser, AuditLogEntry } from "../api/types";
import AuditLogTable from "../components/admin/AuditLogTable";
import UserTable from "../components/admin/UserTable";
import PageHeader from "../components/layout/PageHeader";
import { useAuth } from "../hooks/useAuth";

export default function Admin() {
  const { user } = useAuth();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [safetyCheck, setSafetyCheck] = useState<AdminSafetyCheck | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [nextUsers, nextAuditLogs, nextSafetyCheck] = await Promise.all([
        listAdminUsers(),
        listAuditLogs(),
        getAdminSafetyCheck(),
      ]);
      setUsers(nextUsers);
      setAuditLogs(nextAuditLogs);
      setSafetyCheck(nextSafetyCheck);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Failed to load admin data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const onCreateUser = useCallback(
    async (payload: {
      email: string;
      password: string;
      role: string;
      display_name: string;
    }) => {
      await createAdminUser(payload);
      await loadData();
    },
    [loadData],
  );

  const onSetActive = useCallback(
    async (targetUser: AdminUser, isActive: boolean) => {
      if (isActive) {
        await updateAdminUser(targetUser.id, { is_active: true });
      } else {
        await deactivateAdminUser(targetUser.id);
      }
      await loadData();
    },
    [loadData],
  );

  const hasDefaultAdminWarning = useMemo(() => {
    if (user?.username === DEFAULT_ADMIN_USERNAME) {
      return true;
    }
    const safetyMessages = [
      ...(safetyCheck?.blockers ?? []),
      ...(safetyCheck?.warnings ?? []),
    ];
    return safetyMessages.some((message) =>
      message.toLowerCase().includes("default_admin_password"),
    );
  }, [safetyCheck?.blockers, safetyCheck?.warnings, user?.username]);

  return (
    <div className="space-y-5">
      <PageHeader
        title="Admin"
        subtitle="Role-gated user management and audit review surfaces."
      />

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">Admin Session</h3>
        <p className="mt-1 text-xs text-text-dim">
          Current user: {user?.username} ({user?.role})
        </p>
        {safetyCheck && (
          <p className="mt-2 text-xs text-text-secondary">
            Safety status: {safetyCheck.status.toUpperCase()} · Score {safetyCheck.score}
          </p>
        )}
        {hasDefaultAdminWarning && (
          <p className="mt-2 rounded-md border border-state-warning/30 bg-state-warning/10 px-3 py-2 text-xs text-state-warning">
            Warning: default admin credentials may still be in use. Rotate credentials
            before production use.
          </p>
        )}
        {safetyCheck?.blockers && safetyCheck.blockers.length > 0 && (
          <ul className="mt-2 list-disc space-y-1 pl-5 text-xs text-state-danger">
            {safetyCheck.blockers.map((blocker) => (
              <li key={blocker}>{blocker}</li>
            ))}
          </ul>
        )}
      </section>

      <UserTable
        currentUsername={user?.username ?? "unknown"}
        users={users}
        loading={loading}
        error={error}
        onCreateUser={onCreateUser}
        onSetActive={onSetActive}
      />

      <AuditLogTable items={auditLogs} loading={loading} error={error} />
    </div>
  );
}
