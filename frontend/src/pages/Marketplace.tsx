import React, { useState } from "react";
import { useMarketplace } from "../hooks/useMarketplace";
import { PluginGrid } from "../components/marketplace/PluginGrid";
import { InstalledPluginTable } from "../components/marketplace/InstalledPluginTable";
import { PluginDetailPanel } from "../components/marketplace/PluginDetailPanel";
import { PluginManifest } from "../api/types";

export default function Marketplace() {
  const {
    plugins,
    installations,
    loading,
    error,
    install,
    enable,
    disable,
    uninstall,
    runAction,
  } = useMarketplace();

  const [selectedPlugin, setSelectedPlugin] = useState<PluginManifest | null>(null);

  const handleInstall = async (pluginId: string) => {
    try {
      await install(pluginId, "ws-1");
    } catch (err) {
      // Handled in hook
    }
  };

  const handleRunAction = async (action: string, payload: Record<string, any>, dryRun: boolean) => {
    if (!selectedPlugin) return;
    const inst = installations.find((i) => i.plugin_id === selectedPlugin.id);
    if (!inst) throw new Error("Plugin not installed yet");
    return runAction(inst.id, action, payload, dryRun);
  };

  const isPluginInstalled = (pluginId: string) => {
    return installations.some((inst) => inst.plugin_id === pluginId);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8 text-white relative">
      <div>
        <h2 className="text-3xl font-extrabold mb-2 tracking-tight">Plug-in Marketplace</h2>
        <p className="text-neutral-400">Expand dashboard functionality with verified third-party tools and IoT controls.</p>
      </div>

      {error && (
        <div className="p-4 bg-state-danger/10 border border-state-danger/20 text-state-danger rounded-xl text-sm font-semibold">
          Error: {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-6">
          <div className="h-48 bg-neutral-900/50 rounded-xl animate-pulse" />
          <div className="h-64 bg-neutral-900/50 rounded-xl animate-pulse" />
        </div>
      ) : (
        <>
          {/* Installed plugins section */}
          <section className="space-y-4">
            <h3 className="text-lg font-bold text-neutral-300">Installed Plug-ins</h3>
            <InstalledPluginTable
              installations={installations}
              plugins={plugins}
              onEnable={enable}
              onDisable={disable}
              onUninstall={uninstall}
              onViewDetails={setSelectedPlugin}
            />
          </section>

          {/* Plugin Grid catalog */}
          <section className="space-y-4">
            <h3 className="text-lg font-bold text-neutral-300">Browse Available Plugins</h3>
            <PluginGrid
              plugins={plugins}
              installations={installations}
              onInstall={handleInstall}
              onViewDetails={setSelectedPlugin}
            />
          </section>

          {/* Slide-over details & console panel */}
          {selectedPlugin && (
            <PluginDetailPanel
              plugin={selectedPlugin}
              onClose={() => setSelectedPlugin(null)}
              onInstall={handleInstall}
              isInstalled={isPluginInstalled(selectedPlugin.id)}
              onRunAction={handleRunAction}
            />
          )}
        </>
      )}
    </div>
  );
}
export { Marketplace };
