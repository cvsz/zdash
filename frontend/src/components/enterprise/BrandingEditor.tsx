import React from "react";

export function BrandingEditor() {
  return (
    <div className="bg-neutral-900 border border-neutral-800 p-6 rounded">
      <h4 className="font-bold text-lg mb-4">White-Label Branding</h4>
      <form className="space-y-4">
        <div>
          <label className="block text-sm text-neutral-400 mb-1">Brand Name</label>
          <input type="text" defaultValue="zDash" className="w-full bg-neutral-800 border border-neutral-700 rounded p-2 text-sm text-white focus:border-blue-500 focus:outline-none" />
        </div>
        <div>
          <label className="block text-sm text-neutral-400 mb-1">Logo URL</label>
          <input type="text" placeholder="https://..." className="w-full bg-neutral-800 border border-neutral-700 rounded p-2 text-sm text-white focus:border-blue-500 focus:outline-none" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-neutral-400 mb-1">Primary Color</label>
            <div className="flex gap-2">
              <input type="color" defaultValue="#7c3aed" className="w-8 h-8 rounded cursor-pointer" />
              <input type="text" defaultValue="#7c3aed" className="w-full bg-neutral-800 border border-neutral-700 rounded p-1 text-sm text-white focus:outline-none" />
            </div>
          </div>
          <div>
            <label className="block text-sm text-neutral-400 mb-1">Accent Color</label>
            <div className="flex gap-2">
              <input type="color" defaultValue="#22c55e" className="w-8 h-8 rounded cursor-pointer" />
              <input type="text" defaultValue="#22c55e" className="w-full bg-neutral-800 border border-neutral-700 rounded p-1 text-sm text-white focus:outline-none" />
            </div>
          </div>
        </div>
        <button type="button" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-medium w-full">
          Save Branding Settings
        </button>
      </form>
    </div>
  );
}
