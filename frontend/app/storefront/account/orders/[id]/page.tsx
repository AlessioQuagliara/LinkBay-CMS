'use client'

import { use, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/storefront/lib/store/authStore'
import { getOrder } from '@/storefront/lib/api/account'
import { formatPrice } from '@/storefront/lib/utils/currency'
import { ArrowLeft, Package } from 'lucide-react'
import type { Order } from '@/storefront/lib/types/order'

const STATUS_MAP: Record<Order['status'], { label: string; cls: string }> = {
  pending: { label: 'In attesa', cls: 'bg-yellow-100 text-yellow-700' },
  confirmed: { label: 'Confermato', cls: 'bg-blue-100 text-blue-700' },
  processing: { label: 'In lavorazione', cls: 'bg-blue-100 text-blue-700' },
  shipped: { label: 'Spedito', cls: 'bg-indigo-100 text-indigo-700' },
  delivered: { label: 'Consegnato', cls: 'bg-green-100 text-green-700' },
  cancelled: { label: 'Annullato', cls: 'bg-red-100 text-red-700' },
  refunded: { label: 'Rimborsato', cls: 'bg-gray-100 text-gray-600' },
}

export default function OrderDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = use(params)
  const router = useRouter()
  const { token } = useAuthStore()

  useEffect(() => {
    if (!token) router.replace('/account/login')
  }, [token, router])

  const { data: order, isLoading } = useQuery({
    queryKey: ['order', id],
    queryFn: () => getOrder(Number(id)),
    enabled: !!token && !!id,
  })

  if (!token) return null

  const { label, cls } = order
    ? (STATUS_MAP[order.status] ?? { label: order.status, cls: 'bg-gray-100 text-gray-600' })
    : { label: '', cls: '' }

  const date = order
    ? new Date(order.created_at).toLocaleDateString('it-IT', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : ''

  return (
    <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6">
      <Link
        href="/account/orders"
        className="mb-6 flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="h-4 w-4" />
        Tutti gli ordini
      </Link>

      {isLoading && (
        <div className="space-y-4">
          <div className="h-8 w-48 animate-pulse rounded-lg bg-gray-100" />
          <div className="h-64 animate-pulse rounded-2xl bg-gray-100" />
        </div>
      )}

      {order && (
        <>
          <div className="mb-6 flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">Ordine #{order.id}</h1>
            <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${cls}`}>
              {label}
            </span>
          </div>

          <p className="mb-6 text-sm text-gray-400">{date}</p>

          {/* Items */}
          <div className="mb-6 rounded-2xl border border-gray-200 bg-white shadow-sm">
            <div className="border-b border-gray-100 p-5">
              <div className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                <Package className="h-4 w-4" />
                Articoli
              </div>
            </div>
            <ul className="divide-y divide-gray-100">
              {order.items.map((item) => (
                <li key={item.id} className="flex items-center gap-4 p-4">
                  <div className="flex-1 min-w-0">
                    <p className="truncate text-sm font-medium text-gray-900">{item.name}</p>
                    {item.sku && <p className="text-xs text-gray-400">SKU: {item.sku}</p>}
                  </div>
                  <div className="text-right shrink-0 text-sm">
                    <p className="text-gray-500">×{item.quantity}</p>
                    <p className="font-semibold text-gray-900">{formatPrice(item.total)}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Totals + address */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-gray-200 bg-gray-50 p-5">
              <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400">
                Riepilogo costi
              </h2>
              <div className="space-y-1.5 text-sm">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotale</span>
                  <span>{formatPrice(order.subtotal)}</span>
                </div>
                {order.discount_total > 0 && (
                  <div className="flex justify-between text-green-600">
                    <span>Sconto</span>
                    <span>-{formatPrice(order.discount_total)}</span>
                  </div>
                )}
                <div className="flex justify-between text-gray-600">
                  <span>Spedizione</span>
                  <span>
                    {order.shipping_total === 0
                      ? 'Gratuita'
                      : formatPrice(order.shipping_total)}
                  </span>
                </div>
                <div className="flex justify-between border-t border-gray-200 pt-2 font-bold text-gray-900">
                  <span>Totale</span>
                  <span>{formatPrice(order.total)}</span>
                </div>
              </div>
            </div>

            {order.shipping_address && (
              <div className="rounded-2xl border border-gray-200 bg-gray-50 p-5">
                <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400">
                  Indirizzo di spedizione
                </h2>
                <address className="not-italic text-sm text-gray-700 leading-relaxed">
                  {order.shipping_address.first_name} {order.shipping_address.last_name}
                  <br />
                  {order.shipping_address.address_line_1}
                  {order.shipping_address.address_line_2 && (
                    <>, {order.shipping_address.address_line_2}</>
                  )}
                  <br />
                  {order.shipping_address.postal_code} {order.shipping_address.city}
                  {order.shipping_address.phone && (
                    <>
                      <br />
                      {order.shipping_address.phone}
                    </>
                  )}
                </address>
              </div>
            )}
          </div>

          {order.tracking_number && (
            <div className="mt-4 rounded-xl border border-indigo-100 bg-indigo-50 px-4 py-3 text-sm text-indigo-700">
              Numero di tracking:{' '}
              <span className="font-mono font-semibold">{order.tracking_number}</span>
            </div>
          )}
        </>
      )}
    </div>
  )
}
