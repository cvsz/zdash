import React from "react";
import { PluginDirectory } from "../components/marketplace/PluginDirectory";
import { InstalledPlugins } from "../components/marketplace/InstalledPlugins";

export default function Marketplace() {
  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-bold mb-2">Marketplace</h2>
        <p className="text-neutral-400">Discover and install plugins to extend zDash capabilities.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <section className="lg:col-span-2">
          <h3 className="text-xl font-semibold mb-4">Plugin Directory</h3>
          <PluginDirectory />
        </section>

        <section className="lg:col-span-1">
          <h3 className="text-xl font-semibold mb-4">Installed Plugins</h3>
          <InstalledPlugins />
        </section>
      </div>
    </div>
  );
}
