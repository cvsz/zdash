import { NavLink } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";

type SidebarProps = {
  isOpen: boolean;
  onClose: () => void;
};

type NavItem = {
  to: string;
  label: string;
  roles: string[];
};

const navItems: NavItem[] = [
  { to: "/", label: "Dashboard", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/team", label: "Team Roster", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/xau", label: "XAU Dashboard", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/risk", label: "Risk Panel", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/alerts", label: "Alerts", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/incidents", label: "Incident Ops", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/scheduler", label: "Scheduler", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/backtests", label: "Backtests", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/content", label: "Content Pipeline", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/iot", label: "IoT Control", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/organizations", label: "Organizations", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/workspace", label: "Workspace", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/workers", label: "Workers", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/org", label: "Org Map", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/logs", label: "Session Logs", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/settings", label: "Settings", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/billing", label: "Billing", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/usage", label: "Usage", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/marketplace", label: "Marketplace", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/enterprise", label: "Enterprise", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/onboarding", label: "Onboarding", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/system/health", label: "System Health", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/notifications", label: "Notifications", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/workspace/live", label: "Workspace Live", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/workspace/timeline", label: "Workspace Timeline", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/workspace/notes", label: "Workspace Notes", roles: ["admin", "operator", "analyst", "viewer"] },
  { to: "/admin", label: "Admin", roles: ["admin"] },
];

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const { user } = useAuth();
  const activeRole = user?.role ?? "viewer";

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-slate-800 px-4 py-4">
        <h1 className="text-lg font-bold text-white">zDash</h1>
        <p className="text-xs text-slate-400">Safety-first Operations Dashboard</p>
      </div>

      <nav className="flex-1 space-y-1 overflow-auto px-3 py-4" aria-label="Primary navigation">
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
                  ? "bg-cyan-500/20 text-cyan-100"
                  : "text-slate-300 hover:bg-slate-800 hover:text-slate-100"
              }`
            }
          >
            {item.label}
          </NavLink>
          ))}
      </nav>
    </div>
  );
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <>
      <aside className="hidden w-64 shrink-0 border-r border-slate-800 bg-slate-950/70 backdrop-blur md:block">
        <SidebarContent />
      </aside>

      {isOpen && (
        <div className="fixed inset-0 z-40 md:hidden" role="dialog" aria-modal="true">
          <button
            type="button"
            onClick={onClose}
            className="absolute inset-0 bg-slate-950/70"
            aria-label="Close navigation"
          />
          <aside className="relative z-50 h-full w-72 border-r border-slate-800 bg-slate-950">
            <SidebarContent onNavigate={onClose} />
          </aside>
        </div>
      )}
    </>
  );
}
