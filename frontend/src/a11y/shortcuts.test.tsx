import { act, renderHook } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { RefObject } from 'react';
import { useSearchShortcut } from './shortcuts';

function mountHook() {
  const input = document.createElement('input');
  document.body.appendChild(input);
  const ref: RefObject<HTMLInputElement | null> = { current: input };
  const onEscape = vi.fn();
  const hook = renderHook(() => useSearchShortcut(ref, onEscape));
  return { input, onEscape, ...hook };
}

afterEach(() => {
  vi.restoreAllMocks();
  document.body.innerHTML = '';
});

describe('useSearchShortcut', () => {
  it('focuses and selects the search input when "/" is pressed outside form controls', () => {
    const { input } = mountHook();
    act(() => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: '/' }));
    });
    expect(document.activeElement).toBe(input);
    expect(input.selectionStart).toBe(0);
    expect(input.selectionEnd).toBe(input.value.length);
  });

  it('ignores "/" while the user is typing in an input', () => {
    const { input } = mountHook();
    act(() => {
      input.dispatchEvent(new KeyboardEvent('keydown', { key: '/', bubbles: true }));
    });
    expect(document.activeElement).not.toBe(input);
  });

  it('ignores "/" when a modifier key is held', () => {
    const { input } = mountHook();
    act(() => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: '/', ctrlKey: true }));
      window.dispatchEvent(new KeyboardEvent('keydown', { key: '/', metaKey: true }));
      window.dispatchEvent(new KeyboardEvent('keydown', { key: '/', altKey: true }));
    });
    expect(document.activeElement).not.toBe(input);
  });

  it('clears and blurs the search input on Escape while focused', () => {
    const { input, onEscape } = mountHook();
    input.value = '储能';
    act(() => { input.focus(); });
    act(() => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    });
    expect(onEscape).toHaveBeenCalledTimes(1);
    expect(document.activeElement).not.toBe(input);
  });

  it('clears and blurs on Escape when the event target is the focused input itself', () => {
    const { input, onEscape } = mountHook();
    input.value = '储能';
    act(() => { input.focus(); });
    act(() => {
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    });
    expect(onEscape).toHaveBeenCalledTimes(1);
    expect(document.activeElement).not.toBe(input);
  });

  it('does nothing for Escape when the search input is not focused', () => {
    const { onEscape } = mountHook();
    act(() => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    });
    expect(onEscape).not.toHaveBeenCalled();
  });

  it('ignores unrelated keys', () => {
    const { input } = mountHook();
    act(() => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
    });
    expect(document.activeElement).not.toBe(input);
  });
});
