import { useState } from 'react'
import { apiPost } from '../api/client'
import RoleGate from '../components/RoleGate'

type Item = { id: string; state: string; approved: boolean; [k: string]: unknown }

export default function ContentPipeline() {
  const [item, setItem] = useState<Item | null>(null)
  const [msg, setMsg] = useState('')
  const role = localStorage.getItem('zdash_role') || 'viewer'

  async function createDraft() {
    const data = await apiPost<{ item: Item }, object>(
      '/api/content/create',
      { topic: 'XAU session update', body: 'Draft market summary' },
      { item: {} as Item },
    )
    setItem(data.item)
  }

  async function step(path: string) {
    if (!item?.id) return
    const data = await apiPost<{ item: Item }, object>(path, { item_id: item.id }, { item: item })
    setItem(data.item)
    setMsg(`Updated via ${path}`)
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Content Pipeline</h1>
      <div className="flex flex-wrap gap-2">
        <RoleGate role={role} allow={['admin', 'operator', 'analyst']}>
          <button className="rounded bg-accent px-4 py-2 font-semibold text-slate-900" onClick={createDraft}>
            Create Draft
          </button>
          <button className="rounded bg-sky-700 px-3 py-2 text-sm" onClick={() => step('/api/content/generate-graphic')}>
            Generate Graphic
          </button>
        </RoleGate>
        <RoleGate role={role} allow={['admin', 'operator']}>
          <button className="rounded bg-indigo-700 px-3 py-2 text-sm" onClick={() => step('/api/content/approve')}>
            Approve
          </button>
          <button className="rounded bg-emerald-700 px-3 py-2 text-sm" onClick={() => step('/api/content/post')}>
            Post
          </button>
        </RoleGate>
      </div>
      {msg && <p className="text-sm text-slate-300">{msg}</p>}
      <pre className="overflow-auto rounded border border-slate-700 bg-black/40 p-3 text-xs">{JSON.stringify(item, null, 2)}</pre>
    </div>
  )
}
