import { render, screen } from '@testing-library/react';
import { test, expect } from 'vitest';
import Workers from '../pages/Workers';

test('renders workers header', () => {
  const { getByText } = render(<Workers />);
  expect(getByText('Workers & Queues')).toBeInTheDocument();
});

test('renders default queue from mock data', async () => {
  render(<Workers />);
  const defaultQueue = await screen.findByText('default', { exact: false });
  expect(defaultQueue).toBeInTheDocument();
});

test('renders recent tasks section', async () => {
  render(<Workers />);
  const recentTasks = await screen.findByText('Recent Tasks');
  expect(recentTasks).toBeInTheDocument();
});
