import { useEffect, useState } from 'react'
import { apiGet } from '../api/client'

type Agent = { id: string; name: string; role: string; status: string }

export default function TeamRoster() {
  const [agents, setAgents] = useState<Agent[]>([])
  useEffect(() => {
    apiGet<{ agents: Agent[] }>('/api/agents', { agents: [] }).then((d) => setAgents(d.agents))
  }, [])

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold">Team Roster</h1>
      <div className="grid gap-3 md:grid-cols-2">
        {agents.map((a) => (
          <div key={a.id} className="rounded border border-slate-700 bg-panel p-4">
            <p className="font-semibold">{a.name}</p>
            <p className="text-sm text-slate-300">{a.role}</p>
            <p className="text-xs text-slate-400">{a.status}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
