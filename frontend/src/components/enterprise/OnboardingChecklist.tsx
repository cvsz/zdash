import React from "react";
import { OnboardingChecklist as OnboardingType } from "../../api/types";

interface OnboardingChecklistProps {
  onboarding: OnboardingType | null;
  onCompleteStep: (step: string) => Promise<any>;
  onReset: () => Promise<any>;
  isDryRunLabeled?: boolean;
}

export function OnboardingChecklist({
  onboarding,
  onCompleteStep,
  onReset,
  isDryRunLabeled = false,
}: OnboardingChecklistProps) {
  if (!onboarding) {
    return (
      <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 animate-pulse space-y-4">
        <div className="h-6 w-1/4 bg-neutral-800 rounded" />
        <div className="h-4 w-full bg-neutral-800 rounded animate-pulse" />
      </div>
    );
  }

  const handleToggle = async (step: string, isCompleted: boolean) => {
    if (isCompleted) return; // cannot uncheck via UI for safety audits logs
    try {
      await onCompleteStep(step);
    } catch (err) {
      // Ignored for presentation
    }
  };

  const allSteps = [...onboarding.completed_steps, ...onboarding.pending_steps];

  return (
    <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-4">
        <div>
          <h4 className="text-xl font-bold text-white">System Onboarding Checklist</h4>
          <p className="text-xs text-neutral-500 mt-1">Complete initial steps to activate production-grade modules.</p>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <span className="text-[10px] text-neutral-500 uppercase font-bold tracking-wider">Progress</span>
            <span className="text-lg font-extrabold text-white block">{onboarding.progress_percent}%</span>
          </div>

          <button
            onClick={onReset}
            className="px-3 py-1.5 bg-neutral-900 border border-neutral-800 hover:border-neutral-750 text-neutral-300 rounded text-xs font-semibold transition"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-neutral-900 rounded-full h-2 border border-neutral-850 overflow-hidden">
        <div
          className="h-full rounded-full bg-violet-600 transition-all duration-300"
          style={{ width: `${onboarding.progress_percent}%` }}
        />
      </div>

      {/* Steps List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {allSteps.map((step) => {
          const isCompleted = onboarding.completed_steps.includes(step);
          return (
            <div
              key={step}
              onClick={() => handleToggle(step, isCompleted)}
              className={`p-4 rounded-xl border transition duration-150 flex items-center gap-3 cursor-pointer ${
                isCompleted
                  ? "bg-violet-950/15 border-violet-900/35 text-neutral-450 hover:bg-violet-950/20"
                  : "bg-neutral-950/30 border-neutral-850 hover:border-neutral-750 text-white"
              }`}
            >
              <div
                className={`w-5 h-5 rounded-full flex items-center justify-center border text-xs shrink-0 ${
                  isCompleted
                    ? "bg-violet-600 border-violet-500 text-white font-bold"
                    : "border-neutral-700 bg-neutral-900 text-transparent"
                }`}
              >
                ✓
              </div>

              <div>
                <span className={`text-sm capitalize font-medium ${isCompleted ? "line-through text-neutral-500" : "text-neutral-200"}`}>
                  {step}
                </span>
                {isDryRunLabeled && step.includes("scan") && (
                  <span className="ml-2 px-1.5 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-400 text-[10px] uppercase font-bold tracking-wider">
                    Dry-Run Safe
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
export default OnboardingChecklist;
