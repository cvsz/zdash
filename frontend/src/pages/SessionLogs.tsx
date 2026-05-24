import { useEffect, useState } from 'react'
import LogStream from '../components/LogStream'
import { apiGet } from '../api/client'

type EventRow = { id: number; event_type: string; source: string; payload: unknown; timestamp: string }

export default function SessionLogs() {
  const [lines, setLines] = useState<string[]>([])

  useEffect(() => {
    apiGet<{ events: EventRow[] }>('/api/logs?limit=100&offset=0', { events: [] }).then((d) => {
      const formatted = d.events.map((e) => `${e.timestamp} | ${e.source} | ${e.event_type}`)
      setLines(formatted)
    })

    const token = localStorage.getItem('zdash_token') || ''
    const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const stream = new EventSource(`${base}/api/logs/stream?token=${encodeURIComponent(token)}`)
    stream.onmessage = (evt) => {
      try {
        const e = JSON.parse(evt.data) as EventRow
        setLines((prev) => [`${e.timestamp} | ${e.source} | ${e.event_type}`, ...prev].slice(0, 300))
      } catch {
        // ignore parse errors
      }
    }
    stream.onerror = () => stream.close()
    return () => stream.close()
  }, [])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Session Logs</h1>
      <LogStream lines={lines} />
    </div>
  )
}
