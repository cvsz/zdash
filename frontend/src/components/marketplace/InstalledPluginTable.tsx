import React from "react";
import { PluginInstallation, PluginManifest } from "../../api/types";

interface InstalledPluginTableProps {
  installations: PluginInstallation[];
  plugins: PluginManifest[];
  onEnable: (id: string) => void;
  onDisable: (id: string) => void;
  onUninstall: (id: string) => void;
  onViewDetails: (plugin: PluginManifest) => void;
}

export function InstalledPluginTable({
  installations,
  plugins,
  onEnable,
  onDisable,
  onUninstall,
  onViewDetails,
}: InstalledPluginTableProps) {
  if (installations.length === 0) {
    return (
      <div className="p-8 text-center text-neutral-500 text-sm border border-neutral-850 rounded-xl bg-neutral-950/20">
        No plugins currently installed.
      </div>
    );
  }

  const getPluginName = (pluginId: string) => {
    const plugin = plugins.find((p) => p.id === pluginId);
    return plugin ? plugin.name : pluginId;
  };

  const getPluginManifest = (pluginId: string) => {
    return plugins.find((p) => p.id === pluginId) || null;
  };

  return (
    <div className="overflow-x-auto rounded-xl border border-neutral-800 bg-neutral-950/20">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-neutral-850 bg-neutral-900/10 text-neutral-400 text-xs font-semibold uppercase tracking-wider">
            <th className="p-4">Plug-in</th>
            <th className="p-4">Version</th>
            <th className="p-4">Installed By</th>
            <th className="p-4">Installed At</th>
            <th className="p-4">Status</th>
            <th className="p-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-neutral-850 text-sm text-neutral-300">
          {installations.map((inst) => {
            const manifest = getPluginManifest(inst.plugin_id);
            return (
              <tr key={inst.id} className="hover:bg-neutral-900/10">
                <td className="p-4">
                  <div>
                    <span className="font-bold text-white block">{getPluginName(inst.plugin_id)}</span>
                    <span className="text-neutral-500 text-xs mt-0.5 block font-mono">{inst.plugin_id}</span>
                  </div>
                </td>
                <td className="p-4 font-mono text-neutral-400 text-xs">{inst.version}</td>
                <td className="p-4 text-xs text-neutral-400">{inst.installed_by}</td>
                <td className="p-4 text-xs text-neutral-400">
                  {new Date(inst.installed_at).toLocaleDateString()}
                </td>
                <td className="p-4">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider border ${
                      inst.enabled
                        ? "text-green-400 bg-green-500/10 border-green-500/20"
                        : "text-amber-400 bg-amber-500/10 border-amber-500/20"
                    }`}
                  >
                    {inst.enabled ? "Active" : "Disabled"}
                  </span>
                </td>
                <td className="p-4 text-right flex items-center justify-end gap-3 h-full">
                  {manifest && (
                    <button
                      onClick={() => onViewDetails(manifest)}
                      className="text-violet-400 hover:text-violet-300 text-xs font-semibold"
                    >
                      Console
                    </button>
                  )}

                  {inst.enabled ? (
                    <button
                      onClick={() => onDisable(inst.id)}
                      className="px-2 py-1 bg-amber-950/20 text-amber-400 border border-amber-900/30 hover:border-amber-900/50 rounded text-xs font-semibold transition"
                    >
                      Disable
                    </button>
                  ) : (
                    <button
                      onClick={() => onEnable(inst.id)}
                      className="px-2 py-1 bg-green-950/20 text-green-400 border border-green-900/30 hover:border-green-900/50 rounded text-xs font-semibold transition"
                    >
                      Enable
                    </button>
                  )}

                  <button
                    onClick={() => onUninstall(inst.id)}
                    className="px-2 py-1 bg-rose-950/20 text-rose-400 border border-rose-900/30 hover:border-rose-900/50 rounded text-xs font-semibold transition"
                  >
                    Uninstall
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
export default InstalledPluginTable;
