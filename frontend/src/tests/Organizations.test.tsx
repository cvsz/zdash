import { render, screen } from '@testing-library/react';
import Organizations from '../pages/Organizations';
test('renders organizations page', () => { render(<Organizations />); expect(screen.getByText('Organizations')).toBeInTheDocument(); });
