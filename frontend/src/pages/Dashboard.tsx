import { useEffect, useState } from 'react'
import StatusCard from '../components/StatusCard'
import { apiGet } from '../api/client'

export default function Dashboard() {
  const [agents, setAgents] = useState(0)
  const [jobs, setJobs] = useState(0)
  const [logs, setLogs] = useState(0)
  const [live, setLive] = useState('blocked')

  useEffect(() => {
    apiGet<{ agents: Array<unknown> }>('/api/agents', { agents: [] }).then((d) => setAgents(d.agents.length))
    apiGet<{ jobs: Array<unknown> }>('/api/scheduler/jobs', { jobs: [] }).then((d) => setJobs(d.jobs.length))
    apiGet<{ events: Array<unknown> }>('/api/logs?limit=10&offset=0', { events: [] }).then((d) => setLogs(d.events.length))
    apiGet<{ gates: { all_enabled: boolean } }>('/api/trading/live-gates', { gates: { all_enabled: false } }).then((d) =>
      setLive(d.gates.all_enabled ? 'enabled' : 'blocked'),
    )
  }, [])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">zDash Main Dashboard</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <StatusCard title="Agents" value={agents} />
        <StatusCard title="Scheduler Jobs" value={jobs} />
        <StatusCard title="Recent Logs" value={logs} />
        <StatusCard title="Live Mode" value={live} />
        <StatusCard title="Risk Guardian" value="Enabled" />
      </div>
    </div>
  )
}
