import { useState, type ReactNode } from "react";

import { getSafetyBannerText } from "../../utils/safety";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

type AppLayoutProps = {
  children: ReactNode;
};

const showSafetyBanners =
  String(import.meta.env.VITE_SHOW_SAFETY_BANNERS ?? "true").toLowerCase() ===
  "true";

export default function AppLayout({ children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen text-slate-100">
      <div className="flex min-h-screen">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="min-w-0 flex-1">
          <Topbar onMenuClick={() => setSidebarOpen((previous) => !previous)} />

          {showSafetyBanners && (
            <div className="border-y border-amber-300/30 bg-amber-500/10 px-4 py-2 text-xs font-semibold text-amber-100 md:px-6">
              {getSafetyBannerText()}
            </div>
          )}

          <div className="mx-auto w-full max-w-[1240px] px-4 py-6 md:px-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
