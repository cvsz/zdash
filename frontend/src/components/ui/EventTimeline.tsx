import GlassCard from './GlassCard'
import StatusBadge from './StatusBadge'

type TimelineEvent = {
  id: string
  time: string
  title: string
  description?: string
  type?: 'success' | 'warning' | 'danger' | 'info'
}

type EventTimelineProps = {
  title: string
  events: TimelineEvent[]
  emptyMessage?: string
  maxItems?: number
}

export default function EventTimeline({ title, events, emptyMessage = 'No events.', maxItems = 10 }: EventTimelineProps) {
  const display = events.slice(0, maxItems)

  return (
    <GlassCard className="p-4">
      <p className="text-[11px] font-semibold uppercase tracking-widest text-text-muted">{title}</p>

      {display.length === 0 ? (
        <p className="mt-3 text-xs text-text-dim">{emptyMessage}</p>
      ) : (
        <div className="mt-3 space-y-1">
          {display.map((event) => (
            <div key={event.id} className="flex items-start gap-3 rounded-lg border border-border bg-canvas-light/50 px-3 py-2">
              <div className="flex-shrink-0 pt-0.5">
                <span
                  className={`block h-2 w-2 rounded-full ${
                    event.type === 'danger' ? 'bg-state-danger'
                    : event.type === 'warning' ? 'bg-state-warning'
                    : event.type === 'success' ? 'bg-state-success'
                    : 'bg-accent-cyan'
                  }`}
                />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <p className="truncate text-sm font-medium text-text-primary">{event.title}</p>
                  <span className="flex-shrink-0 text-[11px] text-text-dim">{event.time}</span>
                </div>
                {event.description && (
                  <p className="mt-0.5 text-xs text-text-dim">{event.description}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </GlassCard>
  )
}
