import { render, screen } from '@testing-library/react';
import Alerts from '../pages/Alerts';
import { waitForStableUi } from './utils/settle';

test('renders alerts', async () => {
  render(<Alerts />);
  await waitForStableUi();
  expect(await screen.findByRole('heading', { name: 'Alerts', level: 2 })).toBeInTheDocument();
});
