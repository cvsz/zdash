import GlassCard from './GlassCard'
import StatusBadge from './StatusBadge'
import CommandButton from './CommandButton'

type Gate = {
  name: string
  status: 'pass' | 'fail' | 'pending'
  detail?: string
}

type ReleaseGatePanelProps = {
  gates: Gate[]
  version?: string
  onExecute?: () => void
  canExecute?: boolean
}

export default function ReleaseGatePanel({ gates, version, onExecute, canExecute = false }: ReleaseGatePanelProps) {
  const allPass = gates.every((g) => g.status === 'pass')

  return (
    <GlassCard className="p-4" glow={allPass ? 'cyan' : false}>
      <div className="flex items-center justify-between">
        <p className="text-[11px] font-semibold uppercase tracking-widest text-text-muted">Release Gate</p>
        {version && <span className="text-xs text-text-dim">v{version}</span>}
      </div>

      <div className="mt-3 space-y-1">
        {gates.map((gate) => (
          <div key={gate.name} className="flex items-center justify-between rounded-md border border-border bg-canvas-light/30 px-3 py-1.5">
            <div className="flex items-center gap-2">
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  gate.status === 'pass' ? 'bg-state-success'
                  : gate.status === 'fail' ? 'bg-state-danger'
                  : 'bg-text-dim'
                }`}
              />
              <span className="text-xs font-medium text-text-secondary">{gate.name}</span>
            </div>
            <div className="flex items-center gap-2">
              {gate.detail && <span className="text-[11px] text-text-dim">{gate.detail}</span>}
              <StatusBadge
                status={gate.status === 'pass' ? 'PASS' : gate.status === 'fail' ? 'FAIL' : 'PENDING'}
                variant={gate.status === 'pass' ? 'success' : gate.status === 'fail' ? 'danger' : 'muted'}
                size="sm"
              />
            </div>
          </div>
        ))}
      </div>

      {onExecute && (
        <div className="mt-3 flex justify-end">
          <CommandButton
            onClick={onExecute}
            variant="primary"
            disabled={!canExecute}
            disabledReason={!canExecute ? (allPass ? 'approval required' : 'gates not passed') : undefined}
          >
            Execute Release
          </CommandButton>
        </div>
      )}
    </GlassCard>
  )
}
