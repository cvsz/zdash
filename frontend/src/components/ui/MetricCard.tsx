import GlassCard from './GlassCard'
import StatusBadge from './StatusBadge'

type MetricCardProps = {
  title: string
  value: string | number
  subtitle?: string
  trend?: 'up' | 'down' | 'flat'
  trendLabel?: string
  variant?: 'success' | 'warning' | 'danger' | 'info'
  badge?: string
}

function TrendIcon({ trend }: { trend: 'up' | 'down' | 'flat' }) {
  return (
    <span
      className={`inline-block text-xs ${
        trend === 'up' ? 'text-state-success' : trend === 'down' ? 'text-state-danger' : 'text-text-muted'
      }`}
    >
      {trend === 'up' ? '\u2191' : trend === 'down' ? '\u2193' : '\u2192'}
    </span>
  )
}

export default function MetricCard({ title, value, subtitle, trend, trendLabel, variant, badge }: MetricCardProps) {
  return (
    <GlassCard className="p-4">
      <div className="flex items-start justify-between">
        <p className="text-[11px] font-semibold uppercase tracking-widest text-text-muted">{title}</p>
        {badge && <StatusBadge status={badge} variant={variant} />}
      </div>
      <p className={`mt-2 text-2xl font-bold tracking-tight ${variant === 'danger' ? 'text-state-danger' : variant === 'warning' ? 'text-state-warning' : 'text-text-primary'}`}>
        {value}
      </p>
      {(subtitle || trend) && (
        <div className="mt-1 flex items-center gap-1.5 text-xs text-text-dim">
          {trend && <TrendIcon trend={trend} />}
          {trendLabel && <span>{trendLabel}</span>}
          {subtitle && <span>{subtitle}</span>}
        </div>
      )}
    </GlassCard>
  )
}
