import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import IncidentCenter from '../pages/IncidentCenter'

describe('IncidentCenter', () => {
  it('renders incident center heading', () => {
    render(
      <BrowserRouter>
        <IncidentCenter />
      </BrowserRouter>,
    )
    expect(screen.getByText('Incident Ops')).toBeTruthy()
  })
})
