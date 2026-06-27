'use client'

import { useCartStore } from '@/storefront/lib/store/cartStore'

export function useCart() {
  return useCartStore()
}
