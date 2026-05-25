import { render, screen } from '@testing-library/react';import RiskPanel from '../pages/RiskPanel';import { describe,it,expect } from 'vitest';
describe('RiskPanel',()=>{it('renders',()=>{render(<RiskPanel/>);expect(screen.getByText('Kill Switch')).toBeTruthy();expect(screen.getByText('Halt')).toBeTruthy();expect(screen.getByPlaceholderText('Resume reason')).toBeTruthy();});});
