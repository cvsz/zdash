import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import SessionLogs from '../pages/SessionLogs'
import { waitForStableUi } from './utils/settle'

describe('SessionLogs', () => {
  it('renders session logs heading', async () => {
    render(
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <SessionLogs />
      </BrowserRouter>,
    )
    await waitForStableUi()
    expect(await screen.findByText('Session Logs')).toBeTruthy()
  })
})
