import { render, screen } from '@testing-library/react';
import Workers from '../pages/Workers';
test('renders workers', () => { render(<Workers />); expect(screen.getByText('Workers')).toBeInTheDocument(); });
