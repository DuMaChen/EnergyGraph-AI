import { createContext, useContext } from 'react';
import type { PlatformData } from './types';

export const AppDataContext = createContext<PlatformData | null>(null);

export function usePlatformData(): PlatformData {
  const data = useContext(AppDataContext);
  if (!data) throw new Error('PlatformDataContext is unavailable');
  return data;
}
