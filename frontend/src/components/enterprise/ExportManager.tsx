import React from "react";

export function ExportManager() {
  return (
    <div className="bg-neutral-900 border border-neutral-800 p-6 rounded">
      <h4 className="font-bold text-lg mb-4">Export Bundles</h4>
      <p className="text-sm text-neutral-400 mb-6">Generate full data exports for compliance or offline migration.</p>
      
      <div className="space-y-4 mb-6">
        <label className="flex items-center space-x-3 text-sm">
          <input type="checkbox" defaultChecked className="form-checkbox text-blue-500 bg-neutral-800 border-neutral-700 rounded" />
          <span>Include Audit Logs</span>
        </label>
        <label className="flex items-center space-x-3 text-sm">
          <input type="checkbox" defaultChecked className="form-checkbox text-blue-500 bg-neutral-800 border-neutral-700 rounded" />
          <span>Include Generated Content</span>
        </label>
        <label className="flex items-center space-x-3 text-sm">
          <input type="checkbox" className="form-checkbox text-blue-500 bg-neutral-800 border-neutral-700 rounded" />
          <span>Include Secrets & Keys (Requires elevated privileges)</span>
        </label>
      </div>

      <button className="bg-neutral-800 hover:bg-neutral-700 text-white border border-neutral-700 px-4 py-2 rounded text-sm font-medium w-full">
        Create New Export Bundle
      </button>

      <div className="mt-6 pt-6 border-t border-neutral-800">
        <h5 className="text-sm font-semibold mb-3">Recent Exports</h5>
        <div className="text-sm text-neutral-500 text-center py-4 border border-dashed border-neutral-700 rounded">
          No previous exports found.
        </div>
      </div>
    </div>
  );
}
