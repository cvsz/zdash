export type ReconnectOptions = {
  baseDelayMs?: number;
  maxDelayMs?: number;
  jitterRatio?: number;
};

export function computeReconnectDelay(
  attempt: number,
  options: ReconnectOptions = {},
): number {
  const baseDelayMs = options.baseDelayMs ?? 750;
  const maxDelayMs = options.maxDelayMs ?? 15000;
  const jitterRatio = options.jitterRatio ?? 0.2;

  const safeAttempt = Math.max(0, attempt);
  const exponential = Math.min(maxDelayMs, baseDelayMs * 2 ** safeAttempt);
  const jitter = Math.round(exponential * jitterRatio * Math.random());
  return Math.min(maxDelayMs, exponential + jitter);
}
