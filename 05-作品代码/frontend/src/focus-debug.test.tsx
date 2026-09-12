import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';
import { useAppStore } from './state/app';

describe('focus debug', () => {
  beforeEach(() => {
    useAppStore.setState({ session: null, sessionExpired: false, data: null, preview: false, sidebarOpen: false });
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('preview test')));
    window.history.pushState({}, '', '/');
  });
  it('traces focus', async () => {
    await act(async () => { render(<App />); });
    const search = (await screen.findByLabelText('搜索课程资料')) as HTMLInputElement;
    fireEvent.keyDown(window, { key: '/' });
    console.log('DBG after /1:', document.activeElement?.tagName);
    fireEvent.change(search, { target: { value: '储能' } });
    fireEvent.submit(search.closest('form') as HTMLFormElement);
    await waitFor(() => expect(window.location.pathname).toBe('/search'));
    console.log('DBG after submit1:', window.location.pathname + window.location.search, document.activeElement?.tagName);
    fireEvent.keyDown(window, { key: '/' });
    console.log('DBG after /2:', document.activeElement?.tagName);
    fireEvent.submit(search.closest('form') as HTMLFormElement);
    console.log('DBG after submit2:', window.location.pathname + window.location.search, document.activeElement?.tagName);
  });
});
