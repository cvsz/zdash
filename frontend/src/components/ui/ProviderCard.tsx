import GlassCard from './GlassCard'
import StatusBadge from './StatusBadge'

type ProviderCardProps = {
  name: string
  status: 'connected' | 'disconnected' | 'error' | 'dry-run' | 'disabled'
  description: string
}

const statusConfig: Record<string, { variant: 'success' | 'warning' | 'danger' | 'info' | 'muted'; label: string }> = {
  connected: { variant: 'success', label: 'CONNECTED' },
  disconnected: { variant: 'warning', label: 'DISCONNECTED' },
  error: { variant: 'danger', label: 'ERROR' },
  'dry-run': { variant: 'info', label: 'DRY_RUN' },
  disabled: { variant: 'muted', label: 'DISABLED' },
}

export default function ProviderCard({ name, status, description }: ProviderCardProps) {
  const config = statusConfig[status] ?? { variant: 'muted' as const, label: status.toUpperCase() }

  return (
    <GlassCard hover className="p-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-text-primary">{name}</p>
        <StatusBadge status={config.label} variant={config.variant} />
      </div>
      <p className="mt-1 text-xs text-text-dim">{description}</p>
    </GlassCard>
  )
}
