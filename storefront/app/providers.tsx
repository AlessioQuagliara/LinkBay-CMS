'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { useEffect, useRef } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { useBrandStore } from '@/stores/brandStore'
import { storeApi } from '@/lib/api/client'

function AuthHydrator() {
  const hydrateFromCookie = useAuthStore((s) => s.hydrateFromCookie)
  const ran = useRef(false)

  useEffect(() => {
    if (!ran.current) {
      ran.current = true
      hydrateFromCookie()
    }
  }, [hydrateFromCookie])

  return null
}

function BrandLoader() {
  const setBrand = useBrandStore((s) => s.setBrand)
  const setLoading = useBrandStore((s) => s.setLoading)
  const ran = useRef(false)

  useEffect(() => {
    if (!ran.current) {
      ran.current = true
      storeApi.getBrand()
        .then((res) => setBrand(res.data))
        .catch(() => setLoading(false))
    }
  }, [setBrand, setLoading])

  return null
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      retry: 1,
    },
  },
})

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthHydrator />
      <BrandLoader />
      {children}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: { borderRadius: '8px', fontSize: '14px' },
        }}
      />
    </QueryClientProvider>
  )
}
