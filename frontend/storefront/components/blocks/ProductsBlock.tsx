'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { getProducts } from '@/storefront/lib/api/products'
import ProductGrid from '../products/ProductGrid'

interface ProductsSettings {
  title?: string
  subtitle?: string
  collection_id?: number
  category?: string
  limit?: number
  cta_label?: string
  cta_url?: string
}

export default function ProductsBlock({ settings }: { settings: Record<string, unknown> }) {
  const s = settings as ProductsSettings

  const { data, isLoading } = useQuery({
    queryKey: ['block-products', s.collection_id, s.category, s.limit],
    queryFn: () =>
      getProducts({
        per_page: s.limit ?? 4,
        collection_id: s.collection_id,
        category: s.category,
      }),
    staleTime: 5 * 60_000,
  })

  return (
    <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      {(s.title || s.subtitle) && (
        <div className="mb-8 text-center">
          {s.title && (
            <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">{s.title}</h2>
          )}
          {s.subtitle && (
            <p className="mt-2 text-gray-500">{s.subtitle}</p>
          )}
        </div>
      )}

      <ProductGrid products={data?.data ?? []} isLoading={isLoading} />

      {s.cta_label && s.cta_url && (
        <div className="mt-8 text-center">
          <Link
            href={s.cta_url}
            className="inline-block rounded-xl border border-gray-900 px-6 py-3 text-sm font-medium text-gray-900 transition-colors hover:bg-gray-900 hover:text-white"
          >
            {s.cta_label}
          </Link>
        </div>
      )}
    </section>
  )
}
