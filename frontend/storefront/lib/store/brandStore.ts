'use client'

import { create } from 'zustand'
import { apiClient } from '@/storefront/lib/api/client'
import { applyBrandCssVars } from '@/storefront/lib/utils/brand-css'
import type { Brand } from '@/storefront/lib/types/brand'

interface BrandStore {
  brand: Brand | null
  isLoading: boolean
  fetchBrand: () => Promise<void>
}

export const useBrandStore = create<BrandStore>()((set) => ({
  brand: null,
  isLoading: false,

  async fetchBrand() {
    set({ isLoading: true })
    try {
      const { data } = await apiClient.get<{ data: Brand }>('/api/store/brand')
      const brand = data.data
      set({ brand })
      applyBrandCssVars(brand)
    } catch {
      // Keep defaults if brand API fails
    } finally {
      set({ isLoading: false })
    }
  },
}))
