import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import App from '../App';

describe('App', () => {
  it('renders app', () => {
    render(<App />);
    expect(screen.getByText('zDash')).toBeTruthy();
  });

  it('sidebar nav exists', () => {
    render(<App />);
    expect(screen.getAllByText('Dashboard')[0]).toBeTruthy();
  });

  it('dashboard route works', () => {
    render(<App />);
    expect(screen.getByText('Team Roster')).toBeTruthy();
    expect(screen.getByText('Alexander Prime')).toBeTruthy();
    expect(screen.getByText('Agents per page')).toBeTruthy();
  });
});
