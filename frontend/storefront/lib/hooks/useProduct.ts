'use client'

import { useQuery } from '@tanstack/react-query'
import { getProduct } from '@/storefront/lib/api/products'

export function useProduct(slug: string) {
  return useQuery({
    queryKey: ['product', slug],
    queryFn: () => getProduct(slug),
    staleTime: 60_000,
    enabled: !!slug,
  })
}
