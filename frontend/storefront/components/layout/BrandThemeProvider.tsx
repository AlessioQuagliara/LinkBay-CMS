'use client'

import { useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { useBrandStore } from '@/storefront/lib/store/brandStore'
import { useCartStore } from '@/storefront/lib/store/cartStore'
import { useAuthStore } from '@/storefront/lib/store/authStore'
import CartDrawer from './CartDrawer'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
})

function StoreInitializer() {
  const fetchBrand = useBrandStore((s) => s.fetchBrand)
  const initCart = useCartStore((s) => s.initCart)
  const clearAuth = useAuthStore((s) => s.clearAuth)

  useEffect(() => {
    void fetchBrand()
    void initCart()
  }, [fetchBrand, initCart])

  // The apiClient response interceptor dispatches this on any 401 (expired
  // or revoked token) — keep the in-memory auth store in sync so protected
  // pages redirect immediately instead of only after a reload.
  useEffect(() => {
    window.addEventListener('auth:logout', clearAuth)
    return () => window.removeEventListener('auth:logout', clearAuth)
  }, [clearAuth])

  return null
}

export default function BrandThemeProvider({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <QueryClientProvider client={queryClient}>
      <StoreInitializer />
      {children}
      <CartDrawer />
      <Toaster
        position="bottom-right"
        toastOptions={{
          duration: 3000,
          style: { borderRadius: '8px', fontSize: '14px' },
        }}
      />
    </QueryClientProvider>
  )
}
