import { useMemo, useState } from "react";

import { getLogs } from "../api/endpoints";
import type { EventLog } from "../api/types";
import { useApi } from "./useApi";

export const useLogs = () => {
  const state = useApi<EventLog[]>(getLogs, []);
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [sourceFilter, setSourceFilter] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState<string>("");

  const filteredLogs = useMemo(() => {
    if (!state.data) {
      return [];
    }

    return state.data.filter((entry) => {
      const matchesType =
        typeFilter === "all" ||
        String(entry.type || entry.category || "unknown") === typeFilter;
      const matchesSource =
        sourceFilter === "all" || String(entry.source) === sourceFilter;
      const matchesSearch =
        searchTerm.trim().length === 0 ||
        `${entry.message} ${entry.source} ${entry.type || ""} ${entry.category || ""}`
          .toLowerCase()
          .includes(searchTerm.trim().toLowerCase());
      return matchesType && matchesSource && matchesSearch;
    });
  }, [state.data, typeFilter, sourceFilter, searchTerm]);

  return {
    ...state,
    logs: filteredLogs,
    filters: {
      typeFilter,
      sourceFilter,
      searchTerm,
    },
    setTypeFilter,
    setSourceFilter,
    setSearchTerm,
  };
};
