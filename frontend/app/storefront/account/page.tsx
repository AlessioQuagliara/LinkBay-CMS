'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/storefront/lib/store/authStore'
import { Package, User, LogOut, ChevronRight } from 'lucide-react'

const NAV = [
  { href: '/account/orders', icon: Package, label: 'I miei ordini', sub: 'Storico acquisti e tracking' },
  { href: '/account/profile', icon: User, label: 'Profilo', sub: 'Dati personali e indirizzi' },
]

export default function AccountPage() {
  const router = useRouter()
  const { token, customer, logout, hasHydrated } = useAuthStore()

  useEffect(() => {
    if (hasHydrated && !token) {
      router.replace('/account/login')
    }
  }, [hasHydrated, token, router])

  if (!hasHydrated || !token) return null

  async function handleLogout() {
    await logout()
    router.replace('/account/login')
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-12 sm:px-6">
      {/* Greeting */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Ciao{customer?.name ? `, ${customer.name.split(' ')[0]}` : ''}!
        </h1>
        {customer?.email && (
          <p className="mt-1 text-sm text-gray-500">{customer.email}</p>
        )}
      </div>

      {/* Navigation tiles */}
      <nav className="space-y-3">
        {NAV.map(({ href, icon: Icon, label, sub }) => (
          <Link
            key={href}
            href={href}
            className="flex items-center gap-4 rounded-2xl border border-gray-200 bg-white p-4 transition hover:border-gray-400 hover:shadow-sm"
          >
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gray-100 text-gray-600">
              <Icon className="h-5 w-5" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold text-gray-900">{label}</p>
              <p className="text-xs text-gray-400">{sub}</p>
            </div>
            <ChevronRight className="h-4 w-4 text-gray-300" />
          </Link>
        ))}
      </nav>

      {/* Logout */}
      <button
        type="button"
        onClick={handleLogout}
        className="mt-8 flex w-full items-center justify-center gap-2 rounded-xl border border-red-100 py-3 text-sm font-medium text-red-500 transition hover:bg-red-50"
      >
        <LogOut className="h-4 w-4" />
        Esci dall&rsquo;account
      </button>
    </div>
  )
}
