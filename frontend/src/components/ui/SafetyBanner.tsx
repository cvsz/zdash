type SafetyBannerProps = {
  text: string
  variant?: 'info' | 'warning' | 'danger'
  actions?: React.ReactNode
}

const variantStyles = {
  info: 'border-accent-cyan/30 bg-accent-cyan/8 text-accent-cyan',
  warning: 'border-state-warning/30 bg-state-warning/10 text-state-warning',
  danger: 'border-state-danger/30 bg-state-danger/10 text-state-danger',
}

export default function SafetyBanner({ text, variant = 'warning', actions }: SafetyBannerProps) {
  return (
    <div
      className={`flex items-center justify-between gap-3 border-y px-4 py-2.5 text-xs font-semibold md:px-6 ${variantStyles[variant]}`}
    >
      <div className="flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-current" />
        <span>{text}</span>
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  )
}
