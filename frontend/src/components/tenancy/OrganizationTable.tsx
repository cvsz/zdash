import React from "react";
import type { Organization } from "../../api/types";
import { useT } from '../../hooks/useT';

interface Props {
  organizations: Organization[];
}

export const OrganizationTable: React.FC<Props> = ({ organizations }) => {
  const { t } = useT();

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
      <table className="min-w-full text-left text-sm text-gray-300">
        <thead className="bg-slate-800 border-b border-slate-700">
          <tr>
            <th className="px-4 py-3 font-medium">{t('org_table.name')}</th>
            <th className="px-4 py-3 font-medium">{t('org_table.slug')}</th>
            <th className="px-4 py-3 font-medium">{t('billing.plan')}</th>
            <th className="px-4 py-3 font-medium">{t('common.role')}</th>
            <th className="px-4 py-3 font-medium">{t('common.status')}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {organizations.map((org) => (
            <tr key={org.id} className="hover:bg-slate-800/50 transition-colors">
              <td className="px-4 py-3 font-medium text-white">{org.name}</td>
              <td className="px-4 py-3 text-slate-400">{org.slug}</td>
              <td className="px-4 py-3">
                <span className="px-2 py-1 rounded bg-blue-500/10 text-blue-400 text-xs uppercase font-medium">
                  {org.plan}
                </span>
              </td>
              <td className="px-4 py-3 capitalize">{org.role}</td>
              <td className="px-4 py-3">
                <span
                  className={`px-2 py-1 rounded text-xs uppercase font-medium ${
                    org.status === "active"
                      ? "bg-emerald-500/10 text-emerald-400"
                      : "bg-amber-500/10 text-amber-400"
                  }`}
                >
                  {org.status}
                </span>
              </td>
            </tr>
          ))}
          {organizations.length === 0 && (
            <tr>
              <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                {t('org_table.empty')}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};
