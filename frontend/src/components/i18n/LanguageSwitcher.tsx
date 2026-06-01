import { useT } from '../../hooks/useT';

export function LanguageSwitcher() {
  const { t, currentLang, changeLanguage } = useT();
  return (
    <select
      id="lang-switcher"
      name="lang-switcher"
      value={currentLang}
      onChange={(e) => changeLanguage(e.target.value)}
      className="bg-neutral-800 text-neutral-300 text-xs border border-neutral-700 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
      aria-label={t('common.language')}
    >
      <option value="en">EN</option>
      <option value="th">TH</option>
    </select>
  );
}
