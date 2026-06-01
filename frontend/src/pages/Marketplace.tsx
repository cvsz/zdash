import React, { useState } from "react";
import { useMarketplace } from "../hooks/useMarketplace";
import { PluginGrid } from "../components/marketplace/PluginGrid";
import { InstalledPluginTable } from "../components/marketplace/InstalledPluginTable";
import { PluginDetailPanel } from "../components/marketplace/PluginDetailPanel";
import { PluginManifest } from "../api/types";
import { useT } from "../hooks/useT";

export default function Marketplace() {
  const { t } = useT();
  const {
    plugins,
    installations,
    categories,
    loading,
    error,
    search,
    setSearch,
    category,
    setCategory,
    status,
    setStatus,
    install,
    enable,
    disable,
    uninstall,
    runAction,
  } = useMarketplace();

  const [selectedPlugin, setSelectedPlugin] = useState<PluginManifest | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const handleInstall = async (pluginId: string, config?: Record<string, any>) => {
    setActionLoading("install-" + pluginId);
    try {
      await install(pluginId, "ws-1", config);
    } catch {
      // Error state is handled in useMarketplace.
    } finally {
      setActionLoading(null);
    }
  };

  const handleEnable = async (installationId: string) => {
    setActionLoading("enable-" + installationId);
    try {
      await enable(installationId);
    } catch {
      // Error state is handled in useMarketplace.
    } finally {
      setActionLoading(null);
    }
  };

  const handleDisable = async (installationId: string) => {
    setActionLoading("disable-" + installationId);
    try {
      await disable(installationId);
    } catch {
      // Error state is handled in useMarketplace.
    } finally {
      setActionLoading(null);
    }
  };

  const handleUninstall = async (installationId: string) => {
    setActionLoading("uninstall-" + installationId);
    try {
      await uninstall(installationId);
    } catch {
      // Error state is handled in useMarketplace.
    } finally {
      setActionLoading(null);
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

  const isLoadingAction = (prefix: string, id: string) => {
    return actionLoading === prefix + id;
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8 text-white relative">
      <div>
        <h2 className="text-3xl font-extrabold mb-2 tracking-tight">{t('marketplace.title')}</h2>
        <p className="text-neutral-400">{t('marketplace.subtitle')}</p>
      </div>

      {error && (
        <div className="p-4 bg-state-danger/10 border border-state-danger/20 text-state-danger rounded-xl text-sm font-semibold">
          {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-6">
          <div className="h-48 bg-neutral-900/50 rounded-xl animate-pulse" />
          <div className="h-64 bg-neutral-900/50 rounded-xl animate-pulse" />
        </div>
      ) : (
        <>
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex-1 min-w-[200px]">
              <input
                type="text"
                placeholder={t('marketplace.search_plugins')}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full px-4 py-2 rounded-lg bg-neutral-900 border border-neutral-800 text-neutral-200 placeholder-neutral-600 focus:outline-none focus:border-violet-500 text-sm"
              />
            </div>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="px-4 py-2 rounded-lg bg-neutral-900 border border-neutral-800 text-neutral-200 focus:outline-none focus:border-violet-500 text-sm"
            >
              <option value="">{t('marketplace.all_categories')}</option>
              {categories.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="px-4 py-2 rounded-lg bg-neutral-900 border border-neutral-800 text-neutral-200 focus:outline-none focus:border-violet-500 text-sm"
            >
              <option value="">{t('marketplace.all_statuses')}</option>
              <option value="approved">{t('marketplace.approved')}</option>
              <option value="draft">{t('marketplace.draft')}</option>
              <option value="disabled">{t('marketplace.disabled')}</option>
            </select>
          </div>

          <section className="space-y-4">
            <h3 className="text-lg font-bold text-neutral-300">{t('marketplace.installed_plugins')}</h3>
            <InstalledPluginTable
              installations={installations}
              plugins={plugins}
              onEnable={handleEnable}
              onDisable={handleDisable}
              onUninstall={handleUninstall}
              onViewDetails={setSelectedPlugin}
            />
          </section>

          <section className="space-y-4">
            <h3 className="text-lg font-bold text-neutral-300">{t('marketplace.browse_available')}</h3>
            <PluginGrid
              plugins={plugins}
              installations={installations}
              onInstall={handleInstall}
              onViewDetails={setSelectedPlugin}
            />
          </section>

          {selectedPlugin && (
            <PluginDetailPanel
              plugin={selectedPlugin}
              onClose={() => setSelectedPlugin(null)}
              onInstall={handleInstall}
              isInstalled={isPluginInstalled(selectedPlugin.id)}
              onRunAction={handleRunAction}
              actionLoading={isLoadingAction("install-", selectedPlugin.id)}
            />
          )}
        </>
      )}
    </div>
  );
}

export { Marketplace };
