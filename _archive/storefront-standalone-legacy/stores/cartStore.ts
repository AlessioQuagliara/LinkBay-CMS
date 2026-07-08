import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Cart, CartItem } from '@/types'
import { storeApi } from '@/lib/api/client'

interface CartState {
  sessionId: string | null
  cart: Cart | null
  loading: boolean

  initCart: () => Promise<void>
  addItem: (productId: number, variantId?: number, quantity?: number) => Promise<void>
  updateItem: (itemId: number, quantity: number) => Promise<void>
  removeItem: (itemId: number) => Promise<void>
  applyDiscount: (code: string) => Promise<void>
  clearCart: () => void
  itemCount: () => number
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      sessionId: null,
      cart: null,
      loading: false,

      initCart: async () => {
        const { sessionId } = get()
        if (sessionId) {
          try {
            const res = await storeApi.getCart(sessionId)
            set({ cart: res.data })
          } catch {
            const res = await storeApi.createCart()
            set({ sessionId: res.data.session_id, cart: res.data })
          }
        } else {
          const res = await storeApi.createCart()
          set({ sessionId: res.data.session_id, cart: res.data })
        }
      },

      addItem: async (productId, variantId, quantity = 1) => {
        let { sessionId } = get()
        if (!sessionId) {
          const res = await storeApi.createCart()
          sessionId = res.data.session_id
          set({ sessionId, cart: res.data })
        }
        set({ loading: true })
        try {
          const res = await storeApi.addCartItem(sessionId, {
            product_id: productId,
            variant_id: variantId,
            quantity,
          })
          set({ cart: res.data })
        } finally {
          set({ loading: false })
        }
      },

      updateItem: async (itemId, quantity) => {
        const { sessionId } = get()
        if (!sessionId) return
        set({ loading: true })
        try {
          const res = await storeApi.updateCartItem(sessionId, itemId, quantity)
          set({ cart: res.data })
        } finally {
          set({ loading: false })
        }
      },

      removeItem: async (itemId) => {
        const { sessionId } = get()
        if (!sessionId) return
        set({ loading: true })
        try {
          const res = await storeApi.removeCartItem(sessionId, itemId)
          set({ cart: res.data })
        } finally {
          set({ loading: false })
        }
      },

      applyDiscount: async (code) => {
        const { sessionId } = get()
        if (!sessionId) return
        set({ loading: true })
        try {
          const res = await storeApi.applyDiscount(sessionId, code)
          set({ cart: res.data })
        } finally {
          set({ loading: false })
        }
      },

      clearCart: () => set({ sessionId: null, cart: null }),

      itemCount: () => {
        const { cart } = get()
        return cart?.items.reduce((acc: number, item: CartItem) => acc + item.quantity, 0) ?? 0
      },
    }),
    {
      name: 'cart-storage',
      partialize: (state) => ({ sessionId: state.sessionId }),
    },
  ),
)
