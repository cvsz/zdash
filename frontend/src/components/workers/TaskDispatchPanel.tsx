import React, { useState } from "react";

interface Props {
  onEnqueue: (type: string, payload?: Record<string, unknown>) => void;
}

export const TaskDispatchPanel: React.FC<Props> = ({ onEnqueue }) => {
  const [taskType, setTaskType] = useState("data_sync");
  
  const handleDispatch = () => {
    onEnqueue(taskType, { dry_run: true });
  };

  return (
    <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex flex-col space-y-4">
      <div>
        <h3 className="text-lg font-medium text-white">Dispatch Task</h3>
        <p className="text-sm text-slate-400">Enqueue a dry-run task for workers to pick up.</p>
      </div>
      <div className="flex items-center space-x-2">
        <select
          value={taskType}
          onChange={(e) => setTaskType(e.target.value)}
          className="flex-1 bg-slate-800 border border-slate-700 text-white rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
        >
          <option value="data_sync">Data Sync</option>
          <option value="metrics_rollup">Metrics Rollup</option>
          <option value="tenant_provision">Tenant Provision</option>
        </select>
        <button
          onClick={handleDispatch}
          className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
        >
          Enqueue Dry-Run
        </button>
      </div>
    </div>
  );
};
