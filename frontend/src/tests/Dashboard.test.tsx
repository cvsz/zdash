import { render, screen } from '@testing-library/react';import Dashboard from '../pages/Dashboard';import { describe,it,expect } from 'vitest';
describe('Dashboard',()=>{it('renders cards',()=>{render(<Dashboard/>);expect(screen.getByText('Janie Server')).toBeTruthy();expect(screen.getByText('Guardian Risk')).toBeTruthy();expect(screen.getByText('Content Pipeline')).toBeTruthy();});});
