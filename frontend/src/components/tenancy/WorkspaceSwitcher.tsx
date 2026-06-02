import React from "react";
import { useTenancy } from "../../hooks/useTenancy";
import { useT } from '../../hooks/useT';

export const WorkspaceSwitcher: React.FC = () => {
  const { t } = useT();
  const { workspaces = [], activeWorkspace, switchWorkspace } = useTenancy();

  if (!Array.isArray(workspaces) || workspaces.length === 0) return null;

  return (
    <div className="flex items-center space-x-2">
      <label htmlFor="workspace-switcher" className="text-sm text-gray-400">
        {t('tenancy.workspace_switcher_label')}:
      </label>
      <select
        id="workspace-switcher"
        name="workspace"
        className="bg-slate-800 text-white border border-slate-700 rounded px-2 py-1 text-sm focus:outline-none"
        value={activeWorkspace?.id || ""}
        onChange={(e) => switchWorkspace(e.target.value)}
      >
        {workspaces.map((ws) => (
          <option key={ws.id} value={ws.id}>
            {ws.name} ({ws.environment})
          </option>
        ))}
      </select>
    </div>
  );
};
