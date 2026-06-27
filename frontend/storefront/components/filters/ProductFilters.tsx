'use client'

import { useState } from 'react'
import { useRouter, useSearchParams, usePathname } from 'next/navigation'

export default function ProductFilters() {
  const router = useRouter()
  const pathname = usePathname()
  const params = useSearchParams()

  const [minPrice, setMinPrice] = useState(params.get('min_price') ?? '')
  const [maxPrice, setMaxPrice] = useState(params.get('max_price') ?? '')

  function applyFilters() {
    const next = new URLSearchParams(params.toString())
    if (minPrice) next.set('min_price', minPrice)
    else next.delete('min_price')
    if (maxPrice) next.set('max_price', maxPrice)
    else next.delete('max_price')
    next.delete('page')
    router.push(`${pathname}?${next.toString()}`)
  }

  function clearFilters() {
    setMinPrice('')
    setMaxPrice('')
    const next = new URLSearchParams(params.toString())
    next.delete('min_price')
    next.delete('max_price')
    next.delete('page')
    router.push(`${pathname}?${next.toString()}`)
  }

  return (
    <section aria-label="Filtri prodotti">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-500">
        Filtri
      </h2>

      <div className="space-y-4">
        {/* Price range */}
        <div>
          <p className="mb-2 text-sm font-medium text-gray-700">Fascia di prezzo</p>
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={0}
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
              placeholder="Min €"
              aria-label="Prezzo minimo"
              className="w-full rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary,#111)]"
            />
            <span className="text-gray-400">–</span>
            <input
              type="number"
              min={0}
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              placeholder="Max €"
              aria-label="Prezzo massimo"
              className="w-full rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary,#111)]"
            />
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <button
            onClick={applyFilters}
            className="w-full rounded-lg bg-[var(--color-primary,#111)] py-2 text-sm font-medium text-white hover:opacity-90"
          >
            Applica filtri
          </button>
          {(params.has('min_price') || params.has('max_price')) && (
            <button
              onClick={clearFilters}
              className="w-full rounded-lg border border-gray-200 py-2 text-sm text-gray-600 hover:bg-gray-50"
            >
              Rimuovi filtri
            </button>
          )}
        </div>
      </div>
    </section>
  )
}
