import { render, screen } from '@testing-library/react';import WorkspaceLive from '../pages/WorkspaceLive';import { it, expect } from 'vitest';
it('renders live page',()=>{render(<WorkspaceLive/>);expect(screen.getByText(/Workspace Live/i)).toBeTruthy();});
