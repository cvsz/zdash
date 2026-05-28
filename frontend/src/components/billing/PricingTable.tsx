import React from "react";
import { BillingPlan } from "../../api/types";

interface PricingTableProps {
  plans: BillingPlan[];
  currentTier: string;
  onSelect: (planId: string) => void;
}

export function PricingTable({ plans, currentTier, onSelect }: PricingTableProps) {
  const comparisonFeatures = [
    { name: "Backtest Run Limits", key: "backtest_runs", isLimit: true },
    { name: "AI Token Quota", key: "content_generation_tokens", isLimit: true },
    { name: "Max Plug-ins", key: "marketplace_plugins", isLimit: true },
    { name: "IoT Controls", key: "iot_actions", isLimit: true },
    { name: "Advanced Signal Scan", tierRequired: "pro" },
    { name: "Guardian Drawdown Guard", tierRequired: "pro" },
    { name: "Audit Logging & Exports", tierRequired: "enterprise" },
    { name: "White-Label Domain Support", tierRequired: "enterprise" },
  ];

  const checkFeature = (plan: BillingPlan, item: any) => {
    if (item.isLimit) {
      const val = plan.limits[item.key];
      return val === 999999 ? "Unlimited" : val.toLocaleString();
    }
    const tiers = ["free", "starter", "pro", "enterprise"];
    const planIndex = tiers.indexOf(plan.tier);
    const reqIndex = tiers.indexOf(item.tierRequired);
    return planIndex >= reqIndex ? "✔" : "✘";
  };

  return (
    <div className="w-full overflow-x-auto rounded-xl border border-neutral-800 bg-neutral-950/20">
      <table className="w-full text-left border-collapse min-w-[600px]">
        <thead>
          <tr className="border-b border-neutral-800 bg-neutral-900/30">
            <th className="p-4 text-sm font-semibold text-neutral-400">Features</th>
            {plans.map((p) => (
              <th key={p.id} className="p-4 text-sm font-bold text-white capitalize text-center">
                {p.name}
                <div className="text-xs font-normal text-neutral-500 mt-1">${p.price_monthly}/mo</div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-neutral-850">
          {comparisonFeatures.map((item, idx) => (
            <tr key={idx} className="hover:bg-neutral-900/10">
              <td className="p-4 text-sm font-medium text-neutral-300">{item.name}</td>
              {plans.map((p) => {
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
            <td className="p-4 text-sm font-semibold text-neutral-400">Action</td>
            {plans.map((p) => (
              <td key={p.id} className="p-4 text-center">
                {p.tier === currentTier ? (
                  <span className="text-xs font-semibold text-violet-400 px-3 py-1 bg-violet-500/10 rounded-full border border-violet-500/20">
                    Active
                  </span>
                ) : (
                  <button
                    onClick={() => onSelect(p.id)}
                    className="px-4 py-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 text-neutral-200 border border-neutral-850 hover:border-neutral-700 text-xs font-medium transition duration-150"
                  >
                    Select
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
