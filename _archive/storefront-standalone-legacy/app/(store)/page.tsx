import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Home',
}

export default function StorefrontHomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4">
      <h1 className="text-3xl font-bold text-gray-900 mb-4">Benvenuto</h1>
      <p className="text-gray-600 mb-8">Il tuo negozio è pronto.</p>
      <div className="flex gap-4">
        <Link
          href="/checkout"
          className="px-5 py-2.5 rounded-lg bg-gray-900 text-white text-sm font-semibold hover:bg-gray-700 transition-colors"
        >
          Vai al checkout
        </Link>
        <Link
          href="/account/login"
          className="px-5 py-2.5 rounded-lg border border-gray-300 text-gray-700 text-sm font-semibold hover:bg-gray-50 transition-colors"
        >
          Il mio account
        </Link>
      </div>
    </main>
  )
}
