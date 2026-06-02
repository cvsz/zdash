import React from "react";
import { BillingPlan } from "../../api/types";
import { useT } from "../../hooks/useT";

interface PricingTableProps {
  plans: BillingPlan[];
  currentTier: string;
  onSelect: (planId: string) => void;
}

type ComparisonItem = {
  name: string;
  keys?: string[];
  tierRequired?: string;
  isLimit?: boolean;
};

function formatLimit(value: unknown): string {
  if (value === undefined || value === null) return "N/A";
  if (value === 999999 || value === "unlimited") return "Unlimited";
  if (typeof value === "number") return value.toLocaleString();
  if (typeof value === "boolean") return value ? "Yes" : "No";
  return String(value);
}

function getLimit(plan: BillingPlan, keys: string[] = []): unknown {
  const limits = plan.limits ?? {};
  for (const key of keys) {
    if (Object.prototype.hasOwnProperty.call(limits, key)) {
      return (limits as Record<string, unknown>)[key];
    }
  }
  return undefined;
}

export function PricingTable({ plans, currentTier, onSelect }: PricingTableProps) {
  const { t } = useT();
  const safePlans = Array.isArray(plans) ? plans : [];

  const comparisonFeatures: ComparisonItem[] = [
    { name: t('billing.feature_backtest'), keys: ["backtest_runs", "backtests_per_month"], isLimit: true },
    { name: t('billing.feature_content'), keys: ["content_generation_tokens", "content_items_per_month"], isLimit: true },
    { name: t('billing.feature_plugins'), keys: ["marketplace_plugins"], isLimit: true },
    { name: t('billing.feature_iot'), keys: ["iot_actions", "scheduler_jobs"], isLimit: true },
    { name: t('billing.feature_signal_scan'), tierRequired: "pro" },
    { name: t('billing.feature_drawdown_guard'), tierRequired: "pro" },
    { name: t('billing.feature_audit'), tierRequired: "enterprise" },
    { name: t('billing.feature_whitelabel'), tierRequired: "enterprise" },
  ];

  const checkFeature = (plan: BillingPlan, item: ComparisonItem) => {
    if (item.isLimit) {
      return formatLimit(getLimit(plan, item.keys));
    }

    const tiers = ["free", "starter", "pro", "enterprise"];
    const planIndex = tiers.indexOf(plan.tier);
    const reqIndex = tiers.indexOf(item.tierRequired ?? "enterprise");

    return planIndex >= reqIndex ? "✔" : "✘";
  };

  return (
    <div className="w-full overflow-x-auto rounded-xl border border-neutral-800 bg-neutral-950/20">
      <table className="w-full text-left border-collapse min-w-[600px]">
        <thead>
          <tr className="border-b border-neutral-800 bg-neutral-900/30">
            <th className="p-4 text-sm font-semibold text-neutral-400">{t('billing.features_header')}</th>
            {safePlans.map((p) => (
              <th key={p.id} className="p-4 text-sm font-bold text-white capitalize text-center">
                {p.name ?? p.tier}
                <div className="text-xs font-normal text-neutral-500 mt-1">
                  ${typeof p.price_monthly === "number" ? p.price_monthly.toLocaleString() : "0"}/mo
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-neutral-850">
          {comparisonFeatures.map((item, idx) => (
            <tr key={idx} className="hover:bg-neutral-900/10">
              <td className="p-4 text-sm font-medium text-neutral-300">{item.name}</td>
              {safePlans.map((p) => {
                const res = checkFeature(p, item);
                return (
                  <td
                    key={p.id}
                    className={`p-4 text-sm text-center font-medium ${
                      res === "✔" ? "text-green-400" : res === "✘" ? "text-neutral-600" : "text-neutral-300"
                    }`}
                  >
                    {res}
                  </td>
                );
              })}
            </tr>
          ))}
          <tr className="bg-neutral-900/10">
            <td className="p-4 text-sm font-semibold text-neutral-400">{t('billing.action_header')}</td>
            {safePlans.map((p) => (
              <td key={p.id} className="p-4 text-center">
                {p.tier === currentTier ? (
                  <span className="text-xs font-semibold text-violet-400 px-3 py-1 bg-violet-500/10 rounded-full border border-violet-500/20">
                    {t('billing.active')}
                  </span>
                ) : (
                  <button
                    onClick={() => onSelect(p.id)}
                    className="px-4 py-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 text-neutral-200 border border-neutral-850 hover:border-neutral-700 text-xs font-medium transition duration-150"
                  >
                    {t('billing.select')}
                  </button>
                )}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}
