import React from "react";
import { useT } from '../../hooks/useT';

export function ExportManager() {
  const { t } = useT();

  return (
    <div className="bg-neutral-900 border border-neutral-800 p-6 rounded">
      <h4 className="font-bold text-lg mb-4">{t('enterprise.export_manager_title')}</h4>
      <p className="text-sm text-neutral-400 mb-6">{t('enterprise.export_manager_desc')}</p>
      
      <div className="space-y-4 mb-6">
        <label className="flex items-center space-x-3 text-sm">
          <input type="checkbox" defaultChecked className="form-checkbox text-blue-500 bg-neutral-800 border-neutral-700 rounded" />
          <span>{t('enterprise.include_audit_logs')}</span>
        </label>
        <label className="flex items-center space-x-3 text-sm">
          <input type="checkbox" defaultChecked className="form-checkbox text-blue-500 bg-neutral-800 border-neutral-700 rounded" />
          <span>{t('enterprise.include_content')}</span>
        </label>
        <label className="flex items-center space-x-3 text-sm">
          <input type="checkbox" className="form-checkbox text-blue-500 bg-neutral-800 border-neutral-700 rounded" />
          <span>{t('enterprise.include_secrets_elevated')}</span>
        </label>
      </div>

      <button className="bg-neutral-800 hover:bg-neutral-700 text-white border border-neutral-700 px-4 py-2 rounded text-sm font-medium w-full">
        {t('enterprise.create_new_export_bundle')}
      </button>

      <div className="mt-6 pt-6 border-t border-neutral-800">
        <h5 className="text-sm font-semibold mb-3">{t('enterprise.recent_exports')}</h5>
        <div className="text-sm text-neutral-500 text-center py-4 border border-dashed border-neutral-700 rounded">
          {t('enterprise.no_previous_exports')}
        </div>
      </div>
    </div>
  );
}
