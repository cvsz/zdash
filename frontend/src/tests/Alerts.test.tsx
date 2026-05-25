import { render, screen } from '@testing-library/react';
import Alerts from '../pages/Alerts';
test('renders alerts', () => { render(<Alerts />); expect(screen.getByText('Alerts')).toBeInTheDocument(); });
