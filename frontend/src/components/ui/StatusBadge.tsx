type StatusBadgeProps = {
  status: string
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'muted'
  size?: 'sm' | 'md'
  pulsing?: boolean
}

const variantStyles: Record<string, string> = {
  success: 'bg-state-success/15 text-state-success border-state-success/30',
  warning: 'bg-state-warning/15 text-state-warning border-state-warning/30',
  danger: 'bg-state-danger/15 text-state-danger border-state-danger/30',
  info: 'bg-state-info/15 text-state-info border-state-info/30',
  muted: 'bg-slate-800/50 text-text-muted border-border',
}

export default function StatusBadge({ status, variant = 'muted', size = 'sm', pulsing = false }: StatusBadgeProps) {
  const sizeClass = size === 'sm' ? 'px-2.5 py-0.5 text-[11px]' : 'px-3 py-1 text-xs'

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-pill border font-semibold tracking-wide uppercase ${variantStyles[variant] ?? variantStyles.muted} ${sizeClass} ${pulsing ? 'animate-pulse' : ''}`}
    >
      {pulsing && <span className="h-1.5 w-1.5 rounded-full bg-current" />}
      {status}
    </span>
  )
}
