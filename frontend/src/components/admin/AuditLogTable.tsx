import { useMemo, useState } from "react";

import type { AuditLogEntry } from "../../api/types";
import { useT } from '../../hooks/useT';

type AuditLogTableProps = {
  items: AuditLogEntry[];
  loading?: boolean;
  error?: string | null;
};

export default function AuditLogTable({
  items,
  loading = false,
  error,
}: AuditLogTableProps) {
  const { t } = useT();
  const [actionFilter, setActionFilter] = useState("");
  const [resourceFilter, setResourceFilter] = useState("");
  const [userFilter, setUserFilter] = useState("");

  const filteredItems = useMemo(() => {
    const normalizedAction = actionFilter.trim().toLowerCase();
    const normalizedResource = resourceFilter.trim().toLowerCase();
    const normalizedUser = userFilter.trim().toLowerCase();

    return items.filter((item) => {
      const actionMatch =
        !normalizedAction || item.action.toLowerCase().includes(normalizedAction);
      const resourceMatch =
        !normalizedResource ||
        item.resource_type.toLowerCase().includes(normalizedResource) ||
        item.resource_id.toLowerCase().includes(normalizedResource);
      const userMatch =
        !normalizedUser || item.actor_email.toLowerCase().includes(normalizedUser);
      return actionMatch && resourceMatch && userMatch;
    });
  }, [actionFilter, items, resourceFilter, userFilter]);

  return (
    <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-white">{t('admin.audit_log')}</h3>
        <span className="text-xs text-slate-400">{filteredItems.length} {t('common.details')}</span>
      </div>

      <div className="mt-3 grid gap-2 md:grid-cols-3">
        <input
          value={actionFilter}
          onChange={(event) => setActionFilter(event.target.value)}
          placeholder={t('admin.action')}
          className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
        />
        <input
          value={resourceFilter}
          onChange={(event) => setResourceFilter(event.target.value)}
          placeholder={t('audit_log.resource')}
          className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
        />
        <input
          value={userFilter}
          onChange={(event) => setUserFilter(event.target.value)}
          placeholder={t('audit_log.user')}
          className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
        />
      </div>

      {error && (
        <p className="mt-3 rounded-md border border-rose-400/30 bg-rose-500/10 p-2 text-xs text-rose-100">
          {error}
        </p>
      )}

      <div className="mt-3 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-800 text-sm">
          <thead className="bg-slate-950/50 text-left text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th className="px-3 py-2">{t('common.time')}</th>
              <th className="px-3 py-2">{t('audit_log.action')}</th>
              <th className="px-3 py-2">{t('audit_log.resource')}</th>
              <th className="px-3 py-2">{t('audit_log.user')}</th>
              <th className="px-3 py-2">{t('audit_log.details')}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {loading && (
              <tr>
                <td className="px-3 py-3 text-slate-400" colSpan={5}>
                  {t('admin.audit_log')}...
                </td>
              </tr>
            )}
            {!loading && filteredItems.length === 0 && (
              <tr>
                <td className="px-3 py-3 text-slate-400" colSpan={5}>
                  {t('audit_log.no_logs')}
                </td>
              </tr>
            )}
            {!loading &&
              filteredItems.map((item) => (
                <tr key={item.id}>
                  <td className="px-3 py-2 text-slate-300">{item.created_at}</td>
                  <td className="px-3 py-2 text-slate-200">{item.action}</td>
                  <td className="px-3 py-2 text-slate-300">
                    {item.resource_type || "-"}:{item.resource_id || "-"}
                  </td>
                  <td className="px-3 py-2 text-slate-300">{item.actor_email || "system"}</td>
                  <td className="px-3 py-2 text-slate-300">{item.result}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
