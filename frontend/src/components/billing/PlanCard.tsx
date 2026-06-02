import React from "react";
import { BillingPlan } from "../../api/types";
import { useT } from "../../hooks/useT";

interface PlanCardProps {
  plan: BillingPlan;
  isCurrent: boolean;
  isMock: boolean;
  onSelect: (planId: string) => void;
  onApplyMock: (planTier: string) => void;
}

function formatLimit(value: unknown): string {
  if (value === undefined || value === null) return "N/A";
  if (value === 999999 || value === "unlimited") return "Unlimited";
  if (typeof value === "number") return value.toLocaleString();
  if (typeof value === "boolean") return value ? "Yes" : "No";
  return String(value);
}

function limit(plan: BillingPlan, ...keys: string[]): unknown {
  const limits = plan.limits ?? {};
  for (const key of keys) {
    if (Object.prototype.hasOwnProperty.call(limits, key)) {
      return (limits as Record<string, unknown>)[key];
    }
  }
  return undefined;
}

export function PlanCard({ plan, isCurrent, isMock, onSelect, onApplyMock }: PlanCardProps) {
  const { t } = useT();
  const priceMonthly = typeof plan.price_monthly === "number" ? plan.price_monthly : 0;
  const features = Array.isArray(plan.features) ? plan.features : [];

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
            <h4 className="text-xl font-bold capitalize text-white">{plan.name ?? plan.tier ?? t('billing.plan')}</h4>
            <p className="text-sm text-neutral-400 mt-1">{plan.description ?? t('billing.subscription_plan')}</p>
          </div>
          {isCurrent && (
            <span className="px-2.5 py-1 text-xs font-semibold text-violet-400 bg-violet-500/10 rounded-full border border-violet-500/20">
              {t('billing.active_plan_badge')}
            </span>
          )}
        </div>

        <div className="my-6">
          <span className="text-4xl font-extrabold text-white">${priceMonthly.toLocaleString()}</span>
          <span className="text-neutral-500 ml-1">{t('billing.per_month')}</span>
        </div>

        <div className="space-y-4 mb-8">
          <div className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">{t('billing.limits')}</div>
          <ul className="text-sm space-y-2 text-neutral-300">
            <li>• Backtests: {formatLimit(limit(plan, "backtest_runs", "backtests_per_month"))}</li>
            <li>• Content Items: {formatLimit(limit(plan, "content_generation_tokens", "content_items_per_month"))}</li>
            <li>• Marketplace Plugins: {formatLimit(limit(plan, "marketplace_plugins"))}</li>
            <li>• IoT Actions: {formatLimit(limit(plan, "iot_actions", "scheduler_jobs"))}</li>
          </ul>

          <div className="border-t border-neutral-800/80 my-4" />

          <div className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">{t('billing.features')}</div>
          <ul className="text-sm space-y-2 text-neutral-300">
            {features.map((feature, idx) => (
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
            {t('billing.current_plan_btn')}
          </button>
        ) : (
          <button
            onClick={() => onSelect(plan.id)}
            className="w-full py-2.5 px-4 rounded-lg bg-violet-600 hover:bg-violet-500 active:bg-violet-700 text-white font-medium text-sm transition duration-200 border border-violet-500/20"
          >
            {t('billing.upgrade_plan')}
          </button>
        )}

        {isMock && !isCurrent && (
          <button
            onClick={() => onApplyMock(plan.tier)}
            className="w-full py-1.5 px-3 rounded-lg bg-neutral-900 hover:bg-neutral-850 text-neutral-300 border border-neutral-800 hover:border-neutral-700 text-xs font-medium transition duration-200"
          >
            {t('billing.apply_mock_plan', { tier: plan.tier })}
          </button>
        )}
      </div>
    </div>
  );
}
