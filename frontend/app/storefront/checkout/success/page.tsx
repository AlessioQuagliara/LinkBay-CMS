'use client'

import { Suspense, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { getOrder } from '@/storefront/lib/api/account'
import { getOrderByCheckout } from '@/storefront/lib/api/checkout'
import { useCartStore } from '@/storefront/lib/store/cartStore'
import { formatPrice } from '@/storefront/lib/utils/currency'
import { CheckCircle, Package, ArrowRight } from 'lucide-react'
import type { Order } from '@/storefront/lib/types/order'

function StatusBadge({ status }: { status: Order['status'] }) {
  const map: Record<Order['status'], { label: string; cls: string }> = {
    pending: { label: 'In attesa', cls: 'bg-yellow-100 text-yellow-700' },
    confirmed: { label: 'Confermato', cls: 'bg-blue-100 text-blue-700' },
    processing: { label: 'In lavorazione', cls: 'bg-blue-100 text-blue-700' },
    shipped: { label: 'Spedito', cls: 'bg-indigo-100 text-indigo-700' },
    delivered: { label: 'Consegnato', cls: 'bg-green-100 text-green-700' },
    cancelled: { label: 'Annullato', cls: 'bg-red-100 text-red-700' },
    refunded: { label: 'Rimborsato', cls: 'bg-gray-100 text-gray-600' },
  }
  const { label, cls } = map[status] ?? { label: status, cls: 'bg-gray-100 text-gray-600' }
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${cls}`}>{label}</span>
  )
}

function SuccessContent() {
  const params = useSearchParams()
  const orderId = Number(params.get('order'))
  const checkoutId = Number(params.get('checkout'))
  const clearCart = useCartStore((s) => s.clearCart)

  // Clear cart on mount after successful payment
  useEffect(() => {
    clearCart()
  }, [clearCart])

  // Order lookup is scoped by checkout session id (works for guest checkouts —
  // no auth required), falling back to the authenticated account endpoint only
  // if a checkout id somehow isn't in the URL (e.g. an old/bookmarked link).
  const { data: order, isLoading, isError } = useQuery({
    queryKey: ['order', checkoutId || orderId],
    queryFn: () =>
      checkoutId > 0 ? getOrderByCheckout(checkoutId) : getOrder(orderId),
    enabled: checkoutId > 0 || orderId > 0,
    staleTime: Infinity,
    retry: false,
  })

  return (
    <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
      {/* Confirmation header */}
      <div className="mb-8 text-center">
        <div className="mb-4 flex justify-center">
          <CheckCircle className="h-16 w-16 text-green-500" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900">Ordine confermato!</h1>
        <p className="mt-2 text-gray-500">
          Grazie per il tuo acquisto. Riceverai una email di conferma a breve.
        </p>
        {orderId > 0 && (
          <p className="mt-1 text-sm text-gray-400">Ordine #{orderId}</p>
        )}
      </div>

      {/* Order detail card */}
      {isLoading && (
        <div className="space-y-3 rounded-2xl border border-gray-200 p-6">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-4 animate-pulse rounded bg-gray-100" />
          ))}
        </div>
      )}

      {isError && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-center text-sm text-amber-800">
          Il pagamento è andato a buon fine, ma non riusciamo a mostrare il
          dettaglio dell&apos;ordine in questo momento. Controlla la tua email
          per la conferma, oppure contattaci indicando il riferimento sopra.
        </div>
      )}

      {order && (
        <div className="rounded-2xl border border-gray-200 bg-white shadow-sm">
          {/* Items */}
          <div className="divide-y divide-gray-100 p-6">
            <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-gray-700">
              <Package className="h-4 w-4" />
              Prodotti ordinati
            </div>
            <ul className="space-y-3 pt-4">
              {order.items.map((item) => (
                <li key={item.id} className="flex items-center justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <p className="truncate text-sm font-medium text-gray-900">{item.name}</p>
                    {item.sku && (
                      <p className="text-xs text-gray-400">SKU: {item.sku}</p>
                    )}
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-sm text-gray-600">×{item.quantity}</p>
                    <p className="text-sm font-semibold text-gray-900">{formatPrice(item.total)}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Totals */}
          <div className="border-t border-gray-100 bg-gray-50 px-6 py-4">
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
                  {order.shipping_total === 0 ? 'Gratuita' : formatPrice(order.shipping_total)}
                </span>
              </div>
              <div className="flex justify-between border-t border-gray-200 pt-2 font-bold text-gray-900">
                <span>Totale pagato</span>
                <span>{formatPrice(order.total)}</span>
              </div>
            </div>
          </div>

          {/* Status + address */}
          <div className="grid gap-4 border-t border-gray-100 p-6 sm:grid-cols-2">
            <div>
              <p className="mb-1 text-xs font-medium uppercase tracking-wide text-gray-400">
                Stato
              </p>
              <StatusBadge status={order.status} />
            </div>
            {order.shipping_address && (
              <div>
                <p className="mb-1 text-xs font-medium uppercase tracking-wide text-gray-400">
                  Indirizzo di spedizione
                </p>
                <address className="not-italic text-sm text-gray-700 leading-relaxed">
                  {order.shipping_address.first_name} {order.shipping_address.last_name}
                  <br />
                  {order.shipping_address.address_line_1}
                  {order.shipping_address.address_line_2 && (
                    <>, {order.shipping_address.address_line_2}</>
                  )}
                  <br />
                  {order.shipping_address.postal_code} {order.shipping_address.city}
                </address>
              </div>
            )}
          </div>
        </div>
      )}

      {/* CTA */}
      <div className="mt-8 flex flex-col gap-3 sm:flex-row">
        <Link
          href="/account/orders"
          className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-[var(--color-primary,#111)] py-3.5 text-sm font-semibold text-white transition hover:opacity-90"
        >
          I miei ordini
          <ArrowRight className="h-4 w-4" />
        </Link>
        <Link
          href="/shop"
          className="flex-1 rounded-xl border border-gray-300 py-3.5 text-center text-sm font-semibold text-gray-700 transition hover:bg-gray-50"
        >
          Continua a fare shopping
        </Link>
      </div>
    </div>
  )
}

export default function CheckoutSuccessPage() {
  return (
    <Suspense>
      <SuccessContent />
    </Suspense>
  )
}
