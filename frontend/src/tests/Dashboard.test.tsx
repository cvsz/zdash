import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import Dashboard from '../pages/Dashboard';

describe('Dashboard', () => {
  it('renders team roster on the main dashboard', () => {
    render(<Dashboard />);

    expect(screen.getByText('Team Roster')).toBeTruthy();
    expect(screen.getByText('Alexander Prime')).toBeTruthy();
    expect(screen.getByText('Sophia Lane')).toBeTruthy();
    expect(screen.getByText('Agents per page')).toBeTruthy();
  });
});
