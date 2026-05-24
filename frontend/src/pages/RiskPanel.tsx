import { useEffect, useState } from 'react'
import { apiGet, apiPostEnvelope } from '../api/client'
import RoleGate from '../components/RoleGate'

export default function RiskPanel() {
  const [risk, setRisk] = useState<Record<string, unknown>>({})
  const [reason, setReason] = useState('')
  const [message, setMessage] = useState('')
  const role = localStorage.getItem('zdash_role') || 'viewer'

  const load = () => apiGet('/api/risk/status', {}).then((d) => setRisk(d as Record<string, unknown>))

  useEffect(() => {
    load()
  }, [])

  async function doAction(path: string, prompt: string) {
    if (!reason.trim()) {
      setMessage('Reason is required')
      return
    }
    if (!window.confirm(prompt)) return
    const res = await apiPostEnvelope(path, { reason })
    if (!res?.ok) {
      setMessage(res?.error?.message || 'Action failed')
      return
    }
    setMessage('Action completed')
    load()
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Risk Panel</h1>
      <div className="rounded border border-slate-700 bg-panel p-4">
        <input
          className="w-full rounded bg-slate-900 p-2"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Enter reason for risk action"
        />
        <div className="mt-3 flex flex-wrap gap-2">
          <RoleGate role={role} allow={['admin', 'operator']}>
            <button className="rounded bg-amber-600 px-3 py-2 text-sm" onClick={() => doAction('/api/risk/halt', 'Confirm manual halt?')}>
              Manual Halt
            </button>
          </RoleGate>
          <RoleGate role={role} allow={['admin']}>
            <button className="rounded bg-rose-700 px-3 py-2 text-sm" onClick={() => doAction('/api/risk/emergency-halt', 'Confirm emergency halt?')}>
              Emergency Halt
            </button>
            <button className="rounded bg-sky-700 px-3 py-2 text-sm" onClick={() => doAction('/api/risk/resume', 'Confirm resume?')}>
              Resume
            </button>
            <button
              className="rounded bg-violet-700 px-3 py-2 text-sm"
              onClick={() => doAction('/api/risk/kill-switch-reset', 'Confirm kill-switch reset?')}
            >
              Kill-Switch Reset
            </button>
          </RoleGate>
        </div>
        {message && <p className="mt-2 text-sm text-slate-300">{message}</p>}
      </div>
      <pre className="overflow-auto rounded border border-slate-700 bg-black/40 p-3 text-xs">{JSON.stringify(risk, null, 2)}</pre>
    </div>
  )
}
