import { useState, useEffect } from "react";
import {
  listMarketplacePlugins,
  listPluginInstallations,
  listPluginCategories,
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
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");

  const fetchMarketplace = async () => {
    try {
      setLoading(true);
      setError(null);
      const [pluginsRes, installationsRes, categoriesRes] = await Promise.all([
        listMarketplacePlugins(search || undefined, category || undefined, status || undefined),
        listPluginInstallations(),
        listPluginCategories(),
      ]);
      setPlugins(Array.isArray(pluginsRes) ? pluginsRes : []);
      setInstallations(Array.isArray(installationsRes) ? installationsRes : []);
      setCategories(Array.isArray(categoriesRes) ? categoriesRes : []);
    } catch (err: any) {
      setError(err.message || "Failed to load marketplace data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMarketplace();
  }, [search, category, status]);

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
    refetch: fetchMarketplace,
  };
}
