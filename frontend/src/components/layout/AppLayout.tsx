import { useState, type ReactNode } from "react";

import SafetyBanner from "../ui/SafetyBanner";
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
    <div className="flex min-h-screen">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="flex min-w-0 flex-1 flex-col">
        <Topbar onMenuClick={() => setSidebarOpen((previous) => !previous)} />

        {showSafetyBanners && (
          <SafetyBanner text={getSafetyBannerText()} variant="warning" />
        )}

        <div className="mx-auto w-full max-w-[1240px] flex-1 px-4 py-6 md:px-6">
          {children}
        </div>
      </main>
    </div>
  );
}
