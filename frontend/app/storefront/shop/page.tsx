'use client'

import { Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { useProducts } from '@/storefront/lib/hooks/useProducts'
import { useCategories } from '@/storefront/lib/hooks/useCategories'
import ProductGrid from '@/storefront/components/products/ProductGrid'
import CategoryNav from '@/storefront/components/filters/CategoryNav'
import ProductFilters from '@/storefront/components/filters/ProductFilters'
import SortSelect from '@/storefront/components/filters/SortSelect'
import Pagination from '@/storefront/components/filters/Pagination'

function ShopContent() {
  const params = useSearchParams()
  const { data: categories = [] } = useCategories()

  const queryParams = {
    page: Number(params.get('page') ?? 1),
    search: params.get('search') ?? undefined,
    category: params.get('category') ?? undefined,
    min_price: params.get('min_price') ? Number(params.get('min_price')) : undefined,
    max_price: params.get('max_price') ? Number(params.get('max_price')) : undefined,
    sort_by: (params.get('sort_by') as 'price' | 'name' | 'created_at') ?? 'created_at',
    sort_dir: (params.get('sort_dir') as 'asc' | 'desc') ?? 'desc',
  }

  const { data, isFetching } = useProducts(queryParams)
  const firstPage = data?.pages[0]
  const products = data?.pages.flatMap((p) => p.data) ?? []

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Tutti i prodotti</h1>

      <div className="flex gap-8">
        {/* Sidebar */}
        <aside className="hidden w-56 shrink-0 space-y-8 lg:block">
          <CategoryNav categories={categories} />
          <ProductFilters />
        </aside>

        {/* Main content */}
        <div className="flex-1 min-w-0">
          {/* Toolbar */}
          <div className="mb-4 flex items-center justify-between gap-4">
            {firstPage && (
              <p className="text-sm text-gray-500">
                {firstPage.meta.total}{' '}
                {firstPage.meta.total === 1 ? 'prodotto' : 'prodotti'}
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
      </div>
    </div>
  )
}

export default function ShopPage() {
  return (
    <Suspense>
      <ShopContent />
    </Suspense>
  )
}
