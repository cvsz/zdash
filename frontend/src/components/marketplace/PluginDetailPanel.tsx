import React, { useState } from "react";
import { PluginManifest } from "../../api/types";

interface PluginDetailPanelProps {
  plugin: PluginManifest | null;
  onClose: () => void;
  onInstall: (pluginId: string) => void;
  isInstalled: boolean;
  onRunAction?: (action: string, payload: Record<string, any>, dryRun: boolean) => Promise<any>;
}

export function PluginDetailPanel({
  plugin,
  onClose,
  onInstall,
  isInstalled,
  onRunAction,
}: PluginDetailPanelProps) {
  const [actionName, setActionName] = useState("");
  const [actionPayload, setActionPayload] = useState("");
  const [isDryRun, setIsDryRun] = useState(true);
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<any>(null);
  const [runError, setRunError] = useState<string | null>(null);

  if (!plugin) return null;

  const handleRun = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!onRunAction || !actionName) return;

    setRunning(true);
    setRunResult(null);
    setRunError(null);

    try {
      let parsedPayload = {};
      if (actionPayload.trim()) {
        parsedPayload = JSON.parse(actionPayload);
      }
      const res = await onRunAction(actionName, parsedPayload, isDryRun);
      setRunResult(res);
    } catch (err: any) {
      setRunError(err.message || "Action run failed. Verify payload JSON format.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-xl bg-neutral-950 border-l border-neutral-800 shadow-2xl flex flex-col z-50 overflow-y-auto">
      {/* Header */}
      <div className="p-6 border-b border-neutral-800 flex justify-between items-center bg-neutral-900/30">
        <div>
          <h3 className="text-xl font-bold text-white">{plugin.name}</h3>
          <span className="text-neutral-500 text-xs mt-1 block">
            Category: <span className="capitalize">{plugin.category}</span> • v{plugin.version}
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-neutral-400 hover:text-white p-2 rounded-lg bg-neutral-900 border border-neutral-850 hover:border-neutral-750 transition"
        >
          ✕
        </button>
      </div>

      <div className="p-6 space-y-8 flex-1">
        {/* Description */}
        <section className="space-y-2">
          <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Description</h4>
          <p className="text-sm text-neutral-300 leading-relaxed">{plugin.description}</p>
        </section>

        {/* Safety & Isolation Notes */}
        <section className="p-4 rounded-lg bg-neutral-900/40 border border-neutral-850 space-y-2">
          <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Plugin Safety Level</h4>
          <div className="flex items-center gap-2 mt-1">
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider ${
                plugin.safety_level === "sandbox"
                  ? "text-green-400 bg-green-500/10 border border-green-500/20"
                  : "text-amber-400 bg-amber-500/10 border border-amber-500/20"
              }`}
            >
              {plugin.safety_level}
            </span>
          </div>
          <p className="text-xs text-neutral-400 leading-relaxed mt-2">
            {plugin.safety_level === "sandbox"
              ? "This plug-in executes in a secure sandboxed container. It does not have access to system secrets, files, or external networks. Actions are fully safe to simulate."
              : "This plug-in runs with restricted permissions. It requires access to specific integrations or tokens to communicate with external web services."}
          </p>
        </section>

        {/* Requirements */}
        <section className="grid grid-cols-2 gap-4">
          <div>
            <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">Required Features</h4>
            {plugin.required_features.length === 0 ? (
              <span className="text-xs text-neutral-500">None required</span>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {plugin.required_features.map((f, i) => (
                  <span key={i} className="px-2 py-0.5 rounded bg-neutral-900 text-neutral-400 text-xs font-mono">
                    {f}
                  </span>
                ))}
              </div>
            )}
          </div>

          <div>
            <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">Required Permissions</h4>
            {plugin.required_permissions.length === 0 ? (
              <span className="text-xs text-neutral-500">None required</span>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {plugin.required_permissions.map((p, i) => (
                  <span key={i} className="px-2 py-0.5 rounded bg-neutral-900 text-neutral-400 text-xs font-mono">
                    {p}
                  </span>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Dry-run action runner console */}
        {isInstalled && onRunAction && (
          <section className="border-t border-neutral-900 pt-6 space-y-4">
            <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Dry-Run Plugin Console</h4>
            <p className="text-xs text-neutral-500">
              Simulate actions and verify outputs before enabling active production controls.
            </p>

            <form onSubmit={handleRun} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-neutral-400 mb-1">Action Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. test_action"
                  value={actionName}
                  onChange={(e) => setActionName(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-neutral-900 border border-neutral-800 text-neutral-200 placeholder-neutral-600 focus:outline-none focus:border-violet-500 text-sm font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-neutral-400 mb-1">Payload JSON (Optional)</label>
                <textarea
                  placeholder='e.g. { "param": "value" }'
                  value={actionPayload}
                  onChange={(e) => setActionPayload(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 rounded-lg bg-neutral-900 border border-neutral-800 text-neutral-200 placeholder-neutral-600 focus:outline-none focus:border-violet-500 text-sm font-mono"
                />
              </div>

              <div className="flex items-center justify-between py-1 bg-neutral-900/10 px-3 rounded-lg border border-neutral-850">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="dryRunCheckbox"
                    checked={isDryRun}
                    onChange={(e) => setIsDryRun(e.target.checked)}
                    className="rounded border-neutral-800 text-violet-600 focus:ring-violet-500 h-4 w-4 bg-neutral-950"
                  />
                  <label htmlFor="dryRunCheckbox" className="text-xs font-semibold text-neutral-300">
                    Dry-Run Execution (Recommended)
                  </label>
                </div>
                <span className="text-[10px] uppercase font-extrabold text-green-400 bg-green-500/10 border border-green-500/20 px-2 py-0.5 rounded-full">
                  Mock Protected
                </span>
              </div>

              <button
                type="submit"
                disabled={running}
                className="w-full py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs border border-violet-500/20 transition disabled:opacity-50"
              >
                {running ? "Executing..." : isDryRun ? "Run Dry-Run Action" : "Run Active Action"}
              </button>
            </form>

            {/* Run Output Display */}
            {runResult && (
              <div className="p-4 rounded-lg bg-neutral-900 border border-neutral-850 text-xs font-mono space-y-2">
                <div className="text-green-400 font-bold">✔ Execution Succeeded</div>
                <pre className="text-neutral-300 overflow-x-auto whitespace-pre-wrap">
                  {JSON.stringify(runResult, null, 2)}
                </pre>
              </div>
            )}

            {runError && (
              <div className="p-4 rounded-lg bg-rose-950/20 border border-rose-900/30 text-xs font-mono space-y-2">
                <div className="text-rose-400 font-bold">✕ Execution Failed</div>
                <div className="text-rose-300">{runError}</div>
              </div>
            )}
          </section>
        )}
      </div>

      {/* Footer / Install Action */}
      {!isInstalled && (
        <div className="p-6 border-t border-neutral-800 bg-neutral-900/20 flex gap-4">
          <button
            onClick={() => onInstall(plugin.id)}
            className="w-full py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-semibold text-sm transition"
          >
            Install plug-in
          </button>
        </div>
      )}
    </div>
  );
}
export default PluginDetailPanel;
