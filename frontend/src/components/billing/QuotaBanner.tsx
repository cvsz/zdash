import React from "react";
import { useUsage } from "../../hooks/useUsage";

export function QuotaBanner() {
  const { summary, getMetricProgress, loading } = useUsage();

  if (loading || !summary) return null;

  const metricsToCheck = ["backtest_runs", "content_generation_tokens", "marketplace_plugins", "iot_actions"];
  const exceededList: string[] = [];
  const warningList: string[] = [];

  metricsToCheck.forEach((key) => {
    const status = getMetricProgress(key);
    const label = key.replace(/_/g, " ");
    if (status.exceeded) {
      exceededList.push(label);
    } else if (status.warning) {
      warningList.push(label);
    }
  });

  if (exceededList.length === 0 && warningList.length === 0) {
    return null;
  }

  return (
    <div className="w-full flex flex-col gap-2">
      {exceededList.length > 0 && (
        <div className="p-4 rounded-xl border border-rose-500/20 bg-rose-500/10 text-rose-400 text-sm flex items-center justify-between shadow-lg shadow-rose-950/10">
          <div className="flex items-center gap-3">
            <span className="text-xl">❌</span>
            <div>
              <span className="font-bold">Quota Exceeded!</span> You have reached limits for{" "}
              <span className="font-semibold capitalize">{exceededList.join(", ")}</span>. Operations in these categories are currently blocked.
            </div>
          </div>
          <a
            href="/billing"
            className="px-3.5 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs transition duration-150 border border-rose-500/30"
          >
            Upgrade Plan
          </a>
        </div>
      )}

      {warningList.length > 0 && exceededList.length === 0 && (
        <div className="p-4 rounded-xl border border-amber-500/20 bg-amber-500/10 text-amber-400 text-sm flex items-center justify-between shadow-lg shadow-amber-950/10">
          <div className="flex items-center gap-3">
            <span className="text-xl">⚠</span>
            <div>
              <span className="font-bold">Usage Warning:</span> You are approaching limits (&gt;80%) for{" "}
              <span className="font-semibold capitalize">{warningList.join(", ")}</span>. Upgrading your plan is recommended.
            </div>
          </div>
          <a
            href="/billing"
            className="px-3.5 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs transition duration-150 border border-amber-500/30"
          >
            View Billing
          </a>
        </div>
      )}
    </div>
  );
}
export default QuotaBanner;
