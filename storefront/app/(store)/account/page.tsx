'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useAuthStore } from '@/stores/authStore'
import { AccountLayout } from '@/components/account/AccountLayout'
import { accountApi } from '@/lib/api/client'
import type { Order } from '@/types'
import { ShoppingBag, MapPin, Heart, ChevronRight } from 'lucide-react'
import { OrderCard } from '@/components/account/OrderCard'

function formatCurrency(amount: number, currency: string) {
  return new Intl.NumberFormat('it-IT', {
    style: 'currency',
    currency: currency.toUpperCase(),
  }).format(amount)
}

export default function AccountDashboardPage() {
  const customer = useAuthStore((s) => s.customer)
  const [recentOrders, setRecentOrders] = useState<Order[]>([])

  useEffect(() => {
    accountApi.getOrders()
      .then((res) => setRecentOrders(res.data.slice(0, 3)))
      .catch(() => {})
  }, [])

  return (
    <AccountLayout title={`Ciao, ${customer?.name?.split(' ')[0] ?? 'utente'} 👋`}>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <Link
          href="/account/orders"
          className="flex items-center gap-3 p-4 rounded-xl border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all"
        >
          <div className="p-2 bg-blue-50 rounded-lg">
            <ShoppingBag className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">I miei ordini</p>
            <p className="text-sm font-semibold text-gray-900">Visualizza</p>
          </div>
          <ChevronRight className="w-4 h-4 text-gray-400 ml-auto" />
        </Link>

        <Link
          href="/account/addresses"
          className="flex items-center gap-3 p-4 rounded-xl border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all"
        >
          <div className="p-2 bg-green-50 rounded-lg">
            <MapPin className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">Indirizzi</p>
            <p className="text-sm font-semibold text-gray-900">Gestisci</p>
          </div>
          <ChevronRight className="w-4 h-4 text-gray-400 ml-auto" />
        </Link>

        <Link
          href="/account/wishlist"
          className="flex items-center gap-3 p-4 rounded-xl border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all"
        >
          <div className="p-2 bg-red-50 rounded-lg">
            <Heart className="w-5 h-5 text-red-500" />
          </div>
          <div>
            <p className="text-xs text-gray-500">Lista desideri</p>
            <p className="text-sm font-semibold text-gray-900">Visualizza</p>
          </div>
          <ChevronRight className="w-4 h-4 text-gray-400 ml-auto" />
        </Link>
      </div>

      {recentOrders.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-gray-900">Ultimi ordini</h2>
            <Link href="/account/orders" className="text-xs text-gray-500 hover:text-gray-900">
              Vedi tutti →
            </Link>
          </div>
          <div className="space-y-3">
            {recentOrders.map((order) => (
              <OrderCard key={order.id} order={order} />
            ))}
          </div>
        </div>
      )}
    </AccountLayout>
  )
}
