import { useState } from 'react'
import { apiPost, apiPostEnvelope } from '../api/client'
import RoleGate from '../components/RoleGate'

export default function XauDashboard() {
  const [signal, setSignal] = useState<Record<string, unknown> | null>(null)
  const [message, setMessage] = useState('')
  const role = localStorage.getItem('zdash_role') || 'viewer'

  async function runScan() {
    const data = await apiPost<{ signal: Record<string, unknown> }, object>('/api/trading/scan', {}, { signal: {} })
    setSignal(data.signal)
  }

  async function runDry() {
    if (!signal) return
    const res = await apiPostEnvelope('/api/trading/dry-run', { signal, lot_size: 0.01 })
    setMessage(res?.ok ? 'Dry-run executed' : res?.error?.message || 'Dry-run failed')
  }

  async function runLive() {
    if (!signal) return
    if (!window.confirm('Confirm LIVE execution attempt?')) return
    const res = await apiPostEnvelope('/api/trading/live-execute', { signal, lot_size: 0.01 })
    setMessage(res?.ok ? 'Live execution completed' : res?.error?.message || 'Live execution blocked')
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">XAU Dashboard</h1>
      <div className="flex gap-2">
        <button className="rounded bg-accent px-4 py-2 font-semibold text-slate-900" onClick={runScan}>
          Run Scan
        </button>
        <RoleGate role={role} allow={['admin', 'operator', 'analyst']}>
          <button className="rounded bg-emerald-700 px-4 py-2 text-sm" onClick={runDry}>
            Dry-Run Execute
          </button>
        </RoleGate>
        <RoleGate role={role} allow={['admin', 'operator']}>
          <button className="rounded bg-rose-700 px-4 py-2 text-sm" onClick={runLive}>
            Live Execute
          </button>
        </RoleGate>
      </div>
      {message && <p className="text-sm text-slate-300">{message}</p>}
      <pre className="overflow-auto rounded border border-slate-700 bg-black/40 p-3 text-xs">{JSON.stringify(signal, null, 2)}</pre>
    </div>
  )
}
