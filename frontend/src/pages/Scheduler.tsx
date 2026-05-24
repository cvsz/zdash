import { useEffect, useState } from 'react'
import { apiGet, apiPost } from '../api/client'
import RoleGate from '../components/RoleGate'

type Job = { id: string; name: string; interval_seconds: number; status: string }

export default function Scheduler() {
  const [jobs, setJobs] = useState<Job[]>([])
  const role = localStorage.getItem('zdash_role') || 'viewer'

  const load = () => apiGet<{ jobs: Job[] }>('/api/scheduler/jobs', { jobs: [] }).then((d) => setJobs(d.jobs))

  useEffect(() => {
    load()
  }, [])

  async function createDefault() {
    await apiPost('/api/scheduler/jobs', { name: 'trading_scan', interval_seconds: 60 }, {})
    load()
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Scheduler UI</h1>
      <RoleGate role={role} allow={['admin', 'operator']}>
        <button className="rounded bg-accent px-4 py-2 font-semibold text-slate-900" onClick={createDefault}>
          Add Trading Scan Job
        </button>
      </RoleGate>
      <div className="space-y-2">
        {jobs.map((j) => (
          <div key={j.id} className="rounded border border-slate-700 bg-panel p-3">
            {j.name} · every {j.interval_seconds}s · {j.status}
          </div>
        ))}
      </div>
    </div>
  )
}
