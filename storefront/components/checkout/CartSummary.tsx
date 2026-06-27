'use client'

import Image from 'next/image'
import type { CheckoutSession } from '@/types'

function formatCurrency(amount: number, currency: string) {
  return new Intl.NumberFormat('it-IT', { style: 'currency', currency: currency.toUpperCase() }).format(amount)
}

interface Props {
  checkout: CheckoutSession
}

export function CartSummary({ checkout }: Props) {
  const { cart, subtotal, shipping_total, discount_total, total, currency } = checkout

  return (
    <div className="bg-gray-50 rounded-xl p-6">
      <h2 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-4">
        Riepilogo ordine
      </h2>

      <ul className="divide-y divide-gray-200 mb-6">
        {cart.items.map((item) => (
          <li key={item.id} className="py-4 flex gap-3">
            <div className="relative w-14 h-14 flex-shrink-0 rounded-lg overflow-hidden bg-gray-200">
              {item.image_url && (
                <Image src={item.image_url} alt={item.product_name} fill className="object-cover" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{item.product_name}</p>
              {item.variant_label && (
                <p className="text-xs text-gray-500">{item.variant_label}</p>
              )}
              <p className="text-xs text-gray-500">Qtà: {item.quantity}</p>
            </div>
            <p className="text-sm font-medium text-gray-900 flex-shrink-0">
              {formatCurrency(item.total_price, currency)}
            </p>
          </li>
        ))}
      </ul>

      <div className="space-y-2 text-sm border-t border-gray-200 pt-4">
        <div className="flex justify-between text-gray-600">
          <span>Subtotale</span>
          <span>{formatCurrency(subtotal, currency)}</span>
        </div>

        {discount_total > 0 && (
          <div className="flex justify-between text-green-600">
            <span>Sconto {cart.discount_code && `(${cart.discount_code})`}</span>
            <span>-{formatCurrency(discount_total, currency)}</span>
          </div>
        )}

        <div className="flex justify-between text-gray-600">
          <span>Spedizione</span>
          <span>
            {shipping_total === 0 ? 'Gratuita' : formatCurrency(shipping_total, currency)}
          </span>
        </div>

        <div className="flex justify-between font-semibold text-gray-900 pt-2 border-t border-gray-200 text-base">
          <span>Totale</span>
          <span>{formatCurrency(total, currency)}</span>
        </div>
      </div>
    </div>
  )
}
