import { render, screen } from '@testing-library/react';import Scheduler from '../pages/Scheduler';import { describe,it,expect } from 'vitest';
describe('Scheduler',()=>{it('renders',()=>{render(<Scheduler/>);expect(screen.getByText('Job table')).toBeTruthy();expect(screen.getByText('Run job')).toBeTruthy();expect(screen.getByText(/iot_power_cycle/)).toBeTruthy();});});
