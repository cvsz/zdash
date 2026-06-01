import { useEffect, type ReactNode } from 'react';
import { useT } from '../../hooks/useT';

export function I18nProvider({ children }: { children: ReactNode }) {
  const { currentLang } = useT();
  useEffect(() => {
    document.documentElement.lang = currentLang;
  }, [currentLang]);
  return <>{children}</>;
}
