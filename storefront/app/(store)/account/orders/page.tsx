'use client'

import { useEffect, useState } from 'react'
import { AccountLayout } from '@/components/account/AccountLayout'
import { OrderCard } from '@/components/account/OrderCard'
import { accountApi } from '@/lib/api/client'
import type { Order } from '@/types'
import { Loader2, ShoppingBag } from 'lucide-react'

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    accountApi.getOrders()
      .then((res) => setOrders(res.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <AccountLayout title="I miei ordini">
      {loading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
        </div>
      ) : orders.length === 0 ? (
        <div className="text-center py-12">
          <ShoppingBag className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p className="text-sm font-medium text-gray-700">Nessun ordine ancora</p>
          <p className="text-xs text-gray-400 mt-1">
            I tuoi acquisti appariranno qui non appena effettui un ordine.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {orders.map((order) => (
            <OrderCard key={order.id} order={order} />
          ))}
        </div>
      )}
    </AccountLayout>
  )
}
