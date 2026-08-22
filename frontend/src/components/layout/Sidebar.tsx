import {
  Activity,
  Bell,
  Bot,
  BriefcaseBusiness,
  CalendarClock,
  ChartNoAxesCombined,
  ChevronRight,
  CircleDollarSign,
  FileClock,
  Gauge,
  HeartPulse,
  Home,
  Landmark,
  LayoutGrid,
  Megaphone,
  Network,
  RadioTower,
  Settings,
  ShieldAlert,
  ShieldCheck,
  ShoppingBag,
  Sparkles,
  Users,
  WalletCards,
  Workflow,
  Wrench,
} from "lucide-react";
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
  fallbackLabel: string;
  roles: string[];
  icon: typeof Home;
};

type NavGroup = {
  label: string;
  items: NavItem[];
};

const allRoles = ["admin", "operator", "analyst", "viewer"];

const navGroups: NavGroup[] = [
  {
    label: "Command",
    items: [
      { to: "/", labelKey: "nav.dashboard", fallbackLabel: "Overview", roles: allRoles, icon: Home },
      { to: "/team", labelKey: "nav.team", fallbackLabel: "Agent Team", roles: allRoles, icon: Users },
      { to: "/voice", labelKey: "nav.voice", fallbackLabel: "Voice Agent", roles: allRoles, icon: Bot },
      { to: "/workspace", labelKey: "nav.workspace", fallbackLabel: "Workspace", roles: allRoles, icon: LayoutGrid },
    ],
  },
  {
    label: "Operations",
    items: [
      { to: "/xau", labelKey: "nav.xau", fallbackLabel: "XAU Trading", roles: allRoles, icon: ChartNoAxesCombined },
      { to: "/risk", labelKey: "nav.risk", fallbackLabel: "Risk Control", roles: allRoles, icon: ShieldAlert },
      { to: "/alerts", labelKey: "nav.alerts", fallbackLabel: "Alerts", roles: allRoles, icon: Bell },
      { to: "/incidents", labelKey: "nav.incidents", fallbackLabel: "Incidents", roles: allRoles, icon: ShieldCheck },
      { to: "/scheduler", labelKey: "nav.scheduler", fallbackLabel: "Scheduler", roles: allRoles, icon: CalendarClock },
      { to: "/backtests", labelKey: "nav.backtests", fallbackLabel: "Backtests", roles: allRoles, icon: Gauge },
      { to: "/iot", labelKey: "nav.iot", fallbackLabel: "IoT Control", roles: allRoles, icon: RadioTower },
    ],
  },
  {
    label: "Growth",
    items: [
      { to: "/content", labelKey: "nav.content", fallbackLabel: "Content Pipeline", roles: allRoles, icon: Workflow },
      { to: "/marketing", labelKey: "nav.marketing", fallbackLabel: "Marketing Intelligence", roles: allRoles, icon: Megaphone },
      { to: "/marketplace", labelKey: "nav.marketplace", fallbackLabel: "Marketplace", roles: allRoles, icon: ShoppingBag },
      { to: "/zfinance", labelKey: "nav.zfinance", fallbackLabel: "zFinance", roles: allRoles, icon: Landmark },
    ],
  },
  {
    label: "Organization",
    items: [
      { to: "/organizations", labelKey: "nav.organizations", fallbackLabel: "Organizations", roles: allRoles, icon: BriefcaseBusiness },
      { to: "/workers", labelKey: "nav.workers", fallbackLabel: "Workers", roles: allRoles, icon: Wrench },
      { to: "/org", labelKey: "sidebar.org_map", fallbackLabel: "Org Map", roles: allRoles, icon: Network },
      { to: "/workspace/live", labelKey: "sidebar.workspace_live", fallbackLabel: "Workspace Live", roles: allRoles, icon: Activity },
      { to: "/workspace/timeline", labelKey: "sidebar.workspace_timeline", fallbackLabel: "Timeline", roles: allRoles, icon: FileClock },
      { to: "/workspace/notes", labelKey: "sidebar.workspace_notes", fallbackLabel: "Notes", roles: allRoles, icon: Sparkles },
    ],
  },
  {
    label: "Platform",
    items: [
      { to: "/system/health", labelKey: "nav.system", fallbackLabel: "System Health", roles: allRoles, icon: HeartPulse },
      { to: "/logs", labelKey: "nav.logs", fallbackLabel: "Session Logs", roles: allRoles, icon: FileClock },
      { to: "/notifications", labelKey: "nav.notifications", fallbackLabel: "Notifications", roles: allRoles, icon: Bell },
      { to: "/usage", labelKey: "nav.usage", fallbackLabel: "Usage", roles: allRoles, icon: Gauge },
      { to: "/billing", labelKey: "nav.billing", fallbackLabel: "Billing", roles: allRoles, icon: WalletCards },
      { to: "/enterprise", labelKey: "nav.enterprise", fallbackLabel: "Enterprise", roles: allRoles, icon: CircleDollarSign },
      { to: "/settings", labelKey: "nav.settings", fallbackLabel: "Settings", roles: allRoles, icon: Settings },
      { to: "/onboarding", labelKey: "nav.onboarding", fallbackLabel: "Onboarding", roles: allRoles, icon: Sparkles },
      { to: "/admin", labelKey: "nav.admin", fallbackLabel: "Admin", roles: ["admin"], icon: ShieldCheck },
    ],
  },
];

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const { user } = useAuth();
  const { t } = useT();
  const activeRole = user?.role ?? "viewer";

  return (
    <div className="flex h-full flex-col bg-canvas/95">
      <div className="border-b border-border px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl border border-state-success/30 bg-state-success/10 shadow-glow">
            <ShieldCheck className="h-5 w-5 text-state-success" />
            <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-state-success ring-2 ring-canvas" />
          </div>
          <div className="min-w-0">
            <h1 className="truncate text-base font-bold tracking-tight text-text-primary">{t('sidebar.title')}</h1>
            <p className="truncate text-[10px] uppercase tracking-[0.16em] text-text-dim">Safety-first operations</p>
          </div>
        </div>
      </div>

      <nav className="scrollbar-thin flex-1 overflow-y-auto px-3 py-4" aria-label={t('sidebar.navigation')}>
        <div className="space-y-5">
          {navGroups.map((group) => {
            const items = group.items.filter((item) => item.roles.includes(activeRole));
            if (items.length === 0) return null;

            return (
              <section key={group.label} aria-label={group.label}>
                <p className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-text-dim">
                  {group.label}
                </p>
                <div className="space-y-1">
                  {items.map((item) => {
                    const Icon = item.icon;
                    return (
                      <NavLink
                        key={item.to}
                        to={item.to}
                        end={item.to === "/"}
                        onClick={onNavigate}
                        className={({ isActive }) =>
                          `group relative flex min-h-10 items-center gap-3 rounded-xl px-3 py-2 text-sm transition-all duration-200 ${
                            isActive
                              ? "bg-panel-solid text-text-primary shadow-glass ring-1 ring-border"
                              : "text-text-secondary hover:bg-panel-hover hover:text-text-primary"
                          }`
                        }
                      >
                        {({ isActive }) => (
                          <>
                            {isActive ? (
                              <span className="absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-r-full bg-state-success" />
                            ) : null}
                            <Icon
                              className={`h-[17px] w-[17px] shrink-0 transition-colors ${
                                isActive ? "text-state-success" : "text-text-dim group-hover:text-text-secondary"
                              }`}
                              aria-hidden="true"
                            />
                            <span className="min-w-0 flex-1 truncate font-medium">
                              {t(item.labelKey, { defaultValue: item.fallbackLabel })}
                            </span>
                            {isActive ? <ChevronRight className="h-3.5 w-3.5 text-text-dim" aria-hidden="true" /> : null}
                          </>
                        )}
                      </NavLink>
                    );
                  })}
                </div>
              </section>
            );
          })}
        </div>
      </nav>

      <div className="border-t border-border px-3 py-3">
        <div className="rounded-xl border border-border bg-panel/70 px-3 py-2.5 shadow-glass">
          <div className="flex items-center justify-between gap-3">
            <div className="flex min-w-0 items-center gap-2">
              <span className="relative flex h-2 w-2 shrink-0">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-state-success opacity-50" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-state-success" />
              </span>
              <span className="truncate text-xs font-semibold text-text-primary">Runtime guarded</span>
            </div>
            <span className="rounded-pill border border-state-warning/30 bg-state-warning/10 px-2 py-0.5 text-[9px] font-bold tracking-wide text-state-warning">
              DRY RUN
            </span>
          </div>
          <div className="mt-2">
            <LanguageSwitcher />
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { t } = useT();
  return (
    <>
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 border-r border-border bg-canvas/90 backdrop-blur-xl md:block">
        <SidebarContent />
      </aside>

      {isOpen && (
        <div className="fixed inset-0 z-40 md:hidden" role="dialog" aria-modal="true">
          <button
            type="button"
            onClick={onClose}
            className="absolute inset-0 bg-canvas/85 backdrop-blur-sm"
            aria-label={t('sidebar.collapse')}
          />
          <aside className="relative z-50 h-full w-[min(20rem,88vw)] border-r border-border bg-canvas shadow-glass-lg">
            <SidebarContent onNavigate={onClose} />
          </aside>
        </div>
      )}
    </>
  );
}
