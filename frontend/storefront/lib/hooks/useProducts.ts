'use client'

import { useInfiniteQuery } from '@tanstack/react-query'
import { getProducts } from '@/storefront/lib/api/products'
import type { ProductListParams } from '@/storefront/lib/types/product'

export function useProducts(params: ProductListParams = {}) {
  return useInfiniteQuery({
    queryKey: ['products', params],
    queryFn: ({ pageParam = 1 }) =>
      getProducts({ ...params, page: pageParam as number }),
    initialPageParam: 1,
    getNextPageParam: (last) =>
      last.meta.current_page < last.meta.last_page
        ? last.meta.current_page + 1
        : undefined,
    staleTime: 60_000,
  })
}
