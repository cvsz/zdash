import type { ReactNode } from 'react'

type CommandButtonProps = {
  children: ReactNode
  onClick?: () => void
  variant?: 'primary' | 'danger' | 'ghost'
  disabled?: boolean
  disabledReason?: string
  className?: string
}

const variantStyles = {
  primary: 'bg-accent-cyan/20 text-accent-cyan border-accent-cyan/40 hover:bg-accent-cyan/30',
  danger: 'bg-state-danger/20 text-state-danger border-state-danger/40 hover:bg-state-danger/30',
  ghost: 'bg-transparent text-text-secondary border-border hover:bg-slate-800/50',
}

export default function CommandButton({
  children,
  onClick,
  variant = 'ghost',
  disabled = false,
  disabledReason,
  className = '',
}: CommandButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={disabled && disabledReason ? disabledReason : undefined}
      className={`rounded-button border px-3 py-1.5 text-xs font-semibold transition disabled:cursor-not-allowed disabled:opacity-40 ${variantStyles[variant]} ${className}`}
    >
      {children}
      {disabled && disabledReason && (
        <span className="ml-1.5 text-[10px] opacity-70">({disabledReason})</span>
      )}
    </button>
  )
}
