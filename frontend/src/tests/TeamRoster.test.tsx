import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import TeamRoster from '../pages/TeamRoster'

describe('TeamRoster', () => {
  it('renders team roster heading', () => {
    render(
      <BrowserRouter>
        <TeamRoster />
      </BrowserRouter>,
    )
    expect(screen.getByText('Team Roster')).toBeTruthy()
  })
})
