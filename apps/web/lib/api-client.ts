/**
 * Centralized API client with automatic JWT refresh.
 *
 * Flow:
 *   1. Every request gets the access token injected via Authorization header.
 *   2. On a 401 Unauthorized response, the client automatically calls /auth/refresh
 *      with the stored refresh token and retries the original request once.
 *   3. If the refresh itself fails (expired/revoked), the user is logged out and
 *      redirected to /login.
 */

import { useAuth } from '@/hooks/use-auth'

const API_BASE = 'http://localhost:8000/api/v1'

let isRefreshing = false
let refreshPromise: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  const { refreshToken, setAccessToken, logout } = useAuth.getState()

  if (!refreshToken) {
    logout()
    return null
  }

  // Serialize concurrent refresh calls into one
  if (isRefreshing && refreshPromise) {
    return refreshPromise
  }

  isRefreshing = true
  refreshPromise = (async () => {
    try {
      const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      if (!res.ok) {
        logout()
        if (typeof window !== 'undefined') window.location.href = '/login'
        return null
      }

      const data = await res.json()
      // Store the new rotated access token
      setAccessToken(data.access_token)
      return data.access_token as string
    } catch {
      logout()
      if (typeof window !== 'undefined') window.location.href = '/login'
      return null
    } finally {
      isRefreshing = false
      refreshPromise = null
    }
  })()

  return refreshPromise
}

export async function apiClient<T = unknown>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const { accessToken } = useAuth.getState()

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }

  if (accessToken) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${accessToken}`
  }

  let response = await fetch(`${API_BASE}${path}`, { ...options, headers })

  // Token expired — try a silent refresh and retry once
  if (response.status === 401) {
    const newToken = await refreshAccessToken()

    if (!newToken) {
      throw new Error('Session expired. Please log in again.')
    }

    ;(headers as Record<string, string>)['Authorization'] = `Bearer ${newToken}`
    response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  }

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || `Request failed with status ${response.status}`)
  }

  // Return raw response for 204 No Content
  if (response.status === 204) return undefined as T

  return response.json() as Promise<T>
}
