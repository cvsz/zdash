import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import Settings from '../pages/Settings'
import { waitForStableUi } from './utils/settle'

vi.mock('../hooks/useAuth', async () => {
  const actual = await vi.importActual('../hooks/useAuth')
  return {
    ...actual as any,
    useAuth: () => ({
      user: { username: 'admin', role: 'admin' },
      mode: 'dev',
      login: vi.fn(),
      logout: vi.fn(),
    }),
  }
})

describe('Settings', () => {
  it('renders settings heading', async () => {
    render(<Settings />)
    await waitForStableUi()
    expect(await screen.findByText('Settings')).toBeTruthy()
  })
})
