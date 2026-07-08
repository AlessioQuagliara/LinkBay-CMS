import Link from 'next/link'
import { Package, ChevronRight } from 'lucide-react'
import type { Order } from '@/types'

function formatCurrency(amount: number, currency: string) {
  return new Intl.NumberFormat('it-IT', {
    style: 'currency',
    currency: currency.toUpperCase(),
  }).format(amount)
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('it-IT', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })
}

const STATUS_LABELS: Record<string, string> = {
  pending: 'In attesa',
  processing: 'In lavorazione',
  shipped: 'Spedito',
  delivered: 'Consegnato',
  cancelled: 'Annullato',
  refunded: 'Rimborsato',
}

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  processing: 'bg-blue-100 text-blue-800',
  shipped: 'bg-indigo-100 text-indigo-800',
  delivered: 'bg-green-100 text-green-800',
  cancelled: 'bg-gray-100 text-gray-600',
  refunded: 'bg-red-100 text-red-800',
}

interface Props {
  order: Order
}

export function OrderCard({ order }: Props) {
  const statusLabel = STATUS_LABELS[order.status] ?? order.status
  const statusColor = STATUS_COLORS[order.status] ?? 'bg-gray-100 text-gray-600'

  return (
    <Link
      href={`/account/orders/${order.id}`}
      className="block rounded-xl border border-gray-200 p-5 hover:border-gray-300 hover:shadow-sm transition-all"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-gray-100 rounded-lg flex-shrink-0">
            <Package className="w-4 h-4 text-gray-600" />
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-900">#{order.reference}</p>
            <p className="text-xs text-gray-500 mt-0.5">{formatDate(order.created_at)}</p>
            <p className="text-xs text-gray-500 mt-0.5">
              {order.items.length} {order.items.length === 1 ? 'articolo' : 'articoli'}
            </p>
          </div>
        </div>

        <div className="flex flex-col items-end gap-2 flex-shrink-0">
          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColor}`}>
            {statusLabel}
          </span>
          <p className="text-sm font-semibold text-gray-900">
            {formatCurrency(order.total, order.currency)}
          </p>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between">
        <div className="flex -space-x-1">
          {order.items.slice(0, 3).map((item) => (
            <div
              key={item.id}
              className="w-7 h-7 rounded-full bg-gray-200 border-2 border-white flex items-center justify-center text-xs text-gray-500"
              title={item.product_name}
            >
              {item.product_name[0]}
            </div>
          ))}
          {order.items.length > 3 && (
            <div className="w-7 h-7 rounded-full bg-gray-100 border-2 border-white flex items-center justify-center text-xs text-gray-500">
              +{order.items.length - 3}
            </div>
          )}
        </div>
        <ChevronRight className="w-4 h-4 text-gray-400" />
      </div>
    </Link>
  )
}
