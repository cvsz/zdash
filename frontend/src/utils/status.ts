export type StatusSeverity = "success" | "warning" | "danger" | "normal" | "muted";

export function getSeverityFromStatus(status: string): StatusSeverity {
  const value = status.trim().toLowerCase();

  if (
    value.includes("error") ||
    value.includes("failed") ||
    value.includes("halt") ||
    value.includes("kill") ||
    value.includes("danger") ||
    value.includes("blocked")
  ) {
    return "danger";
  }

  if (
    value.includes("warn") ||
    value.includes("pending") ||
    value.includes("degraded")
  ) {
    return "warning";
  }

  if (
    value.includes("ok") ||
    value.includes("healthy") ||
    value.includes("success") ||
    value.includes("online")
  ) {
    return "success";
  }

  if (value.includes("idle") || value.includes("unknown")) {
    return "muted";
  }

  return "normal";
}

export function getBadgeVariant(status: string): StatusSeverity {
  return getSeverityFromStatus(status);
}

export function isDangerStatus(status: string): boolean {
  return getSeverityFromStatus(status) === "danger";
}
