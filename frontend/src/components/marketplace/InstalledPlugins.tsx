import React from "react";
import { useT } from "../../hooks/useT";

export function InstalledPlugins() {
  const { t } = useT();
  const plugins = [
    { id: "zdash-discord-hook", name: "Discord Webhook", status: "Enabled" },
  ];

  return (
    <div className="space-y-4">
      {plugins.map((p) => (
        <div key={p.id} className="p-4 border border-neutral-800 rounded bg-neutral-900 flex justify-between items-center">
          <div>
            <h4 className="font-bold">{p.name}</h4>
            <span className="text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded">
              {p.status}
            </span>
          </div>
          <div className="space-x-2">
            <button className="text-sm text-neutral-400 hover:text-white px-3 py-1">{t('marketplace.installed_settings_button')}</button>
            <button className="text-sm text-red-400 hover:text-red-300 px-3 py-1">{t('marketplace.installed_uninstall_button')}</button>
          </div>
        </div>
      ))}
      {plugins.length === 0 && <p className="text-neutral-500">{t('marketplace.installed_table_empty')}</p>}
    </div>
  );
}
