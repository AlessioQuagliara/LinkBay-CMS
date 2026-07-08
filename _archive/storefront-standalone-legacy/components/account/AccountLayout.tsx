'use client'

import Link from 'next/link'
import { useBrandStore } from '@/stores/brandStore'
import { AccountNav } from './AccountNav'

interface Props {
  children: React.ReactNode
  title: string
}

export function AccountLayout({ children, title }: Props) {
  const brand = useBrandStore((s) => s.brand)

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <Link href="/" className="text-lg font-bold text-gray-900">
            {brand?.name ?? 'Store'}
          </Link>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <aside className="md:col-span-1">
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <AccountNav />
            </div>
          </aside>

          <main className="md:col-span-3">
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h1 className="text-lg font-semibold text-gray-900 mb-6">{title}</h1>
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
