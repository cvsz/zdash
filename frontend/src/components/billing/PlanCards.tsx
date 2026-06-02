import React from "react";
import { useT } from "../../hooks/useT";

export function PlanCards() {
  const { t } = useT();
  const plans = [
    { name: t('billing.plan_free_name'), price: t('billing.plan_price_free'), features: [t('billing.feature_basic_analytics'), t('billing.feature_1_workspace')] },
    { name: t('billing.plan_starter_name'), price: t('billing.plan_price_starter'), features: [t('billing.feature_trading_scanner'), t('billing.feature_5_workspaces'), t('billing.feature_standard_support')] },
    { name: t('billing.plan_pro_name'), price: t('billing.plan_price_pro'), features: [t('billing.feature_backtesting'), t('billing.feature_ai_analysis'), t('billing.feature_priority_support')] },
    { name: t('billing.plan_enterprise_name'), price: t('billing.plan_price_enterprise'), features: [t('billing.feature_sso'), t('billing.feature_dedicated_manager'), t('billing.feature_custom_deployment')] },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {plans.map((plan) => (
        <div key={plan.name} className="border border-neutral-800 p-6 rounded bg-neutral-900">
          <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
          <p className="text-2xl font-semibold mb-4">{plan.price}</p>
          <ul className="text-sm text-neutral-400 mb-6 space-y-2">
            {plan.features.map((f) => (
              <li key={f}>- {f}</li>
            ))}
          </ul>
          <button className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded text-white font-medium">
            {t('billing.select_plan')}
          </button>
        </div>
      ))}
    </div>
  );
}
