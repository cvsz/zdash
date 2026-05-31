import React, { useState, useEffect } from "react";
import { PluginManifest } from "../../api/types";

interface PluginDetailPanelProps {
  plugin: PluginManifest | null;
  onClose: () => void;
  onInstall: (pluginId: string, config?: Record<string, any>) => void;
  isInstalled: boolean;
  onRunAction?: (action: string, payload: Record<string, any>, dryRun: boolean) => Promise<any>;
  actionLoading?: boolean;
}

export function PluginDetailPanel({
  plugin,
  onClose,
  onInstall,
  isInstalled,
  onRunAction,
  actionLoading,
}: PluginDetailPanelProps) {
  const [actionName, setActionName] = useState("");
  const [actionPayload, setActionPayload] = useState("");
  const [isDryRun, setIsDryRun] = useState(true);
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<any>(null);
  const [runError, setRunError] = useState<string | null>(null);
  const [installConfig, setInstallConfig] = useState("");
  const [configError, setConfigError] = useState<string | null>(null);

  useEffect(() => {
    setInstallConfig(JSON.stringify(plugin?.default_config || {}, null, 2));
    setConfigError(null);
    setActionName("");
    setActionPayload("");
    setRunResult(null);
    setRunError(null);
  }, [plugin]);

  if (!plugin) return null;

  const safetyLevel = typeof plugin.safety_level === "string" && plugin.safety_level.trim()
    ? plugin.safety_level
    : "sandbox";
  const requiredFeatures = Array.isArray(plugin.required_features) ? plugin.required_features : [];
  const requiredPermissions = Array.isArray(plugin.required_permissions) ? plugin.required_permissions : [];
  const pluginName = plugin.name || plugin.id || "Plugin";
  const pluginCategory = plugin.category || "general";
  const pluginVersion = plugin.version || "0.0.0";
  const pluginDescription = plugin.description || "No description provided.";
  const hasConfigSchema = typeof plugin.config_schema === "object" && plugin.config_schema !== null && Object.keys(plugin.config_schema).length > 0;

  const handleConfigChange = (value: string) => {
    setInstallConfig(value);
    try {
      if (value.trim()) {
        JSON.parse(value);
      }
      setConfigError(null);
    } catch {
      setConfigError("Invalid JSON format");
    }
  };

  const handleInstallWithConfig = () => {
    if (configError) return;
    let config: Record<string, any> = {};
    if (installConfig.trim()) {
      try {
        config = JSON.parse(installConfig);
      } catch {
        setConfigError("Invalid JSON configuration");
        return;
      }
    }
    onInstall(plugin.id, config);
  };

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
          <h3 className="text-xl font-bold text-white">{pluginName}</h3>
          {plugin.source_type && (
            <span className="text-neutral-500 text-xs mt-1 block">
              Source: <span className="font-mono">{plugin.source_type}</span>
              {plugin.source_ref && <span> ({plugin.source_ref})</span>}
            </span>
          )}
          <span className="text-neutral-500 text-xs mt-1 block">
            Category: <span className="capitalize">{pluginCategory}</span> • v{pluginVersion}
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
          <p className="text-sm text-neutral-300 leading-relaxed">{pluginDescription}</p>
        </section>

        {/* Safety & Isolation Notes */}
        <section className="p-4 rounded-lg bg-neutral-900/40 border border-neutral-850 space-y-2">
          <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Plugin Safety Level</h4>
          <div className="flex items-center gap-2 mt-1">
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider ${
                safetyLevel === "sandbox"
                  ? "text-green-400 bg-green-500/10 border border-green-500/20"
                  : "text-amber-400 bg-amber-500/10 border border-amber-500/20"
              }`}
            >
              {safetyLevel}
            </span>
          </div>
          <p className="text-xs text-neutral-400 leading-relaxed mt-2">
            {safetyLevel === "sandbox"
              ? "This plug-in executes in a secure sandboxed container. It does not have access to system secrets, files, or external networks. Actions are fully safe to simulate."
              : "This plug-in runs with restricted permissions. It requires access to specific integrations or tokens to communicate with external web services."}
          </p>
        </section>

        {/* Requirements */}
        <section className="grid grid-cols-2 gap-4">
          <div>
            <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">Required Features</h4>
            {requiredFeatures.length === 0 ? (
              <span className="text-xs text-neutral-500">None required</span>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {requiredFeatures.map((f, i) => (
                  <span key={i} className="px-2 py-0.5 rounded bg-neutral-900 text-neutral-400 text-xs font-mono">
                    {f}
                  </span>
                ))}
              </div>
            )}
          </div>

          <div>
            <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">Required Permissions</h4>
            {requiredPermissions.length === 0 ? (
              <span className="text-xs text-neutral-500">None required</span>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {requiredPermissions.map((p, i) => (
                  <span key={i} className="px-2 py-0.5 rounded bg-neutral-900 text-neutral-400 text-xs font-mono">
                    {p}
                  </span>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Config editor for install */}
        {!isInstalled && hasConfigSchema && (
          <section className="border-t border-neutral-900 pt-6 space-y-4">
            <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Configuration</h4>
            <p className="text-xs text-neutral-500">
              Customize plugin configuration before installing. Changes take effect on install.
            </p>
            <textarea
              value={installConfig}
              onChange={(e) => handleConfigChange(e.target.value)}
              rows={6}
              className="w-full px-3 py-2 rounded-lg bg-neutral-900 border border-neutral-800 text-neutral-200 placeholder-neutral-600 focus:outline-none focus:border-violet-500 text-sm font-mono"
            />
            {configError && (
              <p className="text-xs text-rose-400">{configError}</p>
            )}
          </section>
        )}

        {/* Dry-run action runner console */}
        {isInstalled && onRunAction && (
          <section className="border-t border-neutral-900 pt-6 space-y-4">
            <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Dry-Run Plugin Console</h4>
            <p className="text-xs text-neutral-500">
              Simulate actions and verify outputs before enabling active production controls.
            </p>

            <form onSubmit={handleRun} className="space-y-4">
              <div>
                <label htmlFor="plugin-action-name" className="block text-xs font-medium text-neutral-400 mb-1">Action Name</label>
                <input
                  id="plugin-action-name"
                  name="plugin-action-name"
                  type="text"
                  required
                  placeholder="e.g. test_action"
                  value={actionName}
                  onChange={(e) => setActionName(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-neutral-900 border border-neutral-800 text-neutral-200 placeholder-neutral-600 focus:outline-none focus:border-violet-500 text-sm font-mono"
                />
              </div>

              <div>
                <label htmlFor="plugin-action-payload" className="block text-xs font-medium text-neutral-400 mb-1">Payload JSON (Optional)</label>
                <textarea
                  id="plugin-action-payload"
                  name="plugin-action-payload"
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
            onClick={handleInstallWithConfig}
            disabled={!!configError || !!actionLoading}
            className="w-full py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-semibold text-sm transition disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {actionLoading ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Installing...
              </>
            ) : (
              "Install plug-in"
            )}
          </button>
        </div>
      )}
    </div>
  );
}
export default PluginDetailPanel;
