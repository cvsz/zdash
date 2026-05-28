import React from "react";

export function PluginDirectory() {
  const plugins = [
    { id: "zdash-risk-summary", name: "Risk Summary", desc: "Summarize daily risk metrics." },
    { id: "zdash-slack-notify", name: "Slack Alerts", desc: "Send alerts directly to your Slack workspace." },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {plugins.map((p) => (
        <div key={p.id} className="p-4 border border-neutral-800 rounded bg-neutral-900 flex justify-between items-center">
          <div>
            <h4 className="font-bold">{p.name}</h4>
            <p className="text-sm text-neutral-400">{p.desc}</p>
          </div>
          <button className="bg-neutral-700 hover:bg-neutral-600 px-4 py-2 rounded text-sm">
            Install
          </button>
        </div>
      ))}
    </div>
  );
}
