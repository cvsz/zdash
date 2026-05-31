import { render, screen } from '@testing-library/react';
import { test, expect } from 'vitest';
import Organizations from '../pages/Organizations';
import { waitForStableUi } from './utils/settle';

test('renders organizations page', async () => {
  render(<Organizations />);
  await waitForStableUi();
  expect(await screen.findByText('Organizations')).toBeInTheDocument();
});
