import { useState, useEffect } from "react";
import { getUsageSummary } from "../api/endpoints";
import { UsageSummary } from "../api/types";

export function useUsage() {
  const [summary, setSummary] = useState<UsageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUsage = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getUsageSummary();
      setSummary(res);
    } catch (err: any) {
      setError(err.message || "Failed to load usage data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsage();
  }, []);

  const getMetricProgress = (key: string) => {
    if (!summary || !summary.metrics || !summary.metrics[key]) {
      return { usage: 0, limit: 0, percent: 0, warning: false, exceeded: false };
    }
    const metric = summary.metrics[key]!;
    const percent = metric.limit > 0 ? (metric.usage / metric.limit) * 100 : 0;
    return {
      usage: metric.usage,
      limit: metric.limit,
      percent,
      warning: percent >= 80,
      exceeded: metric.usage >= metric.limit,
    };
  };

  return {
    summary,
    loading,
    error,
    getMetricProgress,
    refetch: fetchUsage,
  };
}
