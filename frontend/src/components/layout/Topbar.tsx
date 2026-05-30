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
      className="sticky top-0 z-30 border-b border-border bg-canvas/90 backdrop-blur"
      style={branding ? { borderTop: `3px solid ${branding.primary_color}` } : undefined}
    >
      <div className="flex h-14 items-center justify-between gap-3 px-4 md:px-6">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onMenuClick}
            className="rounded-button p-2 text-text-secondary transition hover:bg-panel-hover md:hidden"
            aria-label="Toggle navigation"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div>
            <p className="text-sm font-semibold text-text-primary">
              {branding?.brand_name || "Operational Dashboard"}
            </p>
            <p className="text-[11px] text-text-dim">Dry-run safe defaults active</p>
          </div>
          <div className="ml-6 hidden items-center gap-4 border-l border-border pl-6 md:flex">
            <OrganizationSwitcher />
            <WorkspaceSwitcher />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="hidden text-xs text-text-dim md:inline">
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
            className="rounded-button border border-border px-3 py-1 text-xs text-text-secondary transition hover:bg-panel-hover"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
