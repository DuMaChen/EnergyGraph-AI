import { render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import ErrorBoundary from './ErrorBoundary';
import { readClientErrorRecords } from './lib/observability';

function BrokenView(): never {
  throw new Error('Authorization=secret-value should never be persisted');
}

describe('ErrorBoundary', () => {
  afterEach(() => {
    window.localStorage.clear();
    vi.restoreAllMocks();
  });

  it('shows a recoverable fallback and stores only redacted diagnostics', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
    render(<ErrorBoundary><BrokenView /></ErrorBoundary>);
    expect(await screen.findByRole('alert')).toHaveTextContent('页面暂时无法显示');
    expect(screen.getByRole('button', { name: '重新加载' })).toBeInTheDocument();
    const records = readClientErrorRecords();
    expect(records).toHaveLength(1);
    expect(records[0]).toMatchObject({ context: 'render', category: 'render' });
    expect(JSON.stringify(records)).not.toContain('secret-value');
  });
});
