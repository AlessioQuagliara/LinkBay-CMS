'use client'

import { Suspense, use } from 'react'
import { useSearchParams } from 'next/navigation'
import { useProducts } from '@/storefront/lib/hooks/useProducts'
import ProductGrid from '@/storefront/components/products/ProductGrid'
import SortSelect from '@/storefront/components/filters/SortSelect'
import Pagination from '@/storefront/components/filters/Pagination'

function CollectionContent({ collectionSlug }: { collectionSlug: string }) {
  const params = useSearchParams()

  const queryParams = {
    page: Number(params.get('page') ?? 1),
    sort_by: (params.get('sort_by') as 'price' | 'name' | 'created_at') ?? 'created_at',
    sort_dir: (params.get('sort_dir') as 'asc' | 'desc') ?? 'desc',
  }

  const { data, isFetching } = useProducts(queryParams)
  const firstPage = data?.pages[0]
  const products = data?.pages.flatMap((p) => p.data) ?? []

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="mb-6 text-2xl font-bold capitalize text-gray-900">
        {collectionSlug.replace(/-/g, ' ')}
      </h1>

      <div className="mb-4 flex items-center justify-between gap-4">
        {firstPage && (
          <p className="text-sm text-gray-500">
            {firstPage.meta.total} prodotti
          </p>
        )}
        <Suspense>
          <SortSelect />
        </Suspense>
      </div>

      <ProductGrid products={products} isLoading={isFetching && products.length === 0} />

      {firstPage && firstPage.meta.last_page > 1 && (
        <div className="mt-8">
          <Suspense>
            <Pagination
              currentPage={firstPage.meta.current_page}
              lastPage={firstPage.meta.last_page}
              total={firstPage.meta.total}
            />
          </Suspense>
        </div>
      )}
    </div>
  )
}

export default function CollectionPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = use(params)
  return (
    <Suspense>
      <CollectionContent collectionSlug={slug} />
    </Suspense>
  )
}
