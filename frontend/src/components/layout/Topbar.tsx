import { Menu } from "lucide-react";
import React, { useState, useEffect } from "react";

import { useSystemStatus } from "../../hooks/useSystemStatus";
import { useAuth } from "../../hooks/useAuth";
import Badge from "../common/Badge";
import ConnectionStatus from "../system/ConnectionStatus";
import NotificationCenter from "../system/NotificationCenter";
import { OrganizationSwitcher } from "../tenancy/OrganizationSwitcher";
import { WorkspaceSwitcher } from "../tenancy/WorkspaceSwitcher";
import { getBrandingSettings } from "../../api/endpoints";
import { BrandingSettings } from "../../api/types";

type TopbarProps = {
  onMenuClick: () => void;
};

export default function Topbar({ onMenuClick }: TopbarProps) {
  const { data, loading } = useSystemStatus();
  const { user, logout } = useAuth();
  const [branding, setBranding] = useState<BrandingSettings | null>(null);

  useEffect(() => {
    getBrandingSettings()
      .then(setBranding)
      .catch(() => {});
  }, []);

  const systemLabel =
    loading || !data?.health?.status
      ? "Loading"
      : String(data.health.status).toUpperCase();
  const riskLabel =
    loading || !data?.risk?.risk_level
      ? "Risk Loading"
      : `Risk ${String(data.risk.risk_level).toUpperCase()}`;

  return (
    <header
      className="sticky top-0 z-30 border-b border-slate-800 bg-slate-950/80 backdrop-blur"
      style={branding ? { borderTop: `3px solid ${branding.primary_color}` } : undefined}
    >
      <div className="flex h-14 items-center justify-between gap-3 px-4 md:px-6">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onMenuClick}
            className="rounded-md p-2 text-slate-200 transition hover:bg-slate-800 md:hidden"
            aria-label="Toggle navigation"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div>
            <p className="text-sm font-semibold text-white">
              {branding?.brand_name || "Operational Dashboard"}
            </p>
            <p className="text-xs text-slate-400">Dry-run safe defaults active</p>
          </div>
          <div className="hidden md:flex items-center space-x-4 ml-6 border-l border-slate-800 pl-6">
            <OrganizationSwitcher />
            <WorkspaceSwitcher />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="hidden text-xs text-slate-400 md:inline">
            {user?.username} ({user?.role})
          </span>
          <Badge variant="success">{systemLabel}</Badge>
          <Badge variant="warning">{riskLabel}</Badge>
          <ConnectionStatus />
          <NotificationCenter />
          <button
            type="button"
            onClick={() => {
              void logout();
            }}
            className="rounded-md border border-slate-700 px-3 py-1 text-xs text-slate-200 transition hover:bg-slate-800"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
