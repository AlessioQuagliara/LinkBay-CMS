'use client'

import { Suspense, use } from 'react'
import { useSearchParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { getCategoryProducts, getCategories } from '@/storefront/lib/api/products'
import ProductGrid from '@/storefront/components/products/ProductGrid'
import CategoryNav from '@/storefront/components/filters/CategoryNav'
import ProductFilters from '@/storefront/components/filters/ProductFilters'
import SortSelect from '@/storefront/components/filters/SortSelect'
import Pagination from '@/storefront/components/filters/Pagination'

function CategoryContent({ categorySlug }: { categorySlug: string }) {
  const params = useSearchParams()
  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: getCategories,
    staleTime: 5 * 60_000,
  })

  const queryParams = {
    page: Number(params.get('page') ?? 1),
    sort_by: (params.get('sort_by') as 'price' | 'name' | 'created_at') ?? 'created_at',
    sort_dir: (params.get('sort_dir') as 'asc' | 'desc') ?? 'desc',
    min_price: params.get('min_price') ? Number(params.get('min_price')) : undefined,
    max_price: params.get('max_price') ? Number(params.get('max_price')) : undefined,
  }

  const { data, isFetching } = useQuery({
    queryKey: ['category-products', categorySlug, queryParams],
    queryFn: () => getCategoryProducts(categorySlug, queryParams),
    staleTime: 60_000,
  })

  const products = data?.data ?? []
  const activeCategory = categories
    .flatMap((c) => [c, ...c.children])
    .find((c) => c.slug === categorySlug)

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">
        {activeCategory?.name ?? categorySlug}
      </h1>

      <div className="flex gap-8">
        <aside className="hidden w-56 shrink-0 space-y-8 lg:block">
          <CategoryNav categories={categories} activeSlug={categorySlug} />
          <ProductFilters />
        </aside>

        <div className="flex-1 min-w-0">
          <div className="mb-4 flex items-center justify-between gap-4">
            {data && (
              <p className="text-sm text-gray-500">
                {data.meta.total} {data.meta.total === 1 ? 'prodotto' : 'prodotti'}
              </p>
            )}
            <Suspense>
              <SortSelect />
            </Suspense>
          </div>

          <ProductGrid products={products} isLoading={isFetching && products.length === 0} />

          {data && data.meta.last_page > 1 && (
            <div className="mt-8">
              <Suspense>
                <Pagination
                  currentPage={data.meta.current_page}
                  lastPage={data.meta.last_page}
                  total={data.meta.total}
                />
              </Suspense>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function CategoryPage({
  params,
}: {
  params: Promise<{ category: string }>
}) {
  const { category } = use(params)
  return (
    <Suspense>
      <CategoryContent categorySlug={category} />
    </Suspense>
  )
}
