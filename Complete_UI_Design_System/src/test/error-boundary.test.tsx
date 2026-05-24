import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ErrorBoundary } from '../app/components/error-boundary';

const BrokenChild = () => {
  throw new Error('Test boom');
};

describe('ErrorBoundary', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <p>safe content</p>
      </ErrorBoundary>,
    );
    expect(screen.getByText('safe content')).toBeInTheDocument();
  });

  it('renders fallback UI when a child throws', () => {
    render(
      <ErrorBoundary>
        <BrokenChild />
      </ErrorBoundary>,
    );
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
  });

  it('renders custom fallback when provided', () => {
    render(
      <ErrorBoundary fallback={<p>custom fallback</p>}>
        <BrokenChild />
      </ErrorBoundary>,
    );
    expect(screen.getByText('custom fallback')).toBeInTheDocument();
  });

  it('resets via Try Again button', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <BrokenChild />
      </ErrorBoundary>,
    );
    // Swap to safe children FIRST so the reset doesn't immediately re-throw.
    rerender(
      <ErrorBoundary>
        <p>recovered</p>
      </ErrorBoundary>,
    );
    fireEvent.click(screen.getByRole('button', { name: /try again/i }));
    expect(screen.getByText('recovered')).toBeInTheDocument();
  });
});
