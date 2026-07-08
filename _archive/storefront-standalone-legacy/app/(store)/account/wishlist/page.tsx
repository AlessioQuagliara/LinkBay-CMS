'use client'

import { useEffect, useState } from 'react'
import { AccountLayout } from '@/components/account/AccountLayout'
import { WishlistItem } from '@/components/account/WishlistItem'
import { accountApi } from '@/lib/api/client'
import type { WishlistItem as WishlistItemType } from '@/types'
import { Loader2, Heart } from 'lucide-react'
import toast from 'react-hot-toast'

export default function WishlistPage() {
  const [items, setItems] = useState<WishlistItemType[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    accountApi.getWishlist()
      .then((res) => setItems(res.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handleRemove = async (productId: number) => {
    await accountApi.removeFromWishlist(productId)
    setItems((prev) => prev.filter((i) => i.product_id !== productId))
    toast.success('Rimosso dalla lista desideri')
  }

  return (
    <AccountLayout title="Lista desideri">
      {loading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
        </div>
      ) : items.length === 0 ? (
        <div className="text-center py-12">
          <Heart className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p className="text-sm font-medium text-gray-700">La lista desideri è vuota</p>
          <p className="text-xs text-gray-400 mt-1">
            Aggiungi prodotti alla lista desideri per trovarli qui.
          </p>
        </div>
      ) : (
        <div className="divide-y divide-gray-100">
          {items.map((item) => (
            <WishlistItem key={item.id} item={item} onRemove={handleRemove} />
          ))}
        </div>
      )}
    </AccountLayout>
  )
}
