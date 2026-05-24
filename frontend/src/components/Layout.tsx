import { Link } from 'react-router-dom'
import { ReactNode } from 'react'
import BuildInfo from './BuildInfo'
import EnvBadge from './EnvBadge'
import LiveModeBanner from './LiveModeBanner'
import OfflineBanner from './OfflineBanner'

type Props = {
  role: string
  onLogout: () => void
  liveWarning: boolean
  liveActive: boolean
  offline: boolean
  children: ReactNode
}

const links: Array<[string, string, string[]]> = [
  ['/', 'Dashboard', ['admin', 'operator', 'analyst', 'viewer']],
  ['/team', 'Team Roster', ['admin', 'operator', 'analyst', 'viewer']],
  ['/xau', 'XAU Dashboard', ['admin', 'operator', 'analyst', 'viewer']],
  ['/scheduler', 'Scheduler', ['admin', 'operator', 'analyst', 'viewer']],
  ['/backtests', 'Backtests', ['admin', 'operator', 'analyst', 'viewer']],
  ['/org', 'Org Map', ['admin', 'operator', 'analyst', 'viewer']],
  ['/logs', 'Session Logs', ['admin', 'operator', 'analyst', 'viewer']],
  ['/risk', 'Risk Panel', ['admin', 'operator', 'analyst', 'viewer']],
  ['/content', 'Content Pipeline', ['admin', 'operator', 'analyst', 'viewer']],
  ['/audit', 'Audit Logs', ['admin', 'operator']],
]

export default function Layout({ role, onLogout, liveWarning, liveActive, offline, children }: Props) {
  return (
    <div className="min-h-screen text-slate-100">
      <header className="sticky top-0 z-10 border-b border-slate-700 bg-slate-900/80 backdrop-blur">
        <nav className="mx-auto flex max-w-7xl flex-wrap items-center gap-3 px-4 py-3">
          {links
            .filter(([, , roles]) => roles.includes(role))
            .map(([href, label]) => (
              <Link key={href} to={href} className="rounded bg-panel px-3 py-1 text-sm hover:bg-slate-700">
                {label}
              </Link>
            ))}
          <button className="ml-auto rounded bg-rose-700 px-3 py-1 text-sm" onClick={onLogout}>
            Logout
          </button>
          <EnvBadge />
        </nav>
        {liveWarning && (
          <div className="bg-rose-800 px-4 py-2 text-center text-sm font-semibold">
            Live Mode Gates are not fully enabled. Trading remains in safe mode.
          </div>
        )}
        <LiveModeBanner active={liveActive} />
        <OfflineBanner offline={offline} />
      </header>
      <main className="mx-auto max-w-7xl px-4 py-5">{children}</main>
      <footer className="border-t border-slate-800 px-4 py-3">
        <div className="mx-auto flex max-w-7xl justify-end">
          <BuildInfo />
        </div>
      </footer>
    </div>
  )
}
