'use client'

import { useQuery } from '@tanstack/react-query'
import { getCategories } from '@/storefront/lib/api/products'

export function useCategories() {
  return useQuery({
    queryKey: ['categories'],
    queryFn: getCategories,
    staleTime: 5 * 60_000,
  })
}
