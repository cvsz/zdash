export function formatDateTime(value: string | Date | null | undefined): string {
  if (!value) {
    return "-";
  }

  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "-";
  }

  return date.toLocaleString();
}

export function formatPercent(value: number, digits = 2): string {
  if (!Number.isFinite(value)) {
    return "-";
  }
  return `${value.toFixed(digits)}%`;
}

export function formatCurrency(
  value: number,
  currency = "USD",
  locale = "en-US",
): string {
  if (!Number.isFinite(value)) {
    return "-";
  }
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatDurationMs(value: number): string {
  if (!Number.isFinite(value) || value < 0) {
    return "-";
  }
  if (value < 1000) {
    return `${Math.round(value)}ms`;
  }
  return `${(value / 1000).toFixed(2)}s`;
}

export function truncateText(value: string, maxLength = 80): string {
  if (value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength - 3)}...`;
}
