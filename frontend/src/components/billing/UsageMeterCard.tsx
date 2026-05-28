import React from "react";
import { UsageSummary } from "../../api/types";

interface UsageMeterCardProps {
  summary: UsageSummary | null;
  getMetricProgress: (key: string) => {
    usage: number;
    limit: number;
    percent: number;
    warning: boolean;
    exceeded: boolean;
  };
}

export function UsageMeterCard({ summary, getMetricProgress }: UsageMeterCardProps) {
  if (!summary) {
    return (
      <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 animate-pulse space-y-4">
        <div className="h-6 w-1/4 bg-neutral-800 rounded" />
        <div className="h-4 w-full bg-neutral-800 rounded" />
        <div className="h-4 w-full bg-neutral-800 rounded" />
      </div>
    );
  }

  const trackedMetrics = [
    { label: "Backtest Runs", key: "backtest_runs" },
    { label: "Content Gen Tokens", key: "content_generation_tokens" },
    { label: "Marketplace Plugins", key: "marketplace_plugins" },
    { label: "IoT Actions", key: "iot_actions" },
  ];

  return (
    <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 flex flex-col gap-6">
      <div className="flex justify-between items-start">
        <div>
          <div className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">Usage & Quotas</div>
          <h4 className="text-xl font-bold text-white mt-1">Resource Consumption</h4>
        </div>
        {summary.reset_timestamp && (
          <div className="text-right">
            <span className="text-neutral-500 text-xs block uppercase font-medium">Next Reset</span>
            <span className="text-sm font-medium text-neutral-300">
              {new Date(summary.reset_timestamp).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>

      <div className="space-y-5">
        {trackedMetrics.map((m) => {
          const prog = getMetricProgress(m.key);
          const limitStr = prog.limit === 999999 ? "∞" : prog.limit.toLocaleString();
          return (
            <div key={m.key} className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="font-semibold text-neutral-300">{m.label}</span>
                <span className="text-neutral-400 font-mono">
                  {prog.usage.toLocaleString()} / {limitStr}
                </span>
              </div>

              {/* Progress bar container */}
              <div className="w-full bg-neutral-900 rounded-full h-2.5 overflow-hidden border border-neutral-800/80">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    prog.exceeded
                      ? "bg-rose-500"
                      : prog.warning
                      ? "bg-amber-500 animate-pulse"
                      : "bg-violet-600"
                  }`}
                  style={{ width: `${Math.min(prog.percent, 100)}%` }}
                />
              </div>

              {/* Badges / description helper */}
              {prog.exceeded ? (
                <div className="text-rose-400 text-xs flex items-center gap-1">
                  <span>❌</span>
                  <span>Limit exceeded! Some operations in this category are blocked. Upgrade your plan to resume.</span>
                </div>
              ) : prog.warning ? (
                <div className="text-amber-400 text-xs flex items-center gap-1">
                  <span>⚠</span>
                  <span>Approaching usage limit ({Math.round(prog.percent)}% consumed). Recommend upgrading soon.</span>
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}
