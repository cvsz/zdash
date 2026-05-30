import { apiClient } from "./client";

export type ZFinanceSection = {
  id: string;
  url: string;
};

export type ZFinanceInstrument = {
  symbol: string;
  name: string;
  asset_class: string;
  region: string;
  google_finance_url: string;
};

export type ZFinanceOverview = {
  provider: string;
  mode: string;
  scraping_enabled: boolean;
  base_url: string;
  sections: ZFinanceSection[];
  watchlist: ZFinanceInstrument[];
  warnings: string[];
  timestamp: string;
};

const fallbackOverview: ZFinanceOverview = {
  provider: "google_finance_beta",
  mode: "read_only_link_adapter",
  scraping_enabled: false,
  base_url: "https://www.google.com/finance/beta",
  sections: [
    { id: "home", url: "https://www.google.com/finance/beta" },
    { id: "us", url: "https://www.google.com/finance/beta/us" },
    { id: "europe", url: "https://www.google.com/finance/beta/europe" },
    { id: "asia", url: "https://www.google.com/finance/beta/asia" },
    { id: "currencies", url: "https://www.google.com/finance/beta/currencies" },
    { id: "crypto", url: "https://www.google.com/finance/beta/crypto" },
    { id: "futures", url: "https://www.google.com/finance/beta/futures" },
  ],
  watchlist: [
    { symbol: ".DJI", name: "Dow Jones", asset_class: "index", region: "US", google_finance_url: "https://www.google.com/finance/beta/search?q=Dow%20Jones" },
    { symbol: ".INX", name: "S&P 500", asset_class: "index", region: "US", google_finance_url: "https://www.google.com/finance/beta/search?q=S%26P%20500" },
    { symbol: ".IXIC", name: "Nasdaq", asset_class: "index", region: "US", google_finance_url: "https://www.google.com/finance/beta/search?q=Nasdaq" },
    { symbol: "XAUUSD", name: "Gold / US Dollar", asset_class: "commodity", region: "Futures", google_finance_url: "https://www.google.com/finance/beta/search?q=Gold" },
  ],
  warnings: ["Read-only external links only", "No scraping or private endpoint use", "Not financial advice"],
  timestamp: new Date().toISOString(),
};

export const getZFinanceOverview = () =>
  apiClient.get<ZFinanceOverview>("/api/integrations/google-finance/overview", fallbackOverview);

export const getZFinanceSearch = (query: string) =>
  apiClient.get<{ query: string; url: string }>(
    `/api/integrations/google-finance/search?q=${encodeURIComponent(query)}`,
    { query, url: `https://www.google.com/finance/beta/search?q=${encodeURIComponent(query)}` },
  );
