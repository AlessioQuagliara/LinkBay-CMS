import { create } from 'zustand'
import type { BrandSettings } from '@/types'

interface BrandState {
  brand: BrandSettings | null
  loading: boolean
  setBrand: (brand: BrandSettings) => void
  setLoading: (loading: boolean) => void
}

export const useBrandStore = create<BrandState>((set) => ({
  brand: null,
  loading: true,
  setBrand: (brand) => set({ brand, loading: false }),
  setLoading: (loading) => set({ loading }),
}))
