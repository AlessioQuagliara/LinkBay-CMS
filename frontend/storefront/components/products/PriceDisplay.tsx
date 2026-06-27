import { formatPrice, discountPercentage } from '@/storefront/lib/utils/currency'

interface PriceDisplayProps {
  price: number
  compareAtPrice?: number | null
  currency?: string
  size?: 'sm' | 'md' | 'lg'
}

export default function PriceDisplay({
  price,
  compareAtPrice,
  currency = 'EUR',
  size = 'md',
}: PriceDisplayProps) {
  const hasDiscount = compareAtPrice != null && compareAtPrice > price
  const discount = hasDiscount ? discountPercentage(compareAtPrice, price) : 0

  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-xl',
  }

  return (
    <div className="flex flex-wrap items-baseline gap-2">
      <span className={`font-bold text-gray-900 ${sizeClasses[size]}`}>
        {formatPrice(price, currency)}
      </span>
      {hasDiscount && (
        <>
          <span className={`text-gray-400 line-through ${sizeClasses[size]}`}>
            {formatPrice(compareAtPrice, currency)}
          </span>
          <span className="rounded-full bg-red-100 px-1.5 py-0.5 text-xs font-semibold text-red-600">
            -{discount}%
          </span>
        </>
      )}
    </div>
  )
}
