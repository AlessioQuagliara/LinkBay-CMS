'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { getProfile, login as apiLogin, logout as apiLogout, register as apiRegister } from '@/storefront/lib/api/account'
import type { Customer, LoginPayload, RegisterPayload } from '@/storefront/lib/types/customer'

interface AuthStore {
  token: string | null
  customer: Customer | null
  isLoading: boolean

  login: (payload: LoginPayload) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  logout: () => Promise<void>
  fetchProfile: () => Promise<void>
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      token: null,
      customer: null,
      isLoading: false,

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
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({ token: state.token }),
    },
  ),
)
