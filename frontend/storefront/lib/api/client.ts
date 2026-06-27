'use client'

import axios, { AxiosError } from 'axios'
import { getClientTenantSlug } from '@/storefront/lib/utils/tenant'

export class ValidationError extends Error {
  constructor(public readonly errors: Record<string, string[]>) {
    super('Errore di validazione')
    this.name = 'ValidationError'
  }
}

export class MaintenanceError extends Error {
  constructor() {
    super('Il servizio è temporaneamente non disponibile')
    this.name = 'MaintenanceError'
  }
}

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? '',
  headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
  timeout: 15_000,
})

// ── Request interceptors ───────────────────────────────────────────────────

apiClient.interceptors.request.use((config) => {
  // Tenant slug from subdomain
  const tenantSlug = getClientTenantSlug()
  if (tenantSlug) {
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
      const data = error.response?.data as { errors?: Record<string, string[]> }
      throw new ValidationError(data?.errors ?? {})
    }

    if (status === 503) {
      throw new MaintenanceError()
    }

    return Promise.reject(error)
  },
)
