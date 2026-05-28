import React from "react";
import { CustomerHealth } from "../../api/types";

interface CustomerHealthCardProps {
  health: CustomerHealth | null;
}

export function CustomerHealthCard({ health }: CustomerHealthCardProps) {
  if (!health) {
    return (
      <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 animate-pulse space-y-4">
        <div className="h-6 w-1/4 bg-neutral-800 rounded" />
        <div className="h-4 w-full bg-neutral-800 rounded animate-pulse" />
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "excellent":
        return "text-green-400 bg-green-500/10 border-green-500/20";
      case "fair":
        return "text-amber-400 bg-amber-500/10 border-amber-500/20";
      default:
        return "text-rose-400 bg-rose-500/10 border-rose-500/20";
    }
  };

  return (
    <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <div className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">success management</div>
          <h4 className="text-xl font-bold text-white mt-1">Tenant Account Health</h4>
        </div>

        <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border uppercase ${getStatusColor(health.status)}`}>
          {health.status} health
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-sm text-neutral-300">
        <div className="p-4 rounded-lg bg-neutral-900/30 border border-neutral-850 flex flex-col justify-between h-24">
          <span className="text-[10px] text-neutral-500 uppercase font-bold tracking-wider">Health Score</span>
          <span className="text-2xl font-black text-white">{health.health_score}%</span>
        </div>

        <div className="p-4 rounded-lg bg-neutral-900/30 border border-neutral-850 flex flex-col justify-between h-24">
          <span className="text-[10px] text-neutral-500 uppercase font-bold tracking-wider">Active Operators</span>
          <span className="text-2xl font-black text-white">{health.active_users} active</span>
        </div>

        <div className="p-4 rounded-lg bg-neutral-900/30 border border-neutral-850 flex flex-col justify-between h-24">
          <span className="text-[10px] text-neutral-500 uppercase font-bold tracking-wider">Consumption Trend</span>
          <span className="text-2xl font-black text-violet-400 capitalize">{health.usage_trend}</span>
        </div>
      </div>
    </div>
  );
}
export default CustomerHealthCard;
