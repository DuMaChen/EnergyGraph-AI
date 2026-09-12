import { useEffect, type RefObject } from 'react';

function isEditableTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false;
  const tag = target.tagName;
  return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || target.isContentEditable;
}

export function useSearchShortcut(inputRef: RefObject<HTMLInputElement | null>, onEscape?: () => void): void {
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.defaultPrevented) return;
      if (event.metaKey || event.ctrlKey || event.altKey) return;
      const input = inputRef.current;
      if (event.key === '/' && input && !isEditableTarget(event.target)) {
        event.preventDefault();
        input.focus();
        input.select();
      } else if (event.key === 'Escape' && input && document.activeElement === input) {
        event.preventDefault();
        onEscape?.();
        input.blur();
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [inputRef, onEscape]);
}
