import React from "react";
import { useT } from '../../hooks/useT';

export function LicenseStatus() {
  const { t } = useT();

  return (
    <div className="bg-neutral-900 border border-neutral-800 p-6 rounded">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h4 className="font-bold text-lg mb-1">{t('enterprise.enterprise_license_title')}</h4>
          <p className="text-sm text-neutral-400">{t('enterprise.enterprise_license_desc')}</p>
        </div>
        <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-medium">
          {t('enterprise.license_status_active')}
        </span>
      </div>
      
      <div className="space-y-3 mb-6">
        <div className="flex justify-between text-sm">
          <span className="text-neutral-500">{t('enterprise.tier')}:</span>
          <span className="font-medium">{t('enterprise.enterprise_custom_tier')}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-neutral-500">{t('enterprise.license_expires')}:</span>
          <span className="font-medium">2027-12-31</span>
        </div>
      </div>
      
      <button className="w-full text-center text-blue-500 hover:text-blue-400 text-sm font-medium border border-blue-500/30 rounded py-2 hover:bg-blue-500/10 transition-colors">
        {t('enterprise.update_license_key_btn')}
      </button>
    </div>
  );
}
