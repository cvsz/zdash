import { NavLink } from "react-router-dom";

type SidebarProps = {
  isOpen: boolean;
  onClose: () => void;
};

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/team", label: "Team Roster" },
  { to: "/xau", label: "XAU Dashboard" },
  { to: "/risk", label: "Risk Panel" },
  { to: "/scheduler", label: "Scheduler" },
  { to: "/backtests", label: "Backtests" },
  { to: "/content", label: "Content Pipeline" },
  { to: "/iot", label: "IoT Control" },
  { to: "/org", label: "Org Map" },
  { to: "/logs", label: "Session Logs" },
  { to: "/settings", label: "Settings" },
];

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-slate-800 px-4 py-4">
        <h1 className="text-lg font-bold text-white">zDash</h1>
        <p className="text-xs text-slate-400">Safety-first Operations Dashboard</p>
      </div>

      <nav className="flex-1 space-y-1 overflow-auto px-3 py-4" aria-label="Primary navigation">
        {navItems.map((item) => (
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
