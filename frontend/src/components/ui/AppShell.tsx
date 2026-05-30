import { useState, type ReactNode } from 'react'

import Sidebar from '../layout/Sidebar'
import Topbar from '../layout/Topbar'
import SafetyBanner from './SafetyBanner'

type AppShellProps = {
  children: ReactNode
  safetyText?: string
  safetyVariant?: 'info' | 'warning' | 'danger'
}

export default function AppShell({ children, safetyText, safetyVariant = 'warning' }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex min-h-screen">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="flex min-w-0 flex-1 flex-col">
        <Topbar onMenuClick={() => setSidebarOpen((p) => !p)} />

        {safetyText && (
          <SafetyBanner text={safetyText} variant={safetyVariant} />
        )}

        <div className="mx-auto w-full max-w-[1240px] flex-1 px-4 py-6 md:px-6">
          {children}
        </div>
      </main>
    </div>
  )
}
