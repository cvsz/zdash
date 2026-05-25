import { render, screen } from '@testing-library/react';
import Workspace from '../pages/Workspace';
test('shows workspace', () => { render(<Workspace />); expect(screen.getByText('Workspace')).toBeInTheDocument(); });
