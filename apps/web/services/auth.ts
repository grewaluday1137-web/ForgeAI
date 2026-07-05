import { apiClient } from "@/lib/api-client"
import { LoginInput, RegisterInput } from "@/lib/validations/auth"

const API_BASE = "http://localhost:8000/api/v1"

// ─── Public endpoints (no auth needed) ────────────────────────────────────────

export async function loginUser(data: LoginInput) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })

  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.detail || "Failed to login")
  }

  return res.json() as Promise<{ access_token: string; refresh_token: string; token_type: string }>
}

export async function registerUser(data: RegisterInput) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })

  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.detail || "Failed to register")
  }

  return res.json()
}

export async function getMe(token: string) {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })

  if (!res.ok) throw new Error("Failed to fetch user profile")
  return res.json()
}

// ─── Authenticated endpoints (go through apiClient with auto-refresh) ─────────

export async function getMyProfile() {
  return apiClient("/auth/me")
}

export async function logoutUser(refreshToken: string) {
  return apiClient("/auth/logout", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
  })
}
