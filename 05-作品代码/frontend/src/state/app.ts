import { create } from 'zustand';
import type { PlatformData, Role, Session } from '../types';

interface AppState {
  session: Session | null;
  sessionExpired: boolean;
  data: PlatformData | null;
  preview: boolean;
  sidebarOpen: boolean;
  pwaUpdateReady: boolean;
  setSession: (session: Session) => void;
  markSessionExpired: () => void;
  clearSession: () => void;
  setData: (data: PlatformData) => void;
  setPreview: (preview: boolean) => void;
  setSidebarOpen: (open: boolean) => void;
  setPwaUpdateReady: (ready: boolean) => void;
  role: () => Role;
}

export const useAppStore = create<AppState>((set, get) => ({
  session: null,
  sessionExpired: false,
  data: null,
  preview: false,
  sidebarOpen: false,
  pwaUpdateReady: false,
  setSession: (session) => set({ session, sessionExpired: false }),
  markSessionExpired: () => set({ session: null, data: null, preview: false, sessionExpired: true }),
  clearSession: () => set({ session: null, data: null, sessionExpired: false }),
  setData: (data) => set({ data }),
  setPreview: (preview) => set({ preview }),
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  setPwaUpdateReady: (pwaUpdateReady) => set({ pwaUpdateReady }),
  role: () => get().session?.role || 'student',
}));
