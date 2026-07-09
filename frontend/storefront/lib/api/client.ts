'use client'

import axios, { AxiosError } from 'axios'
import { getClientTenantSlug, tenantApiUrl } from '@/storefront/lib/utils/tenant'

export class ValidationError extends Error {
  constructor(
    public readonly errors: Record<string, string[]>,
    /** Raw `message` from the 422 response body — Laravel's abort(422, '...')
     * controller calls (no per-field `errors`) still carry a real, specific
     * message here even though `errors` is empty. */
    public readonly responseMessage?: string,
  ) {
    super(responseMessage ?? 'Errore di validazione')
    this.name = 'ValidationError'
  }
}

export class MaintenanceError extends Error {
  constructor() {
    super('Il servizio è temporaneamente non disponibile')
    this.name = 'MaintenanceError'
  }
}

/**
 * Turns a caught API error into a message worth showing a user, instead of
 * the generic wrapper text on ValidationError.message ("Errore di
 * validazione") or a one-size-fits-all toast for every failure mode.
 * `fallback` covers anything that isn't one of the two typed errors above
 * (network failure, unexpected 500, etc.) — callers should pass a message
 * specific to what they were trying to do.
 */
export function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof ValidationError) {
    const firstFieldMessage = Object.values(error.errors)[0]?.[0]
    return firstFieldMessage ?? error.responseMessage ?? fallback
  }

  if (error instanceof MaintenanceError) {
    return error.message
  }

  return fallback
}

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? '',
  headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
  timeout: 15_000,
})

// ── Request interceptors ───────────────────────────────────────────────────

apiClient.interceptors.request.use((config) => {
  // Tenant slug from subdomain — the Laravel backend resolves the tenant by
  // Host header (stancl/tenancy domain-based resolution), so requests must
  // target the tenant's own API domain, not a shared/central base URL.
  const tenantSlug = getClientTenantSlug()
  if (tenantSlug) {
    config.baseURL = tenantApiUrl(tenantSlug)
    config.headers['X-Tenant-Slug'] = tenantSlug
  }

  // Customer bearer token from authStore (lazy import to avoid circular deps)
  if (typeof window !== 'undefined') {
    try {
      const raw = localStorage.getItem('auth-store')
      if (raw) {
        const parsed = JSON.parse(raw) as { state?: { token?: string } }
        const token = parsed?.state?.token
        if (token) {
          config.headers['Authorization'] = `Bearer ${token}`
        }
      }
    } catch {
      // localStorage not available or parse error — ignore
    }
  }

  return config
})

// ── Response interceptors ──────────────────────────────────────────────────

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const status = error.response?.status

    if (status === 401) {
      // Clear auth state and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth-store')
        window.dispatchEvent(new CustomEvent('auth:logout'))
      }
    }

    if (status === 422) {
      const data = error.response?.data as { errors?: Record<string, string[]>; message?: string }
      throw new ValidationError(data?.errors ?? {}, data?.message)
    }

    if (status === 503) {
      throw new MaintenanceError()
    }

    return Promise.reject(error)
  },
)
