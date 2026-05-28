import React from "react";
import { PlanCards } from "../components/billing/PlanCards";
import { UsageMeter } from "../components/billing/UsageMeter";
import { InvoiceHistory } from "../components/billing/InvoiceHistory";

export default function Billing() {
  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-bold mb-2">Billing & Plans</h2>
        <p className="text-neutral-400">Manage your subscription, usage, and invoices.</p>
      </div>

      <section>
        <h3 className="text-xl font-semibold mb-4">Available Plans</h3>
        <PlanCards />
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <section>
          <h3 className="text-xl font-semibold mb-4">Current Usage</h3>
          <UsageMeter />
        </section>

        <section>
          <h3 className="text-xl font-semibold mb-4">Invoice History</h3>
          <InvoiceHistory />
        </section>
      </div>
    </div>
  );
}
