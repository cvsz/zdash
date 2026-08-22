import { Menu, ShieldCheck } from "lucide-react";
import React, { useEffect, useState } from "react";

import { getBrandingSettings } from "../../api/endpoints";
import { BrandingSettings } from "../../api/types";
import { useAuth } from "../../hooks/useAuth";
import { useSystemStatus } from "../../hooks/useSystemStatus";
import { useT } from "../../hooks/useT";
import Badge from "../common/Badge";
import ConnectionStatus from "../system/ConnectionStatus";
import NotificationCenter from "../system/NotificationCenter";
import { OrganizationSwitcher } from "../tenancy/OrganizationSwitcher";
import { WorkspaceSwitcher } from "../tenancy/WorkspaceSwitcher";

type TopbarProps = {
  onMenuClick: () => void;
};

export default function Topbar({ onMenuClick }: TopbarProps) {
  const { data, loading } = useSystemStatus();
  const { user, logout } = useAuth();
  const { t } = useT();
  const [branding, setBranding] = useState<BrandingSettings | null>(null);

  useEffect(() => {
    getBrandingSettings()
      .then(setBranding)
      .catch(() => {});
  }, []);

  const systemLabel =
    loading || !data?.health?.status
      ? t("common.loading")
      : String(data.health.status).toUpperCase();
  const riskLabel =
    loading || !data?.risk?.risk_level
      ? t("topbar.risk_loading")
      : `RISK ${String(data.risk.risk_level).toUpperCase()}`;

  return (
    <header
      className="sticky top-0 z-30 border-b border-border bg-canvas/80 backdrop-blur-xl"
      style={branding ? { borderTop: `3px solid ${branding.primary_color}` } : undefined}
    >
      <div className="flex min-h-16 items-center justify-between gap-3 px-4 py-2 md:px-6 xl:px-8">
        <div className="flex min-w-0 items-center gap-3">
          <button
            type="button"
            onClick={onMenuClick}
            className="rounded-xl border border-border bg-panel/70 p-2 text-text-secondary transition hover:bg-panel-hover md:hidden"
            aria-label={t("topbar.toggle_navigation")}
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="hidden h-9 w-9 items-center justify-center rounded-xl border border-state-success/25 bg-state-success/10 sm:flex md:hidden">
            <ShieldCheck className="h-4.5 w-4.5 text-state-success" />
          </div>

          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-text-primary">
              {branding?.brand_name || t("topbar.operational_dashboard")}
            </p>
            <p className="truncate text-[10px] uppercase tracking-[0.14em] text-text-dim">
              {t("topbar.dry_run_safe_active")}
            </p>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <div className="hidden items-center gap-2 sm:flex">
            <Badge variant="success">{systemLabel}</Badge>
            <Badge variant="warning">{riskLabel}</Badge>
          </div>
          <ConnectionStatus />
          <NotificationCenter />

          <div className="hidden items-center gap-2 rounded-xl border border-border bg-panel/70 px-2.5 py-1.5 lg:flex">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-accent-cyan/10 text-[10px] font-bold uppercase text-accent-cyan ring-1 ring-accent-cyan/20">
              {(user?.username ?? "OP").slice(0, 2)}
            </div>
            <div className="max-w-32 leading-tight">
              <p className="truncate text-xs font-semibold text-text-primary">{user?.username ?? "operator"}</p>
              <p className="truncate text-[10px] uppercase tracking-wide text-text-dim">{user?.role ?? "viewer"}</p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => {
              void logout();
            }}
            className="rounded-xl border border-border bg-panel/60 px-3 py-2 text-xs font-medium text-text-secondary transition hover:border-state-danger/30 hover:bg-state-danger/10 hover:text-state-danger"
          >
            {t("topbar.logout")}
          </button>
        </div>
      </div>

      <div className="flex items-center gap-4 overflow-x-auto border-t border-border/70 px-4 py-2 md:px-6">
        <OrganizationSwitcher />
        <WorkspaceSwitcher />
      </div>
    </header>
  );
}
