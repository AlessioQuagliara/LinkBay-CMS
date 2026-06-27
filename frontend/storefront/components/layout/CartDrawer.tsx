'use client'

import { useEffect, useRef } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { X, Trash2, ShoppingBag } from 'lucide-react'
import { useCartStore } from '@/storefront/lib/store/cartStore'
import { formatPrice } from '@/storefront/lib/utils/currency'
import { useBrandStore } from '@/storefront/lib/store/brandStore'

export default function CartDrawer() {
  const { isOpen, closeDrawer, items, meta, removeItem, updateItem, isLoading } =
    useCartStore()
  const brand = useBrandStore((s) => s.brand)
  const overlayRef = useRef<HTMLDivElement>(null)

  // Trap focus and handle Escape key
  useEffect(() => {
    if (!isOpen) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeDrawer()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [isOpen, closeDrawer])

  const currency = brand?.currency ?? 'EUR'

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          ref={overlayRef}
          className="fixed inset-0 z-50 bg-black/40"
          aria-hidden="true"
          onClick={closeDrawer}
        />
      )}

      {/* Drawer */}
      <aside
        role="dialog"
        aria-modal="true"
        aria-label="Carrello"
        className={`fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col bg-white shadow-2xl transition-transform duration-300 ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Il tuo carrello ({items.reduce((a, i) => a + i.quantity, 0)})
          </h2>
          <button
            onClick={closeDrawer}
            aria-label="Chiudi carrello"
            className="rounded-lg p-1.5 text-gray-500 hover:bg-gray-100"
          >
            <X size={20} />
          </button>
        </div>

        {/* Items */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <ShoppingBag size={48} className="mb-4 text-gray-300" />
              <p className="text-gray-500">Il tuo carrello è vuoto.</p>
              <button
                onClick={closeDrawer}
                className="mt-4 text-sm font-medium text-[var(--color-primary,#111)] underline"
              >
                Continua a fare acquisti
              </button>
            </div>
          ) : (
            <ul className="space-y-4" role="list" aria-label="Articoli nel carrello">
              {items.map((item) => {
                const img =
                  item.product?.productImages?.[0] ??
                  item.product?.images?.[0]

                return (
                  <li key={item.id} className="flex gap-4">
                    {/* Image */}
                    <div className="relative h-20 w-20 shrink-0 overflow-hidden rounded-lg bg-gray-100">
                      {img ? (
                        <Image
                          src={img.url}
                          alt={img.alt_text ?? item.product.name}
                          fill
                          className="object-cover"
                          sizes="80px"
                        />
                      ) : (
                        <ShoppingBag
                          size={24}
                          className="m-auto mt-6 text-gray-300"
                        />
                      )}
                    </div>

                    {/* Details */}
                    <div className="flex flex-1 flex-col justify-between">
                      <div className="flex justify-between gap-2">
                        <p className="text-sm font-medium text-gray-900 leading-tight">
                          {item.product.name}
                        </p>
                        <button
                          onClick={() => void removeItem(item.id)}
                          aria-label={`Rimuovi ${item.product.name}`}
                          className="text-gray-400 hover:text-red-500"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() =>
                              void updateItem(item.id, Math.max(1, item.quantity - 1))
                            }
                            aria-label="Diminuisci quantità"
                            className="flex h-6 w-6 items-center justify-center rounded border border-gray-300 text-sm hover:bg-gray-100"
                          >
                            −
                          </button>
                          <span className="w-6 text-center text-sm">{item.quantity}</span>
                          <button
                            onClick={() => void updateItem(item.id, item.quantity + 1)}
                            aria-label="Aumenta quantità"
                            className="flex h-6 w-6 items-center justify-center rounded border border-gray-300 text-sm hover:bg-gray-100"
                          >
                            +
                          </button>
                        </div>
                        <p className="text-sm font-semibold text-gray-900">
                          {formatPrice(item.line_total, currency)}
                        </p>
                      </div>
                    </div>
                  </li>
                )
              })}
            </ul>
          )}
        </div>

        {/* Footer */}
        {items.length > 0 && (
          <div className="border-t border-gray-200 px-6 py-4">
            <div className="mb-3 flex justify-between text-sm text-gray-600">
              <span>Subtotale</span>
              <span className="font-medium text-gray-900">
                {formatPrice(meta.subtotal, currency)}
              </span>
            </div>
            <p className="mb-4 text-xs text-gray-400">
              Spese di spedizione e sconti calcolati al checkout.
            </p>
            <Link
              href="/checkout"
              onClick={closeDrawer}
              className="block w-full rounded-xl bg-[var(--color-primary,#111)] py-3.5 text-center text-sm font-semibold text-white transition-opacity hover:opacity-90"
            >
              Vai al checkout
            </Link>
            <button
              onClick={closeDrawer}
              className="mt-2 w-full text-center text-sm text-gray-500 hover:text-gray-700"
            >
              Continua a fare acquisti
            </button>
          </div>
        )}

        {/* Loading overlay */}
        {isLoading && (
          <div
            role="status"
            aria-label="Aggiornamento carrello in corso"
            className="absolute inset-0 flex items-center justify-center bg-white/60"
          >
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-[var(--color-primary,#111)]" />
          </div>
        )}
      </aside>
    </>
  )
}
