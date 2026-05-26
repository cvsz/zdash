import { render } from '@testing-library/react';
import { test, expect } from 'vitest';
import Organizations from '../pages/Organizations';

test('renders organizations page', () => {
  const { getByText } = render(<Organizations />);
  expect(getByText('Organizations')).toBeInTheDocument();
});
