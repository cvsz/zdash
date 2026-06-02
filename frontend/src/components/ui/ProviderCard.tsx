import GlassCard from './GlassCard'
import StatusBadge from './StatusBadge'
import { useT } from '../../hooks/useT'

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
  const { t } = useT()
  const labelMap: Record<string, string> = {
    connected: t('provider_card.connected'),
    disconnected: t('provider_card.disconnected'),
    error: t('provider_card.error'),
    'dry-run': t('provider_card.dry_run'),
    disabled: t('provider_card.disabled'),
  }
  const config = statusConfig[status] ?? { variant: 'muted' as const, label: status.toUpperCase() }

  return (
    <GlassCard hover className="p-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-text-primary">{name}</p>
        <StatusBadge status={labelMap[status] ?? config.label} variant={config.variant} />
      </div>
      <p className="mt-1 text-xs text-text-dim">{description}</p>
    </GlassCard>
  )
}
