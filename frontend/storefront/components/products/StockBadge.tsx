interface StockBadgeProps {
  quantity: number
  trackQuantity?: boolean
  lowStockThreshold?: number
}

export default function StockBadge({
  quantity,
  trackQuantity = true,
  lowStockThreshold = 5,
}: StockBadgeProps) {
  if (!trackQuantity) {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-medium text-green-600">
        <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
        Disponibile
      </span>
    )
  }

  if (quantity <= 0) {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-medium text-red-500">
        <span className="h-1.5 w-1.5 rounded-full bg-red-500" />
        Esaurito
      </span>
    )
  }

  if (quantity <= lowStockThreshold) {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-medium text-amber-600">
        <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
        Ultimi {quantity} {quantity === 1 ? 'pezzo' : 'pezzi'}
      </span>
    )
  }

  return (
    <span className="inline-flex items-center gap-1.5 text-xs font-medium text-green-600">
      <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
      Disponibile
    </span>
  )
}
