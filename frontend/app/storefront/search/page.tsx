'use client'

import { Suspense, useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { searchProducts } from '@/storefront/lib/api/products'
import ProductGrid from '@/storefront/components/products/ProductGrid'
import SortSelect from '@/storefront/components/filters/SortSelect'
import Pagination from '@/storefront/components/filters/Pagination'

function SearchContent() {
  const params = useSearchParams()
  const query = params.get('q') ?? ''
  const [debouncedQuery, setDebouncedQuery] = useState(query)

  useEffect(() => {
    const id = setTimeout(() => setDebouncedQuery(query), 300)
    return () => clearTimeout(id)
  }, [query])

  const queryParams = {
    page: Number(params.get('page') ?? 1),
    sort_by: (params.get('sort_by') as 'price' | 'name' | 'created_at') ?? 'created_at',
    sort_dir: (params.get('sort_dir') as 'asc' | 'desc') ?? 'desc',
  }

  const { data, isFetching } = useQuery({
    queryKey: ['search', debouncedQuery, queryParams],
    queryFn: () => searchProducts(debouncedQuery, queryParams),
    enabled: debouncedQuery.trim().length > 0,
    staleTime: 30_000,
  })

  const products = data?.data ?? []

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="mb-2 text-2xl font-bold text-gray-900">
        {query ? `Risultati per "${query}"` : 'Cerca prodotti'}
      </h1>

      {data && (
        <p className="mb-6 text-sm text-gray-500">
          {data.meta.total === 0
            ? `Nessun risultato per "${query}"`
            : `${data.meta.total} ${data.meta.total === 1 ? 'risultato' : 'risultati'}`}
        </p>
      )}

      {data?.meta.total === 0 && (
        <div className="rounded-xl border border-gray-200 bg-gray-50 px-6 py-12 text-center">
          <p className="text-gray-600">
            Nessun prodotto trovato per <strong>&ldquo;{query}&rdquo;</strong>.
          </p>
          <p className="mt-2 text-sm text-gray-400">
            Prova con parole chiave diverse o{' '}
            <a href="/shop" className="text-[var(--color-primary,#111)] underline">
              sfoglia tutti i prodotti
            </a>
            .
          </p>
        </div>
      )}

      {products.length > 0 && (
        <>
          <div className="mb-4 flex justify-end">
            <Suspense>
              <SortSelect />
            </Suspense>
          </div>
          <ProductGrid products={products} isLoading={isFetching} />
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
        </>
      )}

      {!query && (
        <p className="text-center text-gray-400 py-16">
          Inserisci un termine di ricerca per trovare prodotti.
        </p>
      )}
    </div>
  )
}

export default function SearchPage() {
  return (
    <Suspense>
      <SearchContent />
    </Suspense>
  )
}
