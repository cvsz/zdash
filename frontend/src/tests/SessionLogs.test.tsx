import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import SessionLogs from '../pages/SessionLogs'

describe('SessionLogs', () => {
  it('renders session logs heading', () => {
    render(
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <SessionLogs />
      </BrowserRouter>,
    )
    expect(screen.getByText('Session Logs')).toBeTruthy()
  })
})
