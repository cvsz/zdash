import { NavLink } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import { useT } from "../../hooks/useT";
import { LanguageSwitcher } from "../i18n/LanguageSwitcher";

type SidebarProps = {
  isOpen: boolean;
  onClose: () => void;
};

type NavItem = {
  to: string;
  labelKey: string;
  roles: string[];
};

const navItems: NavItem[] = [
  { to: "/", labelKey: "nav.dashboard", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/team", labelKey: "nav.team", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/xau", labelKey: "nav.xau", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/risk", labelKey: "nav.risk", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/alerts", labelKey: "nav.alerts", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/incidents", labelKey: "nav.incidents", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/scheduler", labelKey: "nav.scheduler", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/backtests", labelKey: "nav.backtests", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/content", labelKey: "nav.content", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/iot", labelKey: "nav.iot", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/organizations", labelKey: "nav.organizations", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/workspace", labelKey: "nav.workspace", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/workers", labelKey: "nav.workers", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/org", labelKey: "sidebar.org_map", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/logs", labelKey: "nav.logs", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/settings", labelKey: "nav.settings", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/billing", labelKey: "nav.billing", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/usage", labelKey: "nav.usage", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/marketplace", labelKey: "nav.marketplace", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/enterprise", labelKey: "nav.enterprise", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/onboarding", labelKey: "nav.onboarding", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/system/health", labelKey: "nav.system", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/zfinance", labelKey: "nav.zfinance", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/notifications", labelKey: "nav.notifications", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/workspace/live", labelKey: "sidebar.workspace_live", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/workspace/timeline", labelKey: "sidebar.workspace_timeline", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/workspace/notes", labelKey: "sidebar.workspace_notes", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/admin", labelKey: "nav.admin", roles: ["admin"] },
];

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const { user } = useAuth();
  const { t } = useT();
  const activeRole = user?.role ?? "viewer";

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border px-4 py-5">
        <h1 className="text-lg font-bold tracking-tight text-text-primary">{t('sidebar.title')}</h1>
        <p className="mt-0.5 text-[11px] text-text-dim">{t('sidebar.subtitle')}</p>
      </div>

      <nav className="flex-1 space-y-0.5 overflow-auto px-2 py-3" aria-label={t('sidebar.navigation')}>
        {navItems
          .filter((item) => item.roles.includes(activeRole))
          .map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onNavigate}
            className={({ isActive }) =>
              `block rounded-lg px-3 py-2 text-sm transition ${
                isActive
                  ? "bg-accent-cyan/10 text-accent-cyan font-semibold"
                  : "text-text-secondary hover:bg-panel-hover hover:text-text-primary"
              }`
            }
          >
            {t(item.labelKey)}
          </NavLink>
          ))}
      </nav>

      <div className="border-t border-border px-4 py-3">
        <LanguageSwitcher />
        <p className="mt-2 text-[10px] text-text-dim">
          {t('sidebar.dry_run_active')}
        </p>
      </div>
    </div>
  );
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { t } = useT();
  return (
    <>
      <aside className="hidden w-64 shrink-0 border-r border-border bg-canvas/80 backdrop-blur md:block">
        <SidebarContent />
      </aside>

      {isOpen && (
        <div className="fixed inset-0 z-40 md:hidden" role="dialog" aria-modal="true">
          <button
            type="button"
            onClick={onClose}
            className="absolute inset-0 bg-canvas/80"
            aria-label={t('sidebar.collapse')}
          />
          <aside className="relative z-50 h-full w-72 border-r border-border bg-canvas">
            <SidebarContent onNavigate={onClose} />
          </aside>
        </div>
      )}
    </>
  );
}
