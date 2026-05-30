import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import LiveModeBanner from '../components/LiveModeBanner'
import OfflineBanner from '../components/OfflineBanner'
import EnvBadge from '../components/EnvBadge'
import RoleGate from '../components/RoleGate'

describe('LiveModeBanner', () => {
  it('renders nothing when not active', () => {
    const { container } = render(<LiveModeBanner active={false} />)
    expect(container.innerHTML).toBe('')
  })

  it('renders live mode warning when active', () => {
    render(<LiveModeBanner active={true} />)
    expect(screen.getByText(/live mode/i)).toBeTruthy()
  })
})

describe('OfflineBanner', () => {
  it('renders nothing when online', () => {
    const { container } = render(<OfflineBanner offline={false} />)
    expect(container.innerHTML).toBe('')
  })

  it('renders offline warning when offline', () => {
    render(<OfflineBanner offline={true} />)
    expect(screen.getByText(/offline/i)).toBeTruthy()
  })
})

describe('EnvBadge', () => {
  it('renders environment badge', () => {
    vi.stubEnv('VITE_APP_ENV', 'development')
    render(<EnvBadge />)
    expect(screen.getByText('development')).toBeTruthy()
    vi.unstubAllEnvs()
  })

  it('shows production env badge', () => {
    vi.stubEnv('VITE_APP_ENV', 'production')
    render(<EnvBadge />)
    expect(screen.getByText('production')).toBeTruthy()
    vi.unstubAllEnvs()
  })

  it('defaults to development when env not set', () => {
    vi.stubEnv('VITE_APP_ENV', '')
    render(<EnvBadge />)
    expect(screen.getByText('development')).toBeTruthy()
    vi.unstubAllEnvs()
  })
})

describe('RoleGate', () => {
  it('renders children for allowed role', () => {
    render(
      <RoleGate role="admin" allow={['admin']}>
        <div data-testid="admin-panel">Admin Panel</div>
      </RoleGate>
    )
    expect(screen.getByTestId('admin-panel')).toBeTruthy()
  })

  it('hides children for disallowed role', () => {
    const { container } = render(
      <RoleGate role="viewer" allow={['admin']}>
        <div>Admin Panel</div>
      </RoleGate>
    )
    expect(container.innerHTML).toBe('')
  })

  it('allows multiple roles', () => {
    render(
      <RoleGate role="operator" allow={['admin', 'operator']}>
        <div data-testid="op-panel">Operator Panel</div>
      </RoleGate>
    )
    expect(screen.getByTestId('op-panel')).toBeTruthy()
  })
})

describe('VITE_ env variable safety', () => {
  it('VITE_ENABLE_MOCK_FALLBACK is safe boolean, not secret', () => {
    const val = import.meta.env.VITE_ENABLE_MOCK_FALLBACK
    expect(['true', 'false', true, false, undefined]).toContain(val)
  })

  it('no VITE_ variables contain secret patterns', () => {
    const secretPatterns = ['key', 'secret', 'token', 'password', 'credential', 'api_key']
    for (const [key, val] of Object.entries(import.meta.env)) {
      if (!key.startsWith('VITE_')) continue
      const lowerKey = key.toLowerCase()
      const lowerVal = String(val ?? '').toLowerCase()
      const hasSecretName = secretPatterns.some(p => lowerKey.includes(p))
      const hasSecretValue = secretPatterns.some(p => lowerVal.includes(p))
      if (hasSecretName && hasSecretValue) {
        throw new Error(`Potential secret exposed via ${key}`)
      }
    }
  })

  it('mock fallback is enabled by default', () => {
    const fromEnv = String(import.meta.env.VITE_ENABLE_MOCK_FALLBACK ?? "true").toLowerCase()
    expect(fromEnv).toBe('true')
  })
})
