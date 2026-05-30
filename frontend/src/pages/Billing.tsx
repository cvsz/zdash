import React from "react";
import { useBilling } from "../hooks/useBilling";
import { SubscriptionStatusCard } from "../components/billing/SubscriptionStatusCard";
import { PlanCard } from "../components/billing/PlanCard";
import { PricingTable } from "../components/billing/PricingTable";
import { InvoiceTable } from "../components/billing/InvoiceTable";

export default function Billing() {
  const { status, plans, invoices, loading, error, checkout, portal, cancel, applyMock } = useBilling();

  const handleSelectPlan = async (planId: string) => {
    try {
      await checkout(planId);
    } catch (err) {
      // Handled inside hook
    }
  };

  const handleApplyMockPlan = async (planTier: string) => {
    try {
      await applyMock(planTier);
    } catch (err) {
      // Handled inside hook
    }
  };

  const isMock = status?.provider === "mock";

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8 text-white">
      <div>
        <h2 className="text-3xl font-extrabold mb-2 tracking-tight">SaaS Subscription & Billing</h2>
        <p className="text-neutral-400">Manage subscription, upgrades, usage credits, and invoice receipts history.</p>
      </div>

      {error && (
        <div className="p-4 bg-state-danger/10 border border-state-danger/20 text-state-danger rounded-xl text-sm font-semibold">
          Error: {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-6">
          <div className="h-40 bg-neutral-900/50 rounded-xl animate-pulse" />
          <div className="h-64 bg-neutral-900/50 rounded-xl animate-pulse" />
        </div>
      ) : (
        <>
          {/* Subscription Status details */}
          <section className="space-y-4">
            <h3 className="text-lg font-bold text-neutral-300">Active Plan Status</h3>
            <SubscriptionStatusCard
              status={status}
              onCancel={cancel}
              onPortal={portal}
              isMock={isMock}
            />
          </section>

          {/* Plan Catalog list */}
          <section className="space-y-4">
            <h3 className="text-lg font-bold text-neutral-300">Select Available Plan</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {plans.map((p) => (
                <PlanCard
                  key={p.id}
                  plan={p}
                  isCurrent={status?.plan_tier === p.tier}
                  isMock={isMock}
                  onSelect={handleSelectPlan}
                  onApplyMock={handleApplyMockPlan}
                />
              ))}
            </div>
          </section>

          {/* Feature Matrix */}
          <section className="space-y-4">
            <h3 className="text-lg font-bold text-neutral-300">Plan Comparison Matrix</h3>
            <PricingTable
              plans={plans}
              currentTier={status?.plan_tier || "free"}
              onSelect={handleSelectPlan}
            />
          </section>

          {/* Invoices table logs */}
          <section className="space-y-4">
            <h3 className="text-lg font-bold text-neutral-300">Invoice History Logs</h3>
            <InvoiceTable invoices={invoices} />
          </section>
        </>
      )}
    </div>
  );
}
export { Billing };
