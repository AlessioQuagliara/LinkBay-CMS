'use client'

import { useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { Trash2, ShoppingCart, Loader2 } from 'lucide-react'
import type { WishlistItem as WishlistItemType } from '@/types'
import { useCartStore } from '@/stores/cartStore'
import toast from 'react-hot-toast'

function formatCurrency(amount: number) {
  return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(amount)
}

interface Props {
  item: WishlistItemType
  onRemove: (productId: number) => Promise<void>
}

export function WishlistItem({ item, onRemove }: Props) {
  const [removing, setRemoving] = useState(false)
  const [addingToCart, setAddingToCart] = useState(false)
  const addItem = useCartStore((s) => s.addItem)

  const handleRemove = async () => {
    setRemoving(true)
    try {
      await onRemove(item.product_id)
    } finally {
      setRemoving(false)
    }
  }

  const handleAddToCart = async () => {
    setAddingToCart(true)
    try {
      await addItem(item.product_id)
      toast.success('Aggiunto al carrello')
    } catch {
      toast.error('Errore nell\'aggiunta al carrello')
    } finally {
      setAddingToCart(false)
    }
  }

  return (
    <div className="flex items-center gap-4 py-4">
      <Link href={`/products/${item.product_slug}`} className="flex-shrink-0">
        <div className="w-16 h-16 rounded-lg bg-gray-100 relative overflow-hidden">
          {item.image_url ? (
            <Image src={item.image_url} alt={item.product_name} fill className="object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-300 text-2xl">
              🛍
            </div>
          )}
        </div>
      </Link>

      <div className="flex-1 min-w-0">
        <Link
          href={`/products/${item.product_slug}`}
          className="text-sm font-medium text-gray-900 hover:underline truncate block"
        >
          {item.product_name}
        </Link>
        <p className="text-sm font-semibold text-gray-900 mt-0.5">
          {formatCurrency(item.price)}
        </p>
        <p className={`text-xs mt-0.5 ${item.in_stock ? 'text-green-600' : 'text-red-500'}`}>
          {item.in_stock ? 'Disponibile' : 'Esaurito'}
        </p>
      </div>

      <div className="flex items-center gap-2 flex-shrink-0">
        <button
          onClick={handleAddToCart}
          disabled={!item.in_stock || addingToCart}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-900 text-white text-xs font-medium hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {addingToCart
            ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
            : <ShoppingCart className="w-3.5 h-3.5" />
          }
          Aggiungi
        </button>

        <button
          onClick={handleRemove}
          disabled={removing}
          className="p-1.5 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 disabled:opacity-50 transition-colors"
          aria-label="Rimuovi dalla lista"
        >
          {removing
            ? <Loader2 className="w-4 h-4 animate-spin" />
            : <Trash2 className="w-4 h-4" />
          }
        </button>
      </div>
    </div>
  )
}
