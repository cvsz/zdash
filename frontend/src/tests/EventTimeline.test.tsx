import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { RealtimeProvider } from '../realtime/context'
import EventTimeline from '../pages/EventTimeline'

describe('EventTimeline', () => {
  it('renders event timeline heading', () => {
    render(
      <RealtimeProvider>
        <EventTimeline />
      </RealtimeProvider>,
    )
    expect(screen.getByText('Event Timeline')).toBeTruthy()
  })
})
