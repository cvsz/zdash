import { useTranslation } from 'react-i18next';

export function useT() {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('zdash_lang', lang);
    document.documentElement.lang = lang;
  };

  return { t, i18n, changeLanguage, currentLang: i18n.language };
}
