'use client'

import { CheckCircle } from 'lucide-react'
import Link from 'next/link'
import type { Order } from '@/types'

function formatCurrency(amount: number, currency: string) {
  return new Intl.NumberFormat('it-IT', { style: 'currency', currency: currency.toUpperCase() }).format(amount)
}

interface Props {
  order: Order
}

export function OrderConfirmation({ order }: Props) {
  return (
    <div className="max-w-lg mx-auto text-center py-12 px-4">
      <div className="flex justify-center mb-4">
        <CheckCircle className="w-16 h-16 text-green-500" />
      </div>

      <h1 className="text-2xl font-bold text-gray-900 mb-2">Ordine confermato!</h1>
      <p className="text-gray-600 mb-1">
        Grazie per il tuo acquisto. Riceverai una email di conferma a breve.
      </p>
      <p className="text-sm text-gray-500 mb-8">
        N° ordine: <span className="font-mono font-semibold">{order.reference}</span>
      </p>

      <div className="bg-gray-50 rounded-xl p-6 text-left mb-6">
        <h2 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-4">
          Dettagli ordine
        </h2>
        <ul className="divide-y divide-gray-200">
          {order.items.map((item) => (
            <li key={item.id} className="py-3 flex justify-between text-sm">
              <span className="text-gray-700">
                {item.product_name}
                {item.variant_label && ` — ${item.variant_label}`}
                <span className="text-gray-400 ml-1">×{item.quantity}</span>
              </span>
              <span className="font-medium text-gray-900">
                {formatCurrency(item.total_price, order.currency)}
              </span>
            </li>
          ))}
        </ul>

        <div className="mt-4 pt-4 border-t border-gray-200 space-y-1 text-sm">
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
          <div className="flex justify-between font-semibold text-gray-900 pt-2 text-base">
            <span>Totale</span>
            <span>{formatCurrency(order.total, order.currency)}</span>
          </div>
        </div>
      </div>

      {order.shipping_address && (
        <div className="bg-gray-50 rounded-xl p-6 text-left mb-6">
          <h2 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-2">
            Indirizzo di spedizione
          </h2>
          <address className="not-italic text-sm text-gray-600 leading-relaxed">
            {order.shipping_address.first_name} {order.shipping_address.last_name}<br />
            {order.shipping_address.address_line1}<br />
            {order.shipping_address.address_line2 && <>{order.shipping_address.address_line2}<br /></>}
            {order.shipping_address.postal_code} {order.shipping_address.city}<br />
            {order.shipping_address.country}
          </address>
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <Link
          href="/account/orders"
          className="px-6 py-3 rounded-lg bg-gray-900 text-white text-sm font-semibold hover:bg-gray-700 transition-colors"
        >
          Vedi i miei ordini
        </Link>
        <Link
          href="/"
          className="px-6 py-3 rounded-lg border border-gray-300 text-gray-700 text-sm font-semibold hover:bg-gray-50 transition-colors"
        >
          Continua a fare shopping
        </Link>
      </div>
    </div>
  )
}
