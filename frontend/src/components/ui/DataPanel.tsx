import type { ReactNode } from 'react'
import GlassCard from './GlassCard'

type DataPanelProps = {
  title: string
  subtitle?: string
  children: ReactNode
  className?: string
}

export default function DataPanel({ title, subtitle, children, className = '' }: DataPanelProps) {
  return (
    <GlassCard className={`p-4 ${className}`}>
      <div className="mb-3">
        <p className="text-sm font-semibold text-text-primary">{title}</p>
        {subtitle && <p className="text-xs text-text-dim">{subtitle}</p>}
      </div>
      {children}
    </GlassCard>
  )
}
