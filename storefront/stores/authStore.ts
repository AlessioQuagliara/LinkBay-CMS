import { create } from 'zustand'
import Cookies from 'js-cookie'
import type { Customer } from '@/types'
import { accountApi } from '@/lib/api/client'

interface AuthState {
  customer: Customer | null
  token: string | null
  loading: boolean

  login: (email: string, password: string) => Promise<void>
  register: (data: {
    name: string
    email: string
    password: string
    password_confirmation: string
  }) => Promise<void>
  logout: () => Promise<void>
  setAuth: (customer: Customer, token: string) => void
  hydrateFromCookie: () => Promise<void>
  isAuthenticated: () => boolean
}

const COOKIE_NAME = 'customer_token'
const COOKIE_OPTS = { expires: 30, sameSite: 'lax' as const, secure: process.env.NODE_ENV === 'production' }

export const useAuthStore = create<AuthState>((set, get) => ({
  customer: null,
  token: null,
  loading: false,

  setAuth: (customer, token) => {
    Cookies.set(COOKIE_NAME, token, COOKIE_OPTS)
    set({ customer, token })
  },

  login: async (email, password) => {
    set({ loading: true })
    try {
      const res = await accountApi.login({ email, password })
      get().setAuth(res.data, res.token)
    } finally {
      set({ loading: false })
    }
  },

  register: async (data) => {
    set({ loading: true })
    try {
      const res = await accountApi.register(data)
      get().setAuth(res.data, res.token)
    } finally {
      set({ loading: false })
    }
  },

  logout: async () => {
    set({ loading: true })
    try {
      await accountApi.logout()
    } catch {
      // ignore errors on logout
    } finally {
      Cookies.remove(COOKIE_NAME)
      set({ customer: null, token: null, loading: false })
    }
  },

  hydrateFromCookie: async () => {
    const token = Cookies.get(COOKIE_NAME)
    if (!token || get().customer) return
    set({ token, loading: true })
    try {
      const res = await accountApi.getProfile()
      set({ customer: res.data })
    } catch {
      Cookies.remove(COOKIE_NAME)
      set({ token: null })
    } finally {
      set({ loading: false })
    }
  },

  isAuthenticated: () => !!get().token,
}))
