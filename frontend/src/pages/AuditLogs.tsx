import { useEffect, useState } from 'react'
import { apiGet } from '../api/client'

type AuditItem = {
  id: string
  action: string
  actor: string
  role: string
  target: string
  created_at: string
}

export default function AuditLogs() {
  const [items, setItems] = useState<AuditItem[]>([])
  const [actorFilter, setActorFilter] = useState('')
  const [actionFilter, setActionFilter] = useState('')

  useEffect(() => {
    apiGet<{ items: AuditItem[] }>('/api/audit?limit=200&offset=0', { items: [] }).then((d: any) => setItems(d.items))
  }, [])

  const filtered = items.filter((x) => {
    const actorOk = !actorFilter || x.actor.toLowerCase().includes(actorFilter.toLowerCase())
    const actionOk = !actionFilter || x.action.toLowerCase().includes(actionFilter.toLowerCase())
    return actorOk && actionOk
  })

  return (
    <div className="space-y-3">
      <h1 className="text-2xl font-bold">Audit Logs</h1>
      <div className="flex gap-2">
        <input
          className="rounded bg-slate-900 p-2 text-sm"
          placeholder="Filter actor"
          value={actorFilter}
          onChange={(e) => setActorFilter(e.target.value)}
        />
        <input
          className="rounded bg-slate-900 p-2 text-sm"
          placeholder="Filter action"
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
        />
      </div>
      {filtered.map((item) => (
        <div key={item.id} className="rounded border border-slate-700 bg-panel p-3 text-sm">
          <div className="font-semibold">{item.action}</div>
          <div className="text-slate-300">
            {item.actor} ({item.role}) · {item.target || 'n/a'}
          </div>
          <div className="text-xs text-slate-400">{item.created_at}</div>
        </div>
      ))}
    </div>
  )
}
