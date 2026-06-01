import { render, screen } from '@testing-library/react';
import { test, expect } from 'vitest';
import Workspace from '../pages/Workspace';
import { waitForStableUi } from './utils/settle';

test('shows workspace', async () => {
  render(<Workspace />);
  await waitForStableUi();
  expect(await screen.findByText('Workspace')).toBeInTheDocument();
});
