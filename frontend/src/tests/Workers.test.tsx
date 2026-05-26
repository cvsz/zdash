import { render } from '@testing-library/react';
import { test, expect } from 'vitest';
import Workers from '../pages/Workers';

test('renders workers', () => {
  const { getByText } = render(<Workers />);
  expect(getByText('Workers')).toBeInTheDocument();
});
