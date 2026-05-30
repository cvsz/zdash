import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import XauDashboard from '../pages/XauDashboard'

describe('XauDashboard', () => {
  it('renders dashboard heading', () => {
    render(<XauDashboard />)
    expect(screen.getByText('XAU Dashboard')).toBeTruthy()
  })
})
