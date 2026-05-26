import { useEffect, useMemo, useState } from 'react';

export const AGENTS_PAGE_SIZE_OPTIONS = [6, 9, 12, 24] as const;
export type AgentsPageSize = (typeof AGENTS_PAGE_SIZE_OPTIONS)[number];

const DEFAULT_PAGE_SIZE: AgentsPageSize = 9;
const STORAGE_KEY = 'zdash-agents-per-page';

export function getInitialAgentsPageSize(): AgentsPageSize {
  if (typeof window === 'undefined') return DEFAULT_PAGE_SIZE;

  const saved = Number(window.localStorage.getItem(STORAGE_KEY));
  return AGENTS_PAGE_SIZE_OPTIONS.includes(saved as AgentsPageSize)
    ? (saved as AgentsPageSize)
    : DEFAULT_PAGE_SIZE;
}

export function useAgentsPagination<T>(items: T[]) {
  const [agentsPerPage, setAgentsPerPageState] = useState<AgentsPageSize>(
    getInitialAgentsPageSize,
  );
  const [currentPage, setCurrentPage] = useState(1);

  const totalItems = items.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / agentsPerPage));

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(STORAGE_KEY, String(agentsPerPage));
    }

    setCurrentPage((page) => Math.min(page, totalPages));
  }, [agentsPerPage, totalPages]);

  const pageItems = useMemo(() => {
    const start = (currentPage - 1) * agentsPerPage;
    return items.slice(start, start + agentsPerPage);
  }, [agentsPerPage, currentPage, items]);

  const pageStart = totalItems === 0 ? 0 : (currentPage - 1) * agentsPerPage + 1;
  const pageEnd = Math.min(currentPage * agentsPerPage, totalItems);

  function setAgentsPerPage(value: number) {
    const next = AGENTS_PAGE_SIZE_OPTIONS.includes(value as AgentsPageSize)
      ? (value as AgentsPageSize)
      : DEFAULT_PAGE_SIZE;

    setAgentsPerPageState(next);
    setCurrentPage(1);
  }

  function goToPage(page: number) {
    setCurrentPage(Math.min(Math.max(page, 1), totalPages));
  }

  return {
    agentsPerPage,
    currentPage,
    totalItems,
    totalPages,
    pageItems,
    pageStart,
    pageEnd,
    setAgentsPerPage,
    goToPage,
  };
}
