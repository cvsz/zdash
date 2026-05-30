import GlassCard from './GlassCard'

type Phase = {
  id: string
  name: string
  status: 'done' | 'in-progress' | 'pending' | 'blocked'
  progress?: number
}

type PhaseProgressGridProps = {
  phases: Phase[]
  totalPhases: number
}

const statusStyles: Record<string, string> = {
  done: 'bg-state-success text-white',
  'in-progress': 'bg-accent-cyan text-canvas',
  blocked: 'bg-state-danger text-white',
  pending: 'bg-slate-800/60 text-text-dim',
}

export default function PhaseProgressGrid({ phases, totalPhases }: PhaseProgressGridProps) {
  const completed = phases.filter((p) => p.status === 'done').length
  const percent = totalPhases > 0 ? Math.round((completed / totalPhases) * 100) : 0

  return (
    <GlassCard className="p-4">
      <div className="flex items-center justify-between">
        <p className="text-[11px] font-semibold uppercase tracking-widest text-text-muted">Phase Progress</p>
        <p className="text-xs text-text-dim">
          {completed}/{totalPhases} ({percent}%)
        </p>
      </div>

      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-800/60">
        <div className="h-full rounded-full bg-gradient-to-r from-accent-cyan to-accent-violet transition-all" style={{ width: `${percent}%` }} />
      </div>

      <div className="mt-3 grid grid-cols-2 gap-1.5 sm:grid-cols-3 md:grid-cols-4">
        {phases.map((phase) => (
          <div
            key={phase.id}
            className={`flex items-center gap-1.5 rounded-md px-2 py-1 text-[11px] font-semibold ${statusStyles[phase.status] ?? statusStyles.pending}`}
          >
            {phase.status === 'done' ? '\u2713' : phase.status === 'in-progress' ? '\u25B6' : phase.status === 'blocked' ? '\u26A0' : '\u25CB'}
            <span className="truncate">{phase.name}</span>
          </div>
        ))}
      </div>
    </GlassCard>
  )
}
