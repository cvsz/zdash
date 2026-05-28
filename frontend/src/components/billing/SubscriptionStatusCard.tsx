import React from "react";
import { BillingStatus } from "../../api/types";

interface SubscriptionStatusCardProps {
  status: BillingStatus | null;
  onCancel: () => void;
  onPortal: () => void;
  isMock: boolean;
}

export function SubscriptionStatusCard({ status, onCancel, onPortal, isMock }: SubscriptionStatusCardProps) {
  if (!status) {
    return (
      <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 animate-pulse flex flex-col gap-3">
        <div className="h-6 w-1/3 bg-neutral-800 rounded" />
        <div className="h-4 w-2/3 bg-neutral-800 rounded" />
      </div>
    );
  }

  const isGrace = status.status === "past_due" || !!status.grace_period_ends_at;

  return (
    <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 flex flex-col gap-6">
      {/* Mock Billing Banner */}
      {isMock && (
        <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg flex items-center gap-2 text-amber-400 text-sm">
          <span className="text-base">⚠</span>
          <div>
            <span className="font-bold">Mock Billing Mode:</span> Payments and portal endpoints are simulated. No real charges are made.
          </div>
        </div>
      )}

      {/* Subscription Status details */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">Current Plan</div>
          <h4 className="text-2xl font-extrabold text-white mt-1 capitalize">{status.plan_tier} Plan</h4>
          <p className="text-sm text-neutral-400 mt-0.5">
            Provider: <span className="font-mono text-xs uppercase bg-neutral-850 px-1.5 py-0.5 rounded text-neutral-300">{status.provider}</span>
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <span
            className={`px-3 py-1 text-xs font-semibold rounded-full border ${
              status.status === "active" || status.status === "trialing"
                ? "text-green-400 bg-green-500/10 border-green-500/20"
                : isGrace
                ? "text-amber-400 bg-amber-500/10 border-amber-500/20"
                : "text-neutral-400 bg-neutral-500/10 border-neutral-500/20"
            }`}
          >
            Status: <span className="capitalize">{status.status.replace("_", " ")}</span>
          </span>

          {status.cancel_at_period_end && (
            <span className="px-3 py-1 text-xs font-semibold rounded-full text-amber-500 bg-amber-500/10 border border-amber-500/20">
              Canceling at period end
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 border-t border-b border-neutral-800/60 py-4 text-sm text-neutral-300">
        <div>
          <span className="text-neutral-500 block text-xs uppercase tracking-wider font-semibold">Current Period Ends</span>
          <span className="font-medium mt-1 block">
            {status.current_period_end ? new Date(status.current_period_end).toLocaleDateString() : "N/A"}
          </span>
        </div>

        {status.trial_ends_at && (
          <div>
            <span className="text-neutral-500 block text-xs uppercase tracking-wider font-semibold">Trial Expiration</span>
            <span className="font-medium mt-1 block text-violet-400">
              {new Date(status.trial_ends_at).toLocaleDateString()}
            </span>
          </div>
        )}

        {isGrace && (
          <div>
            <span className="text-amber-500 block text-xs uppercase tracking-wider font-semibold">Grace Period / Past Due</span>
            <span className="font-medium mt-1 block text-amber-400">
              Ends: {status.grace_period_ends_at ? new Date(status.grace_period_ends_at).toLocaleDateString() : "N/A"}
            </span>
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-4 pt-2">
        <button
          onClick={onPortal}
          className="py-2 px-4 rounded-lg bg-neutral-900 hover:bg-neutral-850 text-neutral-200 border border-neutral-800 hover:border-neutral-700 text-sm font-semibold transition duration-150"
        >
          Open Billing Portal
        </button>

        {status.status !== "canceled" && !status.cancel_at_period_end && (
          <button
            onClick={onCancel}
            className="py-2 px-4 rounded-lg bg-rose-950/20 hover:bg-rose-950/40 text-rose-400 border border-rose-900/30 hover:border-rose-900/50 text-sm font-semibold transition duration-150"
          >
            Cancel Subscription
          </button>
        )}
      </div>
    </div>
  );
}
