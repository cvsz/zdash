import React from "react";

export function PlanCards() {
  const plans = [
    { name: "Free", price: "$0", features: ["Basic Analytics", "1 Workspace"] },
    { name: "Starter", price: "$49", features: ["Trading Scanner", "5 Workspaces", "Standard Support"] },
    { name: "Pro", price: "$199", features: ["Backtesting", "AI Analysis", "Priority Support"] },
    { name: "Enterprise", price: "Custom", features: ["SSO", "Dedicated Account Manager", "Custom Deployment"] },
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
            Select Plan
          </button>
        </div>
      ))}
    </div>
  );
}
