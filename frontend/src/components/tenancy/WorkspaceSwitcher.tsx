import React from "react";
import { useTenancy } from "../../hooks/useTenancy";

export const WorkspaceSwitcher: React.FC = () => {
  const { workspaces, activeWorkspace, switchWorkspace } = useTenancy();

  if (!workspaces.length) return null;

  return (
    <div className="flex items-center space-x-2">
      <label className="text-sm text-gray-400">Workspace:</label>
      <select
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
