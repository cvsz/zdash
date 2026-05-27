import { render, screen } from '@testing-library/react';import WorkspaceTimeline from '../pages/WorkspaceTimeline';import { it, expect } from 'vitest';
it('renders timeline page',()=>{render(<WorkspaceTimeline/>);expect(screen.getByText(/Workspace Timeline/i)).toBeTruthy();});
