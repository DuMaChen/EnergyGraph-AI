import { useCallback, useEffect, useState } from 'react';

export interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>;
}

export interface PwaInstallPromptState {
  canInstall: boolean;
  install: () => Promise<void>;
}

export function usePwaInstallPrompt(): PwaInstallPromptState {
  const [promptEvent, setPromptEvent] = useState<BeforeInstallPromptEvent | null>(null);

  useEffect(() => {
    const onBeforeInstallPrompt = (event: Event) => {
      event.preventDefault();
      setPromptEvent(event as BeforeInstallPromptEvent);
    };
    const onAppInstalled = () => setPromptEvent(null);
    window.addEventListener('beforeinstallprompt', onBeforeInstallPrompt);
    window.addEventListener('appinstalled', onAppInstalled);
    return () => {
      window.removeEventListener('beforeinstallprompt', onBeforeInstallPrompt);
      window.removeEventListener('appinstalled', onAppInstalled);
    };
  }, []);

  const install = useCallback(async () => {
    if (!promptEvent) return;
    const current = promptEvent;
    setPromptEvent(null);
    try {
      current.prompt();
      await current.userChoice;
    } catch { /* prompt was dismissed or unavailable in this browser */ }
  }, [promptEvent]);

  return { canInstall: promptEvent !== null, install };
}
