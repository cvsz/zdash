import React, { useState } from "react";
import { PluginManifest, PluginInstallation } from "../../api/types";
import { PluginCard } from "./PluginCard";

interface PluginGridProps {
  plugins: PluginManifest[];
  installations: PluginInstallation[];
  onInstall: (pluginId: string) => void;
  onViewDetails: (plugin: PluginManifest) => void;
}

export function PluginGrid({ plugins, installations, onInstall, onViewDetails }: PluginGridProps) {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  const categories = ["all", ...Array.from(new Set(plugins.map((p) => p.category)))];

  const filteredPlugins = plugins.filter((p) => {
    const matchesSearch =
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.description.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategory === "all" || p.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const isPluginInstalled = (pluginId: string) => {
    return installations.some((inst) => inst.plugin_id === pluginId);
  };

  return (
    <div className="space-y-6">
      {/* Search and Category Filters */}
      <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-4">
        <div className="flex-1 max-w-md">
          <input
            type="text"
            placeholder="Search plugins by name or description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full px-4 py-2 rounded-lg bg-neutral-900 border border-neutral-800 text-neutral-200 placeholder-neutral-500 focus:outline-none focus:border-violet-500 text-sm"
          />
        </div>

        <div className="flex gap-2 overflow-x-auto pb-1 sm:pb-0">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg border text-xs font-semibold uppercase tracking-wider transition-all duration-150 capitalize shrink-0 ${
                selectedCategory === cat
                  ? "bg-violet-600 border-violet-500/20 text-white"
                  : "bg-neutral-900 border-neutral-850 hover:border-neutral-700 text-neutral-400"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {filteredPlugins.length === 0 ? (
        <div className="p-12 text-center text-neutral-500 text-sm border border-neutral-850 rounded-xl bg-neutral-950/20">
          No plug-ins match your filter criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPlugins.map((plugin) => (
            <PluginCard
              key={plugin.id}
              plugin={plugin}
              isInstalled={isPluginInstalled(plugin.id)}
              onInstall={onInstall}
              onViewDetails={onViewDetails}
            />
          ))}
        </div>
      )}
    </div>
  );
}
export default PluginGrid;
