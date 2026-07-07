'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/storefront/lib/store/authStore'
import { getOrders } from '@/storefront/lib/api/account'
import { formatPrice } from '@/storefront/lib/utils/currency'
import { Package, ChevronRight } from 'lucide-react'
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

export default function OrdersPage() {
  const router = useRouter()
  const { token } = useAuthStore()

  useEffect(() => {
    if (!token) router.replace('/account/login')
  }, [token, router])

  const { data: orders = [], isLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: getOrders,
    enabled: !!token,
  })

  if (!token) return null

  return (
    <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6">
      <h1 className="mb-8 text-2xl font-bold text-gray-900">I miei ordini</h1>

      {isLoading && (
        <div className="space-y-3">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-20 animate-pulse rounded-2xl bg-gray-100" />
          ))}
        </div>
      )}

      {!isLoading && orders.length === 0 && (
        <div className="rounded-2xl border border-dashed border-gray-200 py-16 text-center">
          <Package className="mx-auto mb-3 h-10 w-10 text-gray-300" />
          <p className="text-sm text-gray-500">Non hai ancora effettuato ordini.</p>
          <Link
            href="/shop"
            className="mt-4 inline-block text-sm font-medium text-[var(--color-primary,#111)] hover:underline"
          >
            Inizia a fare shopping
          </Link>
        </div>
      )}

      <ul className="space-y-3">
        {orders.map((order) => {
          const { label, cls } = STATUS_MAP[order.status] ?? {
            label: order.status,
            cls: 'bg-gray-100 text-gray-600',
          }
          const date = new Date(order.created_at).toLocaleDateString('it-IT', {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
          })

          return (
            <li key={order.id}>
              <Link
                href={`/account/orders/${order.id}`}
                className="flex items-center gap-4 rounded-2xl border border-gray-200 bg-white p-4 transition hover:border-gray-400 hover:shadow-sm"
              >
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gray-100 text-gray-500">
                  <Package className="h-5 w-5" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-gray-900">
                      Ordine #{order.id}
                    </span>
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}>
                      {label}
                    </span>
                  </div>
                  <p className="mt-0.5 text-xs text-gray-400">{date}</p>
                  <p className="mt-0.5 text-xs text-gray-500">
                    {order.items?.length ?? 0}{' '}
                    {(order.items?.length ?? 0) === 1 ? 'articolo' : 'articoli'}
                  </p>
                </div>

                <div className="text-right shrink-0">
                  <p className="text-sm font-bold text-gray-900">{formatPrice(order.total)}</p>
                  <ChevronRight className="ml-auto mt-1 h-4 w-4 text-gray-300" />
                </div>
              </Link>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
