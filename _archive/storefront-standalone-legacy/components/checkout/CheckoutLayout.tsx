'use client'

import Link from 'next/link'
import { useBrandStore } from '@/stores/brandStore'
import { CheckoutProgress } from './CheckoutProgress'
import { CartSummary } from './CartSummary'
import type { CheckoutSession } from '@/types'

interface Props {
  checkout: CheckoutSession
  currentStep: 0 | 1 | 2
  children: React.ReactNode
  title: string
}

export function CheckoutLayout({ checkout, currentStep, children, title }: Props) {
  const brand = useBrandStore((s) => s.brand)

  return (
    <div className="min-h-screen bg-white">
      <header className="border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-lg font-bold text-gray-900">
            {brand?.name ?? 'Store'}
          </Link>
          <span className="text-xs text-gray-400 uppercase tracking-widest">Checkout sicuro</span>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        <CheckoutProgress currentStep={currentStep} />

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          <div className="lg:col-span-3">
            <h1 className="text-xl font-semibold text-gray-900 mb-6">{title}</h1>
            {children}
          </div>

          <aside className="lg:col-span-2">
            <CartSummary checkout={checkout} />
          </aside>
        </div>
      </main>
    </div>
  )
}
