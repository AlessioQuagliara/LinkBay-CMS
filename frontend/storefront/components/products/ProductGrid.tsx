import type { Product } from '@/storefront/lib/types/product'
import ProductCard from './ProductCard'

interface ProductGridProps {
  products: Product[]
  isLoading?: boolean
  currency?: string
}

function SkeletonCard() {
  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
      <div className="aspect-square animate-pulse bg-gray-100" />
      <div className="p-3 space-y-2">
        <div className="h-4 animate-pulse rounded bg-gray-100" />
        <div className="h-4 w-2/3 animate-pulse rounded bg-gray-100" />
        <div className="h-5 w-1/3 animate-pulse rounded bg-gray-100" />
      </div>
    </div>
  )
}

export default function ProductGrid({
  products,
  isLoading,
  currency = 'EUR',
}: ProductGridProps) {
  if (isLoading) {
    return (
      <div
        role="status"
        aria-label="Caricamento prodotti"
        className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4"
      >
        {Array.from({ length: 8 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    )
  }

  if (products.length === 0) {
    return (
      <div className="py-16 text-center text-gray-500">
        <p>Nessun prodotto trovato.</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} currency={currency} />
      ))}
    </div>
  )
}
