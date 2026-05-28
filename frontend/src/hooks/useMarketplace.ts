import { useState, useEffect } from "react";
import {
  listMarketplacePlugins,
  listPluginInstallations,
  installMarketplacePlugin,
  enablePluginInstallation,
  disablePluginInstallation,
  uninstallPluginInstallation,
  runPluginAction as apiRunPluginAction,
} from "../api/endpoints";
import { PluginManifest, PluginInstallation } from "../api/types";

export function useMarketplace() {
  const [plugins, setPlugins] = useState<PluginManifest[]>([]);
  const [installations, setInstallations] = useState<PluginInstallation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMarketplace = async () => {
    try {
      setLoading(true);
      setError(null);
      const [pluginsRes, installationsRes] = await Promise.all([
        listMarketplacePlugins(),
        listPluginInstallations(),
      ]);
      setPlugins(pluginsRes);
      setInstallations(installationsRes);
    } catch (err: any) {
      setError(err.message || "Failed to load marketplace data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMarketplace();
  }, []);

  const install = async (pluginId: string, workspaceId: string, config: Record<string, any> = {}) => {
    setError(null);
    try {
      const res = await installMarketplacePlugin(pluginId, workspaceId, config);
      await fetchMarketplace();
      return res;
    } catch (err: any) {
      setError(err.message || "Failed to install plugin");
      throw err;
    }
  };

  const enable = async (installationId: string) => {
    setError(null);
    try {
      const res = await enablePluginInstallation(installationId);
      await fetchMarketplace();
      return res;
    } catch (err: any) {
      setError(err.message || "Failed to enable plugin");
      throw err;
    }
  };

  const disable = async (installationId: string) => {
    setError(null);
    try {
      const res = await disablePluginInstallation(installationId);
      await fetchMarketplace();
      return res;
    } catch (err: any) {
      setError(err.message || "Failed to disable plugin");
      throw err;
    }
  };

  const uninstall = async (installationId: string) => {
    setError(null);
    try {
      const res = await uninstallPluginInstallation(installationId);
      await fetchMarketplace();
      return res;
    } catch (err: any) {
      setError(err.message || "Failed to uninstall plugin");
      throw err;
    }
  };

  const runAction = async (
    installationId: string,
    action: string,
    payload: Record<string, any> = {},
    dryRun = true
  ) => {
    setError(null);
    try {
      // Safety rule: Plugin actions default to dry-run unless explicitly allowed (dryRun=false)
      const finalPayload = { ...payload, dry_run: dryRun };
      const res = await apiRunPluginAction(installationId, action, finalPayload);
      return res;
    } catch (err: any) {
      setError(err.message || "Plugin action execution failed");
      throw err;
    }
  };

  return {
    plugins,
    installations,
    loading,
    error,
    install,
    enable,
    disable,
    uninstall,
    runAction,
    refetch: fetchMarketplace,
  };
}
