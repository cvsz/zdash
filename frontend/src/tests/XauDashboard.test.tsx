import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import XauDashboard from '../pages/XauDashboard'
import { waitForStableUi } from './utils/settle'

describe('XauDashboard', () => {
  it('renders dashboard heading', async () => {
    render(<XauDashboard />)
    await waitForStableUi()
    expect(await screen.findByText('XAU Dashboard')).toBeTruthy()
  })
})
