import type { ReactNode } from 'react'

type GlassCardProps = {
  as?: 'div' | 'section' | 'article'
  children: ReactNode
  className?: string
  hover?: boolean
  glow?: 'cyan' | 'violet' | false
}

export default function GlassCard({ as: Component = 'div', children, className = '', hover = false, glow = false }: GlassCardProps) {
  const glowClass = glow === 'cyan' ? 'shadow-glow' : glow === 'violet' ? 'shadow-glow-violet' : ''

  return (
    <Component
      className={`rounded-card border border-border bg-panel backdrop-blur-sm shadow-glass ${glowClass} ${
        hover ? 'transition hover:-translate-y-0.5 hover:shadow-glass-lg' : ''
      } ${className}`}
    >
      {children}
    </Component>
  )
}
