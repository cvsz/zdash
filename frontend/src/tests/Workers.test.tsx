import { render, screen, waitForElementToBeRemoved } from '@testing-library/react';
import { test, expect } from 'vitest';
import Workers from '../pages/Workers';
import { waitForStableUi } from './utils/settle';

test('renders workers header', async () => {
  render(<Workers />);
  await waitForStableUi();
  await waitForElementToBeRemoved(() => screen.queryByText(/Loading/i), { timeout: 2000 }).catch(() => {});
  expect(await screen.findByText('Workers')).toBeInTheDocument();
});

test('renders default queue from mock data', async () => {
  render(<Workers />);
  await waitForStableUi();
  const defaultQueue = await screen.findByText('default', { exact: false });
  expect(defaultQueue).toBeInTheDocument();
});

test('renders recent tasks section', async () => {
  render(<Workers />);
  await waitForStableUi();
  const recentTasks = await screen.findByText(/Recent Tasks/);
  expect(recentTasks).toBeInTheDocument();
});
