import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import TeamRoster from '../pages/TeamRoster'
import { waitForStableUi } from './utils/settle'

describe('TeamRoster', () => {
  it('renders team roster heading', async () => {
    render(
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <TeamRoster />
      </BrowserRouter>,
    )
    await waitForStableUi()
    expect(await screen.findByText('Team Roster')).toBeTruthy()
  })
})
