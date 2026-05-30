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
        <div className="text-text-dim">Loading workspace data...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-panel-solid border border-border p-6 rounded-card">
            <h3 className="text-lg font-medium text-text-primary mb-2">Current Workspace</h3>
            <p className="text-text-secondary">Name: <span className="font-semibold">{activeWorkspace?.name || "N/A"}</span></p>
            <p className="text-text-secondary mt-2">
              Environment: 
              <span className={`ml-2 px-2 py-1 rounded text-xs uppercase font-medium ${activeWorkspace?.environment === 'production' ? 'bg-accent-violet/10 text-accent-violet' : 'bg-border/50 text-text-secondary'}`}>
                {activeWorkspace?.environment || "Unknown"}
              </span>
            </p>
          </div>
          <div className="bg-panel-solid border border-border p-6 rounded-card">
            <h3 className="text-lg font-medium text-text-primary mb-2">Safety State</h3>
            <p className="text-sm text-text-dim">
              Workspace actions are constrained by environment policies and risk gates.
              All destructive or mutating actions require explicit confirmations.
            </p>
            <div className="mt-4 px-3 py-2 bg-state-success/10 border border-state-success/20 text-state-success rounded-md text-sm font-medium w-fit">
              Risk Gates Active
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
