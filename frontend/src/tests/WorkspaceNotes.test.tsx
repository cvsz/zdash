import { render, screen } from '@testing-library/react';import WorkspaceNotes from '../pages/WorkspaceNotes';import { it, expect } from 'vitest';
it('renders notes page',()=>{render(<WorkspaceNotes/>);expect(screen.getByText(/Workspace Notes/i)).toBeTruthy();});
