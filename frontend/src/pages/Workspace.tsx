import React from "react";
import PageHeader from "../components/layout/PageHeader";
import { useTenancy } from "../hooks/useTenancy";

export default function Workspace() {
  const { activeWorkspace, loading } = useTenancy();

  return (
    <div className="flex flex-col space-y-6">
      <PageHeader 
        title="Workspace Overview" 
        subtitle="Current workspace status, environment, and configuration." 
      />
      {loading ? (
        <div className="text-slate-400">Loading workspace data...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg">
            <h3 className="text-lg font-medium text-white mb-2">Current Workspace</h3>
            <p className="text-slate-300">Name: <span className="font-semibold">{activeWorkspace?.name || "N/A"}</span></p>
            <p className="text-slate-300 mt-2">
              Environment: 
              <span className={`ml-2 px-2 py-1 rounded text-xs uppercase font-medium ${activeWorkspace?.environment === 'production' ? 'bg-fuchsia-500/10 text-fuchsia-400' : 'bg-slate-700/50 text-slate-300'}`}>
                {activeWorkspace?.environment || "Unknown"}
              </span>
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg">
            <h3 className="text-lg font-medium text-white mb-2">Safety State</h3>
            <p className="text-sm text-slate-400">
              Workspace actions are constrained by environment policies and risk gates.
              All destructive or mutating actions require explicit confirmations.
            </p>
            <div className="mt-4 px-3 py-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-md text-sm font-medium w-fit">
              Risk Gates Active
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
