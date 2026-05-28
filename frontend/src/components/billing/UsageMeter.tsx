import React from "react";

export function UsageMeter() {
  const usage = [
    { metric: "API Requests", used: 1500, limit: 10000 },
    { metric: "Workspaces", used: 2, limit: 5 },
    { metric: "Trading Signals", used: 120, limit: 500 },
  ];

  return (
    <div className="space-y-4">
      {usage.map((u) => {
        const percent = Math.min((u.used / u.limit) * 100, 100);
        return (
          <div key={u.metric} className="bg-neutral-900 p-4 rounded border border-neutral-800">
            <div className="flex justify-between text-sm mb-2">
              <span className="font-medium">{u.metric}</span>
              <span className="text-neutral-400">
                {u.used} / {u.limit}
              </span>
            </div>
            <div className="w-full bg-neutral-800 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${percent}%` }}
              ></div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
