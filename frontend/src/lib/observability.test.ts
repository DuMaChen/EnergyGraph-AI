import { beforeEach, describe, expect, it, vi } from 'vitest';
import { readClientErrorRecords, reportClientError } from './observability';

describe('client diagnostics', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('keeps only bounded, non-sensitive error metadata', () => {
    const listener = vi.fn();
    window.addEventListener('platform:error', listener);
    for (let index = 0; index < 25; index += 1) {
      reportClientError(new Error(`model answer ${index} Authorization=secret`), 'network');
    }
    const records = readClientErrorRecords();
    expect(records).toHaveLength(20);
    expect(records[0]?.category).toBe('network');
    expect(JSON.stringify(records)).not.toContain('secret');
    expect(listener).toHaveBeenCalledTimes(25);
    window.removeEventListener('platform:error', listener);
  });
});
