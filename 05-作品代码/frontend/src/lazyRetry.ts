import { lazy, type ComponentType, type LazyExoticComponent } from 'react';

export interface LazyRetryOptions {
  retries?: number;
  delaysMs?: number[];
}

const DEFAULT_RETRIES = 2;
const DEFAULT_DELAYS_MS = [600, 1600];

// React's own lazy() uses ComponentType<any>; mirror it so zero-arg and
// prop-taking components both keep their exact props type.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function lazyRetry<T extends ComponentType<any>>(
  factory: () => Promise<{ default: T }>,
  options: LazyRetryOptions = {},
): LazyExoticComponent<T> {
  const retries = options.retries ?? DEFAULT_RETRIES;
  const delaysMs = options.delaysMs ?? DEFAULT_DELAYS_MS;
  let failedAttempts = 0;
  const attempt = (): Promise<{ default: T }> =>
    factory().catch((error: unknown) => {
      if (failedAttempts < retries) {
        const delay = delaysMs[failedAttempts] ?? delaysMs[delaysMs.length - 1] ?? 0;
        failedAttempts += 1;
        return new Promise<{ default: T }>((resolve, reject) => {
          window.setTimeout(() => {
            attempt().then(resolve, reject);
          }, delay);
        });
      }
      throw error;
    });
  return lazy(attempt);
}
