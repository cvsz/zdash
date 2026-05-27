import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import ErrorBoundary from '../components/system/ErrorBoundary';

function Broken() {
  throw new Error('fail');
}

describe('ErrorBoundary', () => {
  it('renders fallback UI when child throws', () => {
    render(<ErrorBoundary><Broken /></ErrorBoundary>);
    expect(screen.getByText(/unexpected error/i)).toBeInTheDocument();
  });
});
