'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import {
  addCartItem,
  applyDiscount as apiApplyDiscount,
  createOrFetchCart,
  generateSessionId,
  removeCartItem,
  updateCartItem,
} from '@/storefront/lib/api/cart'
import type { CartItem, CartMeta } from '@/storefront/lib/types/cart'

interface CartStore {
  sessionId: string | null
  items: CartItem[]
  meta: CartMeta
  isOpen: boolean
  isLoading: boolean

  initCart: (customerId?: number) => Promise<void>
  addItem: (
    productId: number,
    quantity: number,
    variantId?: number,
  ) => Promise<void>
  updateItem: (itemId: number, quantity: number) => Promise<void>
  removeItem: (itemId: number) => Promise<void>
  applyDiscount: (
    code: string,
  ) => Promise<{ success: boolean; message: string }>
  openDrawer: () => void
  closeDrawer: () => void
  clearCart: () => void
}

const emptyMeta: CartMeta = {
  subtotal: 0,
  discount: 0,
  shipping: 0,
  tax: 0,
  total: 0,
}

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      sessionId: null,
      items: [],
      meta: emptyMeta,
      isOpen: false,
      isLoading: false,

      async initCart(customerId) {
        let { sessionId } = get()
        if (!sessionId) {
          sessionId = generateSessionId()
          set({ sessionId })
        }

        set({ isLoading: true })
        try {
          const res = await createOrFetchCart(sessionId, customerId)
          set({ items: res.data.cartItems ?? [], meta: res.meta })
        } catch {
          // Ignore network errors during init — cart stays empty
        } finally {
          set({ isLoading: false })
        }
      },

      async addItem(productId, quantity, variantId) {
        const { sessionId } = get()
        if (!sessionId) return

        set({ isLoading: true })
        try {
          const res = await addCartItem(sessionId, productId, quantity, variantId)
          // Refresh the full cart
          await get().initCart()
          set({ isOpen: true })
        } catch {
          throw new Error('Impossibile aggiungere il prodotto al carrello.')
        } finally {
          set({ isLoading: false })
        }
      },

      async updateItem(itemId, quantity) {
        const { sessionId } = get()
        if (!sessionId) return

        set({ isLoading: true })
        try {
          const res = await updateCartItem(sessionId, itemId, quantity)
          set((state) => ({
            items: state.items.map((i) =>
              i.id === itemId ? { ...i, quantity, line_total: res.data.line_total } : i,
            ),
            meta: res.meta,
          }))
        } finally {
          set({ isLoading: false })
        }
      },

      async removeItem(itemId) {
        const { sessionId } = get()
        if (!sessionId) return

        set({ isLoading: true })
        try {
          const res = await removeCartItem(sessionId, itemId)
          set((state) => ({
            items: state.items.filter((i) => i.id !== itemId),
            meta: res.meta,
          }))
        } finally {
          set({ isLoading: false })
        }
      },

      async applyDiscount(code) {
        const { sessionId } = get()
        if (!sessionId) return { success: false, message: 'Carrello non trovato.' }

        const res = await apiApplyDiscount(sessionId, code)
        return { success: res.meta.success, message: res.meta.message }
      },

      openDrawer: () => set({ isOpen: true }),
      closeDrawer: () => set({ isOpen: false }),
      clearCart: () => set({ items: [], meta: emptyMeta, sessionId: null }),
    }),
    {
      name: 'cart-store',
      partialize: (state) => ({ sessionId: state.sessionId }),
    },
  ),
)
