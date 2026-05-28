import React from "react";
import { BillingPlan } from "../../api/types";

interface PlanCardProps {
  plan: BillingPlan;
  isCurrent: boolean;
  isMock: boolean;
  onSelect: (planId: string) => void;
  onApplyMock: (planTier: string) => void;
}

export function PlanCard({ plan, isCurrent, isMock, onSelect, onApplyMock }: PlanCardProps) {
  return (
    <div
      className={`p-6 rounded-xl border flex flex-col justify-between transition-all duration-300 ${
        isCurrent
          ? "border-violet-500 bg-neutral-900/60 shadow-lg shadow-violet-500/10 scale-102"
          : "border-neutral-800 bg-neutral-950/40 hover:border-neutral-700"
      }`}
    >
      <div>
        <div className="flex justify-between items-start mb-4">
          <div>
            <h4 className="text-xl font-bold capitalize text-white">{plan.name}</h4>
            <p className="text-sm text-neutral-400 mt-1">{plan.description}</p>
          </div>
          {isCurrent && (
            <span className="px-2.5 py-1 text-xs font-semibold text-violet-400 bg-violet-500/10 rounded-full border border-violet-500/20">
              Active Plan
            </span>
          )}
        </div>

        <div className="my-6">
          <span className="text-4xl font-extrabold text-white">${plan.price_monthly}</span>
          <span className="text-neutral-500 ml-1">/ month</span>
        </div>

        <div className="space-y-4 mb-8">
          <div className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">Limits</div>
          <ul className="text-sm space-y-2 text-neutral-300">
            <li>• Backtests: {plan.limits.backtest_runs === 999999 ? "Unlimited" : plan.limits.backtest_runs}</li>
            <li>• AI Tokens: {plan.limits.content_generation_tokens === 999999 ? "Unlimited" : plan.limits.content_generation_tokens.toLocaleString()}</li>
            <li>• Marketplace Plugins: {plan.limits.marketplace_plugins === 999999 ? "Unlimited" : plan.limits.marketplace_plugins}</li>
            <li>• IoT Actions: {plan.limits.iot_actions === 999999 ? "Unlimited" : plan.limits.iot_actions}</li>
          </ul>

          <div className="border-t border-neutral-800/80 my-4" />

          <div className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">Features</div>
          <ul className="text-sm space-y-2 text-neutral-300">
            {plan.features.map((feature, idx) => (
              <li key={idx} className="flex items-center gap-2">
                <span className="text-violet-400 text-xs">✔</span>
                <span>{feature}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="space-y-2 pt-4">
        {isCurrent ? (
          <button
            disabled
            className="w-full py-2.5 px-4 rounded-lg bg-neutral-800 text-neutral-500 font-medium text-sm cursor-not-allowed border border-neutral-700/50"
          >
            Current Plan
          </button>
        ) : (
          <button
            onClick={() => onSelect(plan.id)}
            className="w-full py-2.5 px-4 rounded-lg bg-violet-600 hover:bg-violet-500 active:bg-violet-700 text-white font-medium text-sm transition duration-200 border border-violet-500/20"
          >
            Upgrade Plan
          </button>
        )}

        {isMock && !isCurrent && (
          <button
            onClick={() => onApplyMock(plan.tier)}
            className="w-full py-1.5 px-3 rounded-lg bg-neutral-900 hover:bg-neutral-850 text-neutral-300 border border-neutral-800 hover:border-neutral-700 text-xs font-medium transition duration-200"
          >
            Apply Mock Plan ({plan.tier})
          </button>
        )}
      </div>
    </div>
  );
}
