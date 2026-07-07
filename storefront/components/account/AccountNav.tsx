'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'
import {
  LayoutDashboard,
  User,
  MapPin,
  ShoppingBag,
  Heart,
  LogOut,
} from 'lucide-react'

const LINKS = [
  { href: '/account', label: 'Dashboard', icon: LayoutDashboard, exact: true },
  { href: '/account/profile', label: 'Profilo', icon: User },
  { href: '/account/addresses', label: 'Indirizzi', icon: MapPin },
  { href: '/account/orders', label: 'Ordini', icon: ShoppingBag },
  { href: '/account/wishlist', label: 'Lista desideri', icon: Heart },
]

export function AccountNav() {
  const pathname = usePathname()
  const router = useRouter()
  const logout = useAuthStore((s) => s.logout)

  const handleLogout = async () => {
    await logout()
    router.push('/account/login')
  }

  return (
    <nav className="space-y-0.5">
      {LINKS.map(({ href, label, icon: Icon, exact }) => {
        const active = exact ? pathname === href : pathname.startsWith(href)
        return (
          <Link
            key={href}
            href={href}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              active
                ? 'bg-gray-100 text-gray-900'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </Link>
        )
      })}

      <button
        onClick={handleLogout}
        className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors mt-2"
      >
        <LogOut className="w-4 h-4 flex-shrink-0" />
        Esci
      </button>
    </nav>
  )
}
