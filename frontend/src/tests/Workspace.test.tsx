import { render } from '@testing-library/react';
import { test, expect } from 'vitest';
import Workspace from '../pages/Workspace';

test('shows workspace', () => {
  const { getByText } = render(<Workspace />);
  expect(getByText('Workspace Overview')).toBeInTheDocument();
});
