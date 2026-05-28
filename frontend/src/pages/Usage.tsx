import React from "react";
import { useUsage } from "../hooks/useUsage";
import { UsageMeterCard } from "../components/billing/UsageMeterCard";

export default function Usage() {
  const { summary, loading, error, getMetricProgress } = useUsage();

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-8 text-white">
      <div>
        <h2 className="text-3xl font-extrabold mb-2 tracking-tight">System Usage & Quotas</h2>
        <p className="text-neutral-400">Track real-time api limits and active operations consumption metrics.</p>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-sm font-semibold">
          Error: {error}
        </div>
      )}

      {loading ? (
        <div className="h-64 bg-neutral-900/50 rounded-xl animate-pulse" />
      ) : (
        <div className="space-y-6">
          <UsageMeterCard summary={summary} getMetricProgress={getMetricProgress} />

          {/* Explanation notes */}
          <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 space-y-4">
            <h3 className="text-md font-bold text-neutral-300">Understanding Quota Blocks</h3>
            <p className="text-sm text-neutral-400 leading-relaxed">
              When consumption reaches 100%, the zDash guardian locks corresponding features (e.g. running new backtests, generating marketing tokens, or triggering physical IoT actions) to protect account credentials and control spending spikes. Upgrading to a premium tier automatically raises caps instantly.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
export { Usage };
