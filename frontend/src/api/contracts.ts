export type ErrorPayload = {
  code: string
  message: string
}

export type ApiEnvelope<T> = {
  ok: boolean
  data: T
  error: ErrorPayload | null
  timestamp: string
}

export function isEnvelope(value: unknown): value is ApiEnvelope<unknown> {
  if (!value || typeof value !== 'object') return false
  const v = value as Record<string, unknown>
  return typeof v.ok === 'boolean' && 'data' in v && 'error' in v && typeof v.timestamp === 'string'
}
