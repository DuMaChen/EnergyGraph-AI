import { Suspense } from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import ErrorBoundary from './ErrorBoundary';
import { lazyRetry } from './lazyRetry';

function Fixture({ onMount }: { onMount?: () => void }) {
  onMount?.();
  return <div>chunk-loaded</div>;
}

type FixtureModule = { default: typeof Fixture };

describe('lazyRetry', () => {
  it('renders on the first attempt when the chunk loads immediately', async () => {
    const factory: () => Promise<FixtureModule> = vi.fn(async () => ({ default: Fixture }));
    const LazyFixture = lazyRetry(factory);
    render(<Suspense fallback={<div>loading…</div>}><LazyFixture /></Suspense>);
    expect(await screen.findByText('chunk-loaded')).toBeInTheDocument();
    expect(factory).toHaveBeenCalledTimes(1);
  });

  it('recovers from a transient chunk failure and renders after the retry', async () => {
    const factory: () => Promise<FixtureModule> = vi.fn()
      .mockRejectedValueOnce(new Error('network glitch'))
      .mockResolvedValueOnce({ default: Fixture });
    const LazyFixture = lazyRetry(factory, { delaysMs: [0] });
    render(<Suspense fallback={<div>loading…</div>}><LazyFixture /></Suspense>);
    expect(await screen.findByText('chunk-loaded')).toBeInTheDocument();
    expect(factory).toHaveBeenCalledTimes(2);
  });

  it('retries up to the configured limit before surfacing the error to the boundary', async () => {
    const failure = new Error('chunk unavailable');
    const factory: () => Promise<FixtureModule> = vi.fn().mockRejectedValue(failure);
    const LazyFixture = lazyRetry(factory, { retries: 2, delaysMs: [0, 0] });
    render(
      <ErrorBoundary>
        <Suspense fallback={<div>loading…</div>}><LazyFixture /></Suspense>
      </ErrorBoundary>,
    );
    expect(await screen.findByRole('alert')).toBeInTheDocument();
    expect(factory).toHaveBeenCalledTimes(3);
  });

  it('does not retry when retries is zero', async () => {
    const factory: () => Promise<FixtureModule> = vi.fn().mockRejectedValue(new Error('chunk unavailable'));
    const LazyFixture = lazyRetry(factory, { retries: 0, delaysMs: [] });
    render(
      <ErrorBoundary>
        <Suspense fallback={<div>loading…</div>}><LazyFixture /></Suspense>
      </ErrorBoundary>,
    );
    await waitFor(() => expect(factory).toHaveBeenCalledTimes(1));
    expect(await screen.findByRole('alert')).toBeInTheDocument();
  });
});
