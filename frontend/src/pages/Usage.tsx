import React from "react";
import { useUsage } from "../hooks/useUsage";
import { UsageMeterCard } from "../components/billing/UsageMeterCard";
import { useT } from "../hooks/useT";

export default function Usage() {
  const { t } = useT();
  const { summary, loading, error, getMetricProgress } = useUsage();

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-8 text-white">
      <div>
        <h2 className="text-3xl font-extrabold mb-2 tracking-tight">{t('usage.title')}</h2>
        <p className="text-neutral-400">{t('usage.subtitle')}</p>
      </div>

      {error && (
        <div className="p-4 bg-state-danger/10 border border-state-danger/20 text-state-danger rounded-xl text-sm font-semibold">
          {t('common.error')}: {error}
        </div>
      )}

      {loading ? (
        <div className="h-64 bg-neutral-900/50 rounded-xl animate-pulse" />
      ) : (
        <div className="space-y-6">
          <UsageMeterCard summary={summary} getMetricProgress={getMetricProgress} />

          <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 space-y-4">
            <h3 className="text-md font-bold text-neutral-300">{t('usage.understanding_quotas')}</h3>
            <p className="text-sm text-neutral-400 leading-relaxed">
              {t('usage.understanding_quotas_desc')}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
export { Usage };
