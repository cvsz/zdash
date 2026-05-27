import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import SystemHealth from '../pages/SystemHealth';
import { RealtimeContext } from '../realtime/context';

vi.mock('../hooks/useAuth', () => ({ useAuth: () => ({ user: { role: 'admin' } }) }));
vi.mock('../hooks/useApi', () => ({ useApi: () => ({ data: { timestamp: '2026-01-01T00:00:00Z' }, error: null }) }));

describe('SystemHealth page', () => {
  it('renders diagnostics safely', () => {
    render(<RealtimeContext.Provider value={{ state: 'connected', events: [], unread: 0, clearUnread: () => {} }}><MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><SystemHealth /></MemoryRouter></RealtimeContext.Provider>);
    expect(screen.getByText(/build mode/i)).toBeInTheDocument();
    expect(screen.getByText(/current user role/i)).toBeInTheDocument();
  });
});
