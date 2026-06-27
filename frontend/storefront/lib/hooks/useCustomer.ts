'use client'

import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/storefront/lib/store/authStore'
import { getProfile } from '@/storefront/lib/api/account'

export function useCustomer() {
  const token = useAuthStore((s) => s.token)

  return useQuery({
    queryKey: ['customer', 'profile'],
    queryFn: getProfile,
    enabled: !!token,
    staleTime: 5 * 60_000,
  })
}
