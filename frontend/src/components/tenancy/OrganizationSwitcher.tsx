import React from "react";
import { useTenancy } from "../../hooks/useTenancy";
import { useT } from '../../hooks/useT';

export const OrganizationSwitcher: React.FC = () => {
  const { t } = useT();
  const { organizations = [], activeOrg, switchOrganization } = useTenancy();

  if (!Array.isArray(organizations) || organizations.length === 0) return null;

  return (
    <div className="flex items-center space-x-2">
      <label htmlFor="organization-switcher" className="text-sm text-gray-400">
        {t('tenancy.organization_switcher_label')}:
      </label>
      <select
        id="organization-switcher"
        name="organization"
        className="bg-slate-800 text-white border border-slate-700 rounded px-2 py-1 text-sm focus:outline-none"
        value={activeOrg?.id || ""}
        onChange={(e) => switchOrganization(e.target.value)}
      >
        {organizations.map((org) => (
          <option key={org.id} value={org.id}>
            {org.name}
          </option>
        ))}
      </select>
    </div>
  );
};
