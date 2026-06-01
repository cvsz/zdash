import { useState } from "react";
import {
  getZFinanceOverview,
  getZFinanceSearch,
  type ZFinanceOverview,
  type ZFinanceInstrument,
  type ZFinanceSection,
} from "../api/zFinance";
import Badge from "../components/common/Badge";
import SectionCard from "../components/common/SectionCard";
import PageHeader from "../components/layout/PageHeader";
import { useApi } from "../hooks/useApi";
import { useT } from "../hooks/useT";

export default function ZFinance() {
  const { t } = useT();
  const { data: overview, loading, error } = useApi(getZFinanceOverview, []);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResult, setSearchResult] = useState<{ query: string; url: string } | null>(null);
  const [searching, setSearching] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = searchQuery.trim();
    if (!q) return;
    setSearching(true);
    try {
      const result = await getZFinanceSearch(q);
      setSearchResult(result);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6 text-text-primary">
      <PageHeader
        title={t('zfinance.title')}
        subtitle={t('zfinance.subtitle')}
      />

      <div className="flex flex-wrap gap-2">
        <Badge variant="warning">{t('zfinance.read_only')}</Badge>
        <Badge variant="warning">{t('zfinance.no_scraping')}</Badge>
        <Badge variant="warning">{t('zfinance.not_financial_advice')}</Badge>
        {overview && (
          <Badge variant="muted">{overview.mode}</Badge>
        )}
      </div>

      {error && (
        <div className="p-4 bg-state-danger/10 border border-state-danger/20 text-state-danger rounded-xl text-sm font-semibold">
          {t('common.error')}: {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-4">
          <div className="h-48 bg-panel/50 rounded-xl animate-pulse" />
          <div className="h-64 bg-panel/50 rounded-xl animate-pulse" />
        </div>
      ) : overview ? (
        <>
          <SectionCard title={t('zfinance.provider_mode')}>
            <div className="text-sm text-text-secondary space-y-1">
              <p><span className="font-semibold text-text-primary">{t('zfinance.provider')}:</span> {overview.provider}</p>
              <p><span className="font-semibold text-text-primary">{t('zfinance.mode')}:</span> {overview.mode}</p>
              <p><span className="font-semibold text-text-primary">{t('zfinance.scraping')}:</span> {t('zfinance.disabled')}</p>
              <p><span className="font-semibold text-text-primary">{t('zfinance.base_url')}:</span>{" "}
                <a
                  href={overview.base_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cyan-400 hover:underline"
                >
                  {overview.base_url}
                </a>
              </p>
            </div>
          </SectionCard>

          <SectionCard title={t('zfinance.sections')}>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
              {overview.sections.map((section: ZFinanceSection) => (
                <a
                  key={section.id}
                  href={section.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block rounded-card border border-border bg-panel px-3 py-2 text-sm text-text-secondary hover:border-cyan-500/50 hover:text-cyan-400 transition"
                >
                  {section.id.charAt(0).toUpperCase() + section.id.slice(1)}
                </a>
              ))}
            </div>
          </SectionCard>

          <SectionCard title={t('zfinance.watchlist')}>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="border-b border-border text-text-dim">
                    <th className="pb-2 pr-4 font-semibold">{t('zfinance.symbol')}</th>
                    <th className="pb-2 pr-4 font-semibold">{t('zfinance.name')}</th>
                    <th className="pb-2 pr-4 font-semibold">{t('zfinance.class')}</th>
                    <th className="pb-2 pr-4 font-semibold">{t('zfinance.region')}</th>
                    <th className="pb-2 font-semibold">{t('zfinance.link')}</th>
                  </tr>
                </thead>
                <tbody>
                  {overview.watchlist.map((item: ZFinanceInstrument) => (
                    <tr key={item.symbol} className="border-b border-border text-text-secondary">
                      <td className="py-2 pr-4 font-medium text-text-primary">{item.symbol}</td>
                      <td className="py-2 pr-4">{item.name}</td>
                      <td className="py-2 pr-4">{item.asset_class}</td>
                      <td className="py-2 pr-4">{item.region}</td>
                      <td className="py-2">
                        <a
                          href={item.google_finance_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-cyan-400 hover:underline"
                        >
                          {t('zfinance.open')}
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </SectionCard>

          <SectionCard title={t('zfinance.search')}>
            <form onSubmit={handleSearch} className="flex gap-2 mb-3">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={t('zfinance.search_placeholder')}
                className="flex-1 rounded-card border border-border bg-panel-solid px-3 py-2 text-sm text-text-primary placeholder-text-dim focus:outline-none focus:border-cyan-500/50"
              />
              <button
                type="submit"
                disabled={searching || !searchQuery.trim()}
                className="rounded-card bg-cyan-600 px-4 py-2 text-sm font-semibold text-text-primary hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {searching ? t('zfinance.searching') : t('zfinance.search')}
              </button>
            </form>
            {searchResult && (
              <a
                href={searchResult.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-cyan-400 hover:underline"
              >
                {t('zfinance.open_search_results')} &ldquo;{searchResult.query}&rdquo;
                <span className="text-xs">↗</span>
              </a>
            )}
          </SectionCard>

          {overview.warnings.length > 0 && (
            <SectionCard title={t('zfinance.warnings')} className="border-amber-500/20">
              <ul className="space-y-1">
                {overview.warnings.map((w: string, i: number) => (
                  <li key={i} className="text-sm text-amber-300 flex items-start gap-2">
                    <span className="mt-0.5 text-amber-400">⚠</span>
                    {w}
                  </li>
                ))}
              </ul>
            </SectionCard>
          )}
        </>
      ) : null}
    </div>
  );
}
