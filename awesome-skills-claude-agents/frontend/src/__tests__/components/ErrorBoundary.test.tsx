import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorBoundary, ErrorFallback, ApiError, ErrorToast } from '../../components/common/ErrorBoundary';
import { ErrorCodes } from '../../types';
import type { ErrorResponse } from '../../types';

// Component that throws an error for testing ErrorBoundary
function ThrowError({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error message');
  }
  return <div>Content rendered successfully</div>;
}

describe('ErrorBoundary', () => {
  // Suppress console.error for expected errors in tests
  const originalError = console.error;
  beforeEach(() => {
    console.error = vi.fn();
  });

  afterEach(() => {
    console.error = originalError;
  });

  it('renders children when no error occurs', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Content rendered successfully')).toBeInTheDocument();
  });

  it('renders fallback UI when error occurs', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });

  it('renders custom fallback when provided', () => {
    render(
      <ErrorBoundary fallback={<div>Custom error fallback</div>}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Custom error fallback')).toBeInTheDocument();
  });

  it('calls onError callback when error occurs', () => {
    const onError = vi.fn();

    render(
      <ErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(onError).toHaveBeenCalled();
    expect(onError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        componentStack: expect.any(String)
      })
    );
  });

  it('calls onRetry when retry button is clicked', () => {
    const onRetry = vi.fn();

    render(
      <ErrorBoundary onRetry={onRetry}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    const retryButton = screen.getByRole('button', { name: /try again/i });
    fireEvent.click(retryButton);

    expect(onRetry).toHaveBeenCalled();
  });
});

describe('ErrorFallback', () => {
  it('renders error message', () => {
    const error = new Error('Custom error message');
    render(<ErrorFallback error={error} />);

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Custom error message')).toBeInTheDocument();
  });

  it('renders default message when error is null', () => {
    render(<ErrorFallback error={null} />);

    expect(screen.getByText('An unexpected error occurred')).toBeInTheDocument();
  });

  it('renders retry button when onRetry is provided', () => {
    const onRetry = vi.fn();
    render(<ErrorFallback error={null} onRetry={onRetry} />);

    const retryButton = screen.getByRole('button', { name: /try again/i });
    expect(retryButton).toBeInTheDocument();

    fireEvent.click(retryButton);
    expect(onRetry).toHaveBeenCalled();
  });

  it('does not render retry button when onRetry is not provided', () => {
    render(<ErrorFallback error={null} />);

    expect(screen.queryByRole('button', { name: /try again/i })).not.toBeInTheDocument();
  });
});

describe('ApiError', () => {
  const sampleError: ErrorResponse = {
    code: ErrorCodes.AGENT_NOT_FOUND,
    message: 'Agent not found',
    detail: 'The agent with ID xyz does not exist',
    suggestedAction: 'Please check the agent ID',
    requestId: 'req-123',
  };

  it('renders error message and details', () => {
    render(<ApiError error={sampleError} />);

    expect(screen.getByText('Agent not found')).toBeInTheDocument();
    expect(screen.getByText('The agent with ID xyz does not exist')).toBeInTheDocument();
    expect(screen.getByText('Please check the agent ID')).toBeInTheDocument();
  });

  it('renders request ID when provided', () => {
    render(<ApiError error={sampleError} />);

    expect(screen.getByText('req-123')).toBeInTheDocument();
  });

  it('renders retry button when onRetry is provided', () => {
    const onRetry = vi.fn();
    render(<ApiError error={sampleError} onRetry={onRetry} />);

    const retryButton = screen.getByRole('button', { name: /try again/i });
    fireEvent.click(retryButton);

    expect(onRetry).toHaveBeenCalled();
  });

  it('renders dismiss button when onDismiss is provided', () => {
    const onDismiss = vi.fn();
    render(<ApiError error={sampleError} onDismiss={onDismiss} />);

    const dismissButton = screen.getByRole('button', { name: /dismiss/i });
    fireEvent.click(dismissButton);

    expect(onDismiss).toHaveBeenCalled();
  });

  it('renders compact version correctly', () => {
    render(<ApiError error={sampleError} compact />);

    expect(screen.getByText('Agent not found')).toBeInTheDocument();
    // In compact mode, detail should not be visible
    expect(screen.queryByText('Please check the agent ID')).not.toBeInTheDocument();
  });

  it('handles different error codes with appropriate icons', () => {
    const authError: ErrorResponse = {
      code: ErrorCodes.AUTH_TOKEN_EXPIRED,
      message: 'Token expired',
    };

    const { rerender } = render(<ApiError error={authError} />);
    // Auth errors should show lock icon
    expect(screen.getByText('Token expired')).toBeInTheDocument();

    const rateLimitError: ErrorResponse = {
      code: ErrorCodes.RATE_LIMIT_EXCEEDED,
      message: 'Too many requests',
    };

    rerender(<ApiError error={rateLimitError} />);
    expect(screen.getByText('Too many requests')).toBeInTheDocument();
  });
});

describe('ErrorToast', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  const toastError: ErrorResponse = {
    code: ErrorCodes.SERVER_ERROR,
    message: 'Server error',
  };

  it('renders toast with error message', () => {
    const onDismiss = vi.fn();
    render(<ErrorToast error={toastError} onDismiss={onDismiss} />);

    expect(screen.getByText('Server error')).toBeInTheDocument();
  });

  it('auto-dismisses after specified duration', () => {
    const onDismiss = vi.fn();
    render(<ErrorToast error={toastError} onDismiss={onDismiss} autoHideDuration={3000} />);

    expect(onDismiss).not.toHaveBeenCalled();

    vi.advanceTimersByTime(3000);

    expect(onDismiss).toHaveBeenCalled();
  });

  it('does not auto-dismiss when duration is 0', () => {
    const onDismiss = vi.fn();
    render(<ErrorToast error={toastError} onDismiss={onDismiss} autoHideDuration={0} />);

    vi.advanceTimersByTime(10000);

    expect(onDismiss).not.toHaveBeenCalled();
  });

  it('can be manually dismissed', () => {
    const onDismiss = vi.fn();
    render(<ErrorToast error={toastError} onDismiss={onDismiss} />);

    const closeButton = screen.getByRole('button');
    fireEvent.click(closeButton);

    expect(onDismiss).toHaveBeenCalled();
  });
});
