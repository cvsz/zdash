import React from "react";

export function OnboardingChecklist() {
  const steps = [
    { label: "Create organization", completed: true },
    { label: "Invite team", completed: true },
    { label: "Verify risk guardian", completed: false },
    { label: "Run first dry-run scan", completed: false },
    { label: "Configure billing", completed: false },
  ];

  const completedCount = steps.filter((s) => s.completed).length;
  const progress = (completedCount / steps.length) * 100;

  return (
    <div className="bg-neutral-900 border border-neutral-800 p-6 rounded">
      <h4 className="font-bold text-lg mb-2">Platform Onboarding</h4>
      <p className="text-sm text-neutral-400 mb-4">Complete these steps to unlock full value.</p>
      
      <div className="mb-6">
        <div className="flex justify-between text-sm mb-2">
          <span className="font-medium">Progress</span>
          <span className="text-neutral-400">{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-neutral-800 rounded-full h-2">
          <div
            className="bg-green-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      <div className="space-y-3">
        {steps.map((step, idx) => (
          <label key={idx} className={`flex items-center space-x-3 p-2 rounded hover:bg-neutral-800/50 cursor-pointer ${step.completed ? 'opacity-50' : ''}`}>
            <input 
              type="checkbox" 
              checked={step.completed} 
              readOnly
              className="form-checkbox text-green-500 bg-neutral-800 border-neutral-700 rounded h-4 w-4" 
            />
            <span className={`text-sm ${step.completed ? 'line-through text-neutral-500' : 'text-neutral-200'}`}>
              {step.label}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}
