import Link from 'next/link'
import Image from 'next/image'
import { ChevronLeft, MapPin, Truck } from 'lucide-react'
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
    hour: '2-digit',
    minute: '2-digit',
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

export function OrderDetail({ order }: Props) {
  const statusLabel = STATUS_LABELS[order.status] ?? order.status
  const statusColor = STATUS_COLORS[order.status] ?? 'bg-gray-100 text-gray-600'

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <Link
          href="/account/orders"
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-900 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          Ordini
        </Link>
        <span className="text-gray-300">/</span>
        <span className="text-sm font-medium text-gray-900">#{order.reference}</span>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div>
          <p className="text-xs text-gray-500">Effettuato il {formatDate(order.created_at)}</p>
          {order.tracking_number && (
            <p className="text-xs text-gray-500 mt-0.5">
              Tracking: <span className="font-mono">{order.tracking_number}</span>
            </p>
          )}
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColor}`}>
          {statusLabel}
        </span>
      </div>

      {/* Items */}
      <div className="rounded-xl border border-gray-200 overflow-hidden mb-6">
        <div className="px-5 py-3 bg-gray-50 border-b border-gray-200">
          <h2 className="text-sm font-semibold text-gray-900">Articoli</h2>
        </div>
        <ul className="divide-y divide-gray-100">
          {order.items.map((item) => (
            <li key={item.id} className="flex items-center gap-4 px-5 py-4">
              <div className="w-12 h-12 rounded-lg bg-gray-100 flex-shrink-0 relative overflow-hidden">
                {item.image_url && (
                  <Image src={item.image_url} alt={item.product_name} fill className="object-cover" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">{item.product_name}</p>
                {item.variant_label && (
                  <p className="text-xs text-gray-500">{item.variant_label}</p>
                )}
                <p className="text-xs text-gray-400">SKU: {item.sku}</p>
              </div>
              <div className="text-right flex-shrink-0">
                <p className="text-sm font-medium text-gray-900">
                  {formatCurrency(item.total_price, order.currency)}
                </p>
                <p className="text-xs text-gray-500">
                  {formatCurrency(item.unit_price, order.currency)} × {item.quantity}
                </p>
              </div>
            </li>
          ))}
        </ul>

        {/* Totals */}
        <div className="px-5 py-4 bg-gray-50 border-t border-gray-200 space-y-2 text-sm">
          <div className="flex justify-between text-gray-600">
            <span>Subtotale</span>
            <span>{formatCurrency(order.subtotal, order.currency)}</span>
          </div>
          {order.discount_total > 0 && (
            <div className="flex justify-between text-green-600">
              <span>Sconto</span>
              <span>-{formatCurrency(order.discount_total, order.currency)}</span>
            </div>
          )}
          <div className="flex justify-between text-gray-600">
            <span>Spedizione</span>
            <span>
              {order.shipping_total === 0
                ? 'Gratuita'
                : formatCurrency(order.shipping_total, order.currency)}
            </span>
          </div>
          <div className="flex justify-between font-semibold text-gray-900 pt-2 border-t border-gray-200 text-base">
            <span>Totale</span>
            <span>{formatCurrency(order.total, order.currency)}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {order.shipping_address && (
          <div className="rounded-xl border border-gray-200 p-5">
            <div className="flex items-center gap-2 mb-3">
              <MapPin className="w-4 h-4 text-gray-500" />
              <h2 className="text-sm font-semibold text-gray-900">Indirizzo di spedizione</h2>
            </div>
            <address className="not-italic text-sm text-gray-600 leading-relaxed">
              {order.shipping_address.first_name} {order.shipping_address.last_name}<br />
              {order.shipping_address.address_line1}<br />
              {order.shipping_address.address_line2 && <>{order.shipping_address.address_line2}<br /></>}
              {order.shipping_address.postal_code} {order.shipping_address.city}<br />
              {order.shipping_address.country}
            </address>
          </div>
        )}

        {order.shipping_method && (
          <div className="rounded-xl border border-gray-200 p-5">
            <div className="flex items-center gap-2 mb-3">
              <Truck className="w-4 h-4 text-gray-500" />
              <h2 className="text-sm font-semibold text-gray-900">Spedizione</h2>
            </div>
            <p className="text-sm text-gray-600">{order.shipping_method}</p>
          </div>
        )}
      </div>
    </div>
  )
}
