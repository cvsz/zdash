import { useState, type ReactNode } from "react";

import { useT } from "../../hooks/useT";
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
  const { t } = useT();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="relative flex min-h-screen bg-canvas text-text-secondary">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-mission-grid opacity-45" aria-hidden />
      <div className="pointer-events-none fixed inset-0 -z-10 bg-mission-glow" aria-hidden />

      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="relative flex min-w-0 flex-1 flex-col">
        <Topbar onMenuClick={() => setSidebarOpen((previous) => !previous)} />

        {showSafetyBanners && (
          <div className="px-4 pt-3 md:px-6">
            <SafetyBanner text={getSafetyBannerText()} variant="warning" />
          </div>
        )}

        <div className="mx-auto w-full max-w-[1480px] flex-1 px-4 py-5 md:px-6 md:py-6 xl:px-8">
          {children}
        </div>

        <footer className="border-t border-border bg-canvas/80 px-4 py-3 backdrop-blur-xl md:px-6">
          <div className="mx-auto flex w-full max-w-[1480px] flex-col items-center justify-between gap-2 text-[11px] text-text-dim sm:flex-row">
            <div className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-state-success" />
              <span>{t('common.footer', { version: '2.0.2' })}</span>
            </div>
            <span className="font-mono uppercase tracking-[0.12em]">safety-first mission control</span>
          </div>
        </footer>
      </main>
    </div>
  );
}
