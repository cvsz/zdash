import React from "react";
import { PluginManifest } from "../../api/types";
import { useT } from "../../hooks/useT";

interface PluginCardProps {
  plugin: PluginManifest;
  isInstalled: boolean;
  onInstall: (pluginId: string) => void;
  onViewDetails: (plugin: PluginManifest) => void;
}

function safeText(value: unknown, fallback = ""): string {
  return typeof value === "string" && value.trim() ? value : fallback;
}

export function PluginCard({ plugin, isInstalled, onInstall, onViewDetails }: PluginCardProps) {
  const { t } = useT();
  const safetyLevel = safeText(plugin.safety_level, "sandbox");
  const category = safeText(plugin.category, "general");
  const name = safeText(plugin.name, plugin.id || "Plugin");
  const version = safeText(plugin.version, "0.0.0");
  const author = safeText(plugin.author, t('common.unknown'));
  const description = safeText(plugin.description, t('common.no_description'));

  const getSafetyBadgeStyle = (level: string) => {
    switch (level.toLowerCase()) {
      case "sandbox":
        return "text-green-400 bg-green-500/10 border-green-500/20";
      case "restricted":
        return "text-amber-400 bg-amber-500/10 border-amber-500/20";
      default:
        return "text-rose-400 bg-rose-500/10 border-rose-500/20";
    }
  };

  return (
    <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/40 hover:border-neutral-700 flex flex-col justify-between transition-all duration-200">
      <div>
        <div className="flex justify-between items-start gap-2 mb-4">
          <div>
            <h4 className="text-lg font-bold text-white">{name}</h4>
            <span className="text-neutral-500 text-xs mt-1 block">
              {t('marketplace.plugin_card_version_by', { version, author })}
            </span>
          </div>
          <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-neutral-900 border border-neutral-800 text-neutral-400 capitalize">
            {category}
          </span>
        </div>

        <p className="text-sm text-neutral-400 mb-6 line-clamp-3">{description}</p>

        <div className="space-y-3 mb-6">
          <div className="flex items-center justify-between text-xs border-b border-neutral-900 pb-2">
            <span className="text-neutral-500 font-semibold uppercase tracking-wider">{t('marketplace.plugin_card_safety_rating')}</span>
            <span
              className={`px-2 py-0.5 rounded-full border text-[10px] uppercase font-bold tracking-wider ${getSafetyBadgeStyle(
                safetyLevel,
              )}`}
            >
              {safetyLevel}
            </span>
          </div>

          <div className="text-[11px] text-neutral-500 italic">
            {safetyLevel === "sandbox"
              ? t('marketplace.plugin_card_safety_sandbox')
              : t('marketplace.plugin_card_safety_restricted')}
          </div>
        </div>
      </div>

      <div className="flex gap-2 pt-2 border-t border-neutral-900">
        <button
          onClick={() => onViewDetails({ ...plugin, safety_level: safetyLevel })}
          className="flex-1 py-2 px-3 rounded-lg bg-neutral-900 hover:bg-neutral-850 text-neutral-300 border border-neutral-800 text-xs font-semibold transition duration-150"
        >
          {t('marketplace.plugin_card_view_details')}
        </button>

        {isInstalled ? (
          <button
            disabled
            className="flex-1 py-2 px-3 rounded-lg bg-neutral-950 text-neutral-600 border border-neutral-900 text-xs font-semibold cursor-not-allowed"
          >
            {t('marketplace.plugin_card_installed')}
          </button>
        ) : (
          <button
            onClick={() => onInstall(plugin.id)}
            className="flex-1 py-2 px-3 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs border border-violet-500/20 transition duration-150"
          >
            {t('marketplace.plugin_card_install')}
          </button>
        )}
      </div>
    </div>
  );
}
