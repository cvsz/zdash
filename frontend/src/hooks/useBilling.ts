import { useState, useEffect } from "react";
import {
  getBillingStatus,
  getBillingPlans,
  getInvoices,
  startCheckout,
  openBillingPortal,
  cancelSubscription,
  applyMockPlan as apiApplyMockPlan,
} from "../api/endpoints";
import { BillingStatus, BillingPlan, Invoice } from "../api/types";

export function useBilling() {
  const [status, setStatus] = useState<BillingStatus | null>(null);
  const [plans, setPlans] = useState<BillingPlan[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = async () => {
    try {
      setLoading(true);
      setError(null);
      const [statusRes, plansRes, invoicesRes] = await Promise.all([
        getBillingStatus(),
        getBillingPlans(),
        getInvoices(),
      ]);
      setStatus(statusRes);
      setPlans(plansRes);
      setInvoices(invoicesRes);
    } catch (err: any) {
      setError(err.message || "Failed to load billing details");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const checkout = async (planId: string) => {
    setError(null);
    try {
      const res = await startCheckout(planId);
      if (res.checkout_url) {
        window.location.href = res.checkout_url;
      }
      return res;
    } catch (err: any) {
      setError(err.message || "Checkout failed");
      throw err;
    }
  };

  const portal = async () => {
    setError(null);
    try {
      const res = await openBillingPortal();
      if (res.portal_url) {
        window.location.href = res.portal_url;
      }
      return res;
    } catch (err: any) {
      setError(err.message || "Failed to open billing portal");
      throw err;
    }
  };

  const cancel = async () => {
    setError(null);
    try {
      const res = await cancelSubscription();
      await fetchAll();
      return res;
    } catch (err: any) {
      setError(err.message || "Subscription cancel failed");
      throw err;
    }
  };

  const applyMock = async (planTier: string) => {
    setError(null);
    try {
      const res = await apiApplyMockPlan(planTier);
      await fetchAll();
      return res;
    } catch (err: any) {
      setError(err.message || "Applying mock plan failed");
      throw err;
    }
  };

  return {
    status,
    plans,
    invoices,
    loading,
    error,
    checkout,
    portal,
    cancel,
    applyMock,
    refetch: fetchAll,
  };
}
