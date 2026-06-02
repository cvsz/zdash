import React from "react";
import type { Workspace } from "../../api/types";
import { useT } from '../../hooks/useT';

interface Props {
  workspaces: Workspace[];
}

export const WorkspaceTable: React.FC<Props> = ({ workspaces }) => {
  const { t } = useT();

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
      <table className="min-w-full text-left text-sm text-gray-300">
        <thead className="bg-slate-800 border-b border-slate-700">
          <tr>
            <th className="px-4 py-3 font-medium">{t('workspace_table.name')}</th>
            <th className="px-4 py-3 font-medium">{t('workspace_table.slug')}</th>
            <th className="px-4 py-3 font-medium">{t('workspace_table.environment')}</th>
            <th className="px-4 py-3 font-medium">{t('common.status')}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {workspaces.map((ws) => (
            <tr key={ws.id} className="hover:bg-slate-800/50 transition-colors">
              <td className="px-4 py-3 font-medium text-white">{ws.name}</td>
              <td className="px-4 py-3 text-slate-400">{ws.slug}</td>
              <td className="px-4 py-3 capitalize">
                <span className={`px-2 py-1 rounded text-xs font-medium ${ws.environment === 'production' ? 'bg-fuchsia-500/10 text-fuchsia-400' : 'bg-slate-700/50 text-slate-300'}`}>
                  {ws.environment}
                </span>
              </td>
              <td className="px-4 py-3">
                {ws.is_active ? (
                  <span className="text-emerald-400 font-medium">{t('common.active')}</span>
                ) : (
                  <span className="text-slate-500">{t('common.inactive')}</span>
                )}
              </td>
            </tr>
          ))}
          {workspaces.length === 0 && (
            <tr>
              <td colSpan={4} className="px-4 py-8 text-center text-slate-500">
                {t('workspace_table.empty')}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};
