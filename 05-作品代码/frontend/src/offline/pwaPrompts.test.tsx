import { act, fireEvent, render, renderHook, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { usePwaInstallPrompt, type BeforeInstallPromptEvent } from './usePwaInstallPrompt';
import { InstallPromptButton, UpdatePromptBanner } from './pwaPrompts';

function dispatch(type: string): void {
  act(() => { window.dispatchEvent(new Event(type)); });
}

function makePromptEvent() {
  const prompt = vi.fn(async () => undefined);
  const userChoice = Promise.resolve({ outcome: 'accepted', platform: 'web' });
  const event = new Event('beforeinstallprompt') as unknown as BeforeInstallPromptEvent;
  Object.assign(event, { prompt, userChoice });
  return { prompt, event };
}

describe('usePwaInstallPrompt', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('starts with no install prompt available', async () => {
    const { result } = renderHook(() => usePwaInstallPrompt());
    expect(result.current.canInstall).toBe(false);
    await expect(result.current.install()).resolves.toBeUndefined();
  });

  it('captures the beforeinstallprompt event and exposes install', async () => {
    const { prompt, event } = makePromptEvent();
    const { result } = renderHook(() => usePwaInstallPrompt());
    act(() => { window.dispatchEvent(event); });
    expect(result.current.canInstall).toBe(true);
    await act(async () => { await result.current.install(); });
    expect(prompt).toHaveBeenCalledTimes(1);
    expect(result.current.canInstall).toBe(false);
  });

  it('hides the install prompt after appinstalled', () => {
    const { result } = renderHook(() => usePwaInstallPrompt());
    act(() => { window.dispatchEvent(makePromptEvent().event); });
    expect(result.current.canInstall).toBe(true);
    dispatch('appinstalled');
    expect(result.current.canInstall).toBe(false);
  });
});

describe('InstallPromptButton', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('renders nothing while no install prompt is available', () => {
    render(<InstallPromptButton />);
    expect(screen.queryByRole('button', { name: '安装应用' })).not.toBeInTheDocument();
  });

  it('renders the install button and prompts on click', () => {
    const { prompt, event } = makePromptEvent();
    render(<InstallPromptButton />);
    act(() => { window.dispatchEvent(event); });
    const button = screen.getByRole('button', { name: '安装应用' });
    fireEvent.click(button);
    expect(prompt).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole('button', { name: '安装应用' })).not.toBeInTheDocument();
  });
});

describe('UpdatePromptBanner', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('renders nothing when no update is available', () => {
    render(<UpdatePromptBanner visible={false} />);
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('shows the update banner and refreshes via the provided handler', () => {
    const onRefresh = vi.fn();
    render(<UpdatePromptBanner visible onRefresh={onRefresh} />);
    expect(screen.getByText('发现新版本')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '立即刷新' }));
    expect(onRefresh).toHaveBeenCalledTimes(1);
  });
});
