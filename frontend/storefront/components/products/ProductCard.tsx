import Link from 'next/link'
import Image from 'next/image'
import type { Product } from '@/storefront/lib/types/product'
import PriceDisplay from './PriceDisplay'
import StockBadge from './StockBadge'

interface ProductCardProps {
  product: Product
  currency?: string
}

export default function ProductCard({ product, currency = 'EUR' }: ProductCardProps) {
  const primaryImage =
    product.productImages?.find((i) => i.is_primary) ??
    product.productImages?.[0] ??
    (product.images?.[0] as { url: string; alt_text?: string | null } | undefined)

  const isOutOfStock = product.track_quantity && (product.quantity ?? product.stock) <= 0

  return (
    <Link
      href={`/products/${product.slug}`}
      className="group flex flex-col overflow-hidden rounded-xl border border-gray-200 bg-white transition-shadow hover:shadow-md"
    >
      {/* Image */}
      <div className="relative aspect-square overflow-hidden bg-gray-50">
        {primaryImage ? (
          <Image
            src={primaryImage.url}
            alt={primaryImage.alt_text ?? product.name}
            fill
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
            className={`object-cover transition-transform duration-300 group-hover:scale-105 ${isOutOfStock ? 'opacity-60' : ''}`}
          />
        ) : (
          <div className="flex h-full items-center justify-center text-gray-300">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-16 w-16"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}
        {isOutOfStock && (
          <span className="absolute left-2 top-2 rounded-full bg-gray-800/80 px-2 py-0.5 text-xs font-medium text-white">
            Esaurito
          </span>
        )}
      </div>

      {/* Info */}
      <div className="flex flex-1 flex-col p-3">
        <p className="line-clamp-2 text-sm font-medium text-gray-900 leading-snug">
          {product.name}
        </p>
        <div className="mt-auto pt-2">
          <PriceDisplay
            price={product.price}
            compareAtPrice={product.compare_at_price ?? product.compare_price}
            currency={currency}
            size="sm"
          />
        </div>
      </div>
    </Link>
  )
}
