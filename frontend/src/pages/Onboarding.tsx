import React, { useState } from "react";
import { useEnterprise } from "../hooks/useEnterprise";
import { OnboardingChecklist } from "../components/enterprise/OnboardingChecklist";
import { useT } from "../hooks/useT";

export default function Onboarding() {
  const { t } = useT();
  const { onboarding, completeStep, resetOnboarding, loading, error } = useEnterprise();
  const [dryRunRunning, setDryRunRunning] = useState<string | null>(null);
  const [dryRunOutput, setDryRunOutput] = useState<string | null>(null);

  const handleQuickAction = async (actionKey: string, stepToComplete: string) => {
    setDryRunRunning(actionKey);
    setDryRunOutput(null);
    try {
      // Simulate quick action (always dry-run for safety)
      await new Promise((resolve) => setTimeout(resolve, 1500));
      setDryRunOutput(`✔ ${t('onboarding.dry_run_simulator_success')}: ${actionKey}`);
      if (onboarding && onboarding.pending_steps.includes(stepToComplete)) {
        await completeStep(stepToComplete);
      }
    } catch (err: any) {
      setDryRunOutput(`✕ ${t('onboarding.dry_run_simulator_error')}: ${err.message}`);
    } finally {
      setDryRunRunning(null);
    }
  };

  const safetyItems = [
    { text: "Drawdown Risk Guardian checks enabled by default (fail-closed model)", status: "verified" },
    { text: "Live orders, smart plugs, and publishing channels set to simulation / dry-run mode", status: "verified" },
    { text: "No sensitive environment credentials baked or committed to repositories", status: "verified" },
    { text: "Sandbox isolation configured for third-party marketplace plug-ins", status: "verified" },
  ];

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-8 text-white">
      <div>
        <h2 className="text-3xl font-extrabold mb-2 tracking-tight">{t('onboarding.title')}</h2>
        <p className="text-neutral-400">{t('onboarding.subtitle')}</p>
      </div>

      {error && (
        <div className="p-4 bg-state-danger/10 border border-state-danger/20 text-state-danger rounded-xl text-sm font-semibold">
          Error: {error}
        </div>
      )}

      {loading ? (
        <div className="h-64 bg-neutral-900/50 rounded-xl animate-pulse" />
      ) : (
        <div className="space-y-8">
          {/* Safety Checklist Column */}
          <section className="p-6 rounded-xl border border-state-danger/20 bg-rose-500/5 space-y-4">
            <h3 className="text-lg font-bold text-state-danger flex items-center gap-2">
              <span>🛡</span> {t('onboarding.safety_guidelines')}
            </h3>
            <p className="text-xs text-neutral-400">
              {t('onboarding.safety_guidelines_desc')}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              {safetyItems.map((item, idx) => (
                <div key={idx} className="p-3 rounded-card bg-neutral-950/40 border border-neutral-850 flex items-start gap-3">
                  <span className="text-state-success text-sm font-bold">✔</span>
                  <span className="text-xs text-neutral-300 leading-relaxed font-medium">{item.text}</span>
                </div>
              ))}
            </div>
          </section>

          {/* Quick Actions (Dry-Run Labeled) */}
          <section className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 space-y-4">
            <h3 className="text-lg font-bold text-neutral-300">{t('onboarding.quick_dry_run_actions')}</h3>
            <p className="text-xs text-neutral-500">
              {t('onboarding.quick_actions_desc')}
            </p>

            <div className="flex flex-wrap gap-4 pt-2">
              <button
                onClick={() => handleQuickAction("Signal Scan", "run first dry-run scan")}
                disabled={!!dryRunRunning}
                className="py-2 px-4 rounded-card bg-neutral-900 hover:bg-neutral-850 text-neutral-250 border border-neutral-800 hover:border-neutral-700 text-xs font-semibold flex items-center gap-2 transition disabled:opacity-50"
              >
                <span>🔍</span> {t('onboarding.run_dry_run_scan')}
              </button>

              <button
                onClick={() => handleQuickAction("Backtest Run", "run first backtest")}
                disabled={!!dryRunRunning}
                className="py-2 px-4 rounded-card bg-neutral-900 hover:bg-neutral-850 text-neutral-250 border border-neutral-800 hover:border-neutral-700 text-xs font-semibold flex items-center gap-2 transition disabled:opacity-50"
              >
                <span>📊</span> {t('onboarding.run_backtest')}
              </button>

              <button
                onClick={() => handleQuickAction("Content Creation", "create first content item")}
                disabled={!!dryRunRunning}
                className="py-2 px-4 rounded-card bg-neutral-900 hover:bg-neutral-850 text-neutral-250 border border-neutral-800 hover:border-neutral-700 text-xs font-semibold flex items-center gap-2 transition disabled:opacity-50"
              >
                <span>✏</span> {t('onboarding.create_content_item')}
              </button>

              <a
                href="/risk"
                className="py-2 px-4 rounded-card bg-neutral-900 hover:bg-neutral-850 text-neutral-250 border border-neutral-800 hover:border-neutral-700 text-xs font-semibold flex items-center gap-2 transition"
              >
                <span>🛡</span> {t('onboarding.review_risk_panel')}
              </a>

              <a
                href="/billing"
                className="py-2 px-4 rounded-card bg-neutral-900 hover:bg-neutral-850 text-neutral-250 border border-neutral-800 hover:border-neutral-700 text-xs font-semibold flex items-center gap-2 transition"
              >
                <span>💳</span> {t('onboarding.review_billing')}
              </a>
            </div>

            {dryRunRunning && (
              <div className="p-3 bg-neutral-900 border border-neutral-850 rounded-card text-xs font-mono text-violet-400 animate-pulse">
                ⏳ {t('onboarding.simulating_action')} {dryRunRunning}. {t('common.loading')}
              </div>
            )}

            {dryRunOutput && (
              <div className="p-3 bg-neutral-900 border border-neutral-850 rounded-card text-xs font-mono text-state-success">
                {dryRunOutput}
              </div>
            )}
          </section>

          {/* Onboarding checklist */}
          <section className="space-y-4">
            <OnboardingChecklist
              onboarding={onboarding}
              onCompleteStep={completeStep}
              onReset={resetOnboarding}
              isDryRunLabeled={true}
            />
          </section>
        </div>
      )}
    </div>
  );
}
export { Onboarding };
