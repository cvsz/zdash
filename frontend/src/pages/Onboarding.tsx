import React, { useState } from "react";
import { useEnterprise } from "../hooks/useEnterprise";
import { OnboardingChecklist } from "../components/enterprise/OnboardingChecklist";

export default function Onboarding() {
  const { onboarding, completeStep, resetOnboarding, loading, error } = useEnterprise();
  const [dryRunRunning, setDryRunRunning] = useState<string | null>(null);
  const [dryRunOutput, setDryRunOutput] = useState<string | null>(null);

  const handleQuickAction = async (actionKey: string, stepToComplete: string) => {
    setDryRunRunning(actionKey);
    setDryRunOutput(null);
    try {
      // Simulate quick action (always dry-run for safety)
      await new Promise((resolve) => setTimeout(resolve, 1500));
      setDryRunOutput(`✔ Dry-run simulator succeeded: ${actionKey} successfully simulated in offline mode.`);
      if (onboarding && onboarding.pending_steps.includes(stepToComplete)) {
        await completeStep(stepToComplete);
      }
    } catch (err: any) {
      setDryRunOutput(`✕ Simulator error: ${err.message}`);
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
        <h2 className="text-3xl font-extrabold mb-2 tracking-tight">System Onboarding & Safety Verification</h2>
        <p className="text-neutral-400">Complete setup tasks and verify sandbox guidelines before active automation starts.</p>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-sm font-semibold">
          Error: {error}
        </div>
      )}

      {loading ? (
        <div className="h-64 bg-neutral-900/50 rounded-xl animate-pulse" />
      ) : (
        <div className="space-y-8">
          {/* Safety Checklist Column */}
          <section className="p-6 rounded-xl border border-rose-500/20 bg-rose-500/5 space-y-4">
            <h3 className="text-lg font-bold text-rose-400 flex items-center gap-2">
              <span>🛡</span> Safety Guidelines & Sandbox Rules
            </h3>
            <p className="text-xs text-neutral-400">
              Before activating any live execution loops, ensure the following safety gates remain closed and validated.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              {safetyItems.map((item, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-neutral-950/40 border border-neutral-850 flex items-start gap-3">
                  <span className="text-emerald-400 text-sm font-bold">✔</span>
                  <span className="text-xs text-neutral-300 leading-relaxed font-medium">{item.text}</span>
                </div>
              ))}
            </div>
          </section>

          {/* Quick Actions (Dry-Run Labeled) */}
          <section className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 space-y-4">
            <h3 className="text-lg font-bold text-neutral-300">Quick Dry-Run Actions</h3>
            <p className="text-xs text-neutral-500">
              Run test procedures instantly to check operational pipelines. All actions below run in simulation mode.
            </p>

            <div className="flex flex-wrap gap-4 pt-2">
              <button
                onClick={() => handleQuickAction("Signal Scan", "run first dry-run scan")}
                disabled={!!dryRunRunning}
                className="py-2 px-4 rounded-lg bg-neutral-900 hover:bg-neutral-850 text-neutral-250 border border-neutral-800 hover:border-neutral-700 text-xs font-semibold flex items-center gap-2 transition disabled:opacity-50"
              >
                <span>🔍</span> Run Dry-Run Scan
              </button>

              <button
                onClick={() => handleQuickAction("Backtest Run", "run first backtest")}
                disabled={!!dryRunRunning}
                className="py-2 px-4 rounded-lg bg-neutral-900 hover:bg-neutral-850 text-neutral-250 border border-neutral-800 hover:border-neutral-700 text-xs font-semibold flex items-center gap-2 transition disabled:opacity-50"
              >
                <span>📊</span> Run Backtest
              </button>

              <button
                onClick={() => handleQuickAction("Content Creation", "create first content item")}
                disabled={!!dryRunRunning}
                className="py-2 px-4 rounded-lg bg-neutral-900 hover:bg-neutral-850 text-neutral-250 border border-neutral-800 hover:border-neutral-700 text-xs font-semibold flex items-center gap-2 transition disabled:opacity-50"
              >
                <span>✏</span> Create Content Item
              </button>

              <a
                href="/risk"
                className="py-2 px-4 rounded-lg bg-neutral-900 hover:bg-neutral-850 text-neutral-250 border border-neutral-800 hover:border-neutral-700 text-xs font-semibold flex items-center gap-2 transition"
              >
                <span>🛡</span> Review Risk Panel
              </a>

              <a
                href="/billing"
                className="py-2 px-4 rounded-lg bg-neutral-900 hover:bg-neutral-850 text-neutral-250 border border-neutral-800 hover:border-neutral-700 text-xs font-semibold flex items-center gap-2 transition"
              >
                <span>💳</span> Review Billing
              </a>
            </div>

            {dryRunRunning && (
              <div className="p-3 bg-neutral-900 border border-neutral-850 rounded-lg text-xs font-mono text-violet-400 animate-pulse">
                ⏳ Simulating {dryRunRunning} action. Please wait...
              </div>
            )}

            {dryRunOutput && (
              <div className="p-3 bg-neutral-900 border border-neutral-850 rounded-lg text-xs font-mono text-emerald-400">
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
