'use client'

import { useState } from 'react'
import { ShoppingBag, Check } from 'lucide-react'
import toast from 'react-hot-toast'
import { useCartStore } from '@/storefront/lib/store/cartStore'

interface AddToCartButtonProps {
  productId: number
  variantId?: number | null
  quantity?: number
  disabled?: boolean
  outOfStock?: boolean
}

export default function AddToCartButton({
  productId,
  variantId,
  quantity = 1,
  disabled,
  outOfStock,
}: AddToCartButtonProps) {
  const { addItem, isLoading } = useCartStore()
  const [added, setAdded] = useState(false)

  async function handleAdd() {
    if (disabled || outOfStock) return
    try {
      await addItem(productId, quantity, variantId ?? undefined)
      setAdded(true)
      toast.success('Aggiunto al carrello!')
      setTimeout(() => setAdded(false), 2000)
    } catch {
      toast.error('Impossibile aggiungere al carrello.')
    }
  }

  if (outOfStock) {
    return (
      <button
        disabled
        aria-label="Prodotto esaurito"
        className="w-full cursor-not-allowed rounded-xl bg-gray-100 py-4 text-sm font-semibold text-gray-400"
      >
        Esaurito
      </button>
    )
  }

  return (
    <button
      onClick={() => void handleAdd()}
      disabled={disabled || isLoading || added}
      aria-label={added ? 'Aggiunto al carrello' : 'Aggiungi al carrello'}
      className="flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--color-primary,#111)] py-4 text-sm font-semibold text-white transition-all hover:opacity-90 disabled:opacity-60"
    >
      {isLoading ? (
        <>
          <span
            role="status"
            aria-label="Aggiunta in corso"
            className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white"
          />
          Aggiunta in corso…
        </>
      ) : added ? (
        <>
          <Check size={16} />
          Aggiunto!
        </>
      ) : (
        <>
          <ShoppingBag size={16} />
          Aggiungi al carrello
        </>
      )}
    </button>
  )
}
