'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { getProfile, login as apiLogin, logout as apiLogout, register as apiRegister } from '@/storefront/lib/api/account'
import type { Customer, LoginPayload, RegisterPayload } from '@/storefront/lib/types/customer'

interface AuthStore {
  token: string | null
  customer: Customer | null
  isLoading: boolean
  /** False until the persisted token has been read back from localStorage —
   * on a full page load/navigation, the store's first render is always the
   * default (unhydrated) state, so guards like "no token -> redirect to
   * login" must wait for this before deciding, or they fire one tick too
   * early and boot an already-logged-in visitor back to the login page. */
  hasHydrated: boolean

  login: (payload: LoginPayload) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  logout: () => Promise<void>
  fetchProfile: () => Promise<void>
  /** Clears local auth state without calling the API — used when the server
   * already rejected the token (401) and there is nothing left to revoke. */
  clearAuth: () => void
  setHasHydrated: (value: boolean) => void
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      token: null,
      customer: null,
      isLoading: false,
      hasHydrated: false,

      async login(payload) {
        set({ isLoading: true })
        try {
          const tokens = await apiLogin(payload)
          set({ token: tokens.token })
          await get().fetchProfile()
        } finally {
          set({ isLoading: false })
        }
      },

      async register(payload) {
        set({ isLoading: true })
        try {
          const tokens = await apiRegister(payload)
          set({ token: tokens.token })
          await get().fetchProfile()
        } finally {
          set({ isLoading: false })
        }
      },

      async logout() {
        try {
          await apiLogout()
        } catch {
          // Fire and forget
        } finally {
          set({ token: null, customer: null })
        }
      },

      async fetchProfile() {
        try {
          const customer = await getProfile()
          set({ customer })
        } catch {
          set({ token: null, customer: null })
        }
      },

      clearAuth() {
        set({ token: null, customer: null })
      },

      setHasHydrated(value) {
        set({ hasHydrated: value })
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({ token: state.token }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true)
      },
    },
  ),
)
