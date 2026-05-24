export type ApiEnvelope<T> = {
  ok: boolean
  data: T
  error: { code: string; message: string } | null
  timestamp: string
}

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export function getToken(): string {
  return localStorage.getItem('zdash_token') || ''
}

export function setSession(token: string, role: string, username: string) {
  localStorage.setItem('zdash_token', token)
  localStorage.setItem('zdash_role', role)
  localStorage.setItem('zdash_username', username)
}

export function clearSession() {
  localStorage.removeItem('zdash_token')
  localStorage.removeItem('zdash_role')
  localStorage.removeItem('zdash_username')
}

function authHeaders(): Record<string, string> {
  const token = getToken()
  if (!token) return {}
  return { Authorization: `Bearer ${token}` }
}

export async function apiGet<T>(path: string, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${BASE_URL}${path}`, { headers: { ...authHeaders() } })
    if (res.status === 401) {
      window.dispatchEvent(new Event('auth:unauthorized'))
      return fallback
    }
    if (!res.ok) return fallback
    const payload = (await res.json()) as ApiEnvelope<T>
    return payload.data ?? fallback
  } catch {
    return fallback
  }
}

export async function apiGetEnvelope<T>(path: string): Promise<ApiEnvelope<T> | null> {
  try {
    const res = await fetch(`${BASE_URL}${path}`, { headers: { ...authHeaders() } })
    if (res.status === 401) {
      window.dispatchEvent(new Event('auth:unauthorized'))
      return null
    }
    return (await res.json()) as ApiEnvelope<T>
  } catch {
    return null
  }
}

export async function apiPost<T, B>(path: string, body: B, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(body),
    })
    if (res.status === 401) {
      window.dispatchEvent(new Event('auth:unauthorized'))
      return fallback
    }
    if (!res.ok) return fallback
    const payload = (await res.json()) as ApiEnvelope<T>
    return payload.data ?? fallback
  } catch {
    return fallback
  }
}

export async function apiPostEnvelope<T, B>(path: string, body: B): Promise<ApiEnvelope<T> | null> {
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(body),
    })
    if (res.status === 401) {
      window.dispatchEvent(new Event('auth:unauthorized'))
      return null
    }
    return (await res.json()) as ApiEnvelope<T>
  } catch {
    return null
  }
}
