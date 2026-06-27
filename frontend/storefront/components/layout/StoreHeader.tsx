'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { ShoppingBag, User, Menu, X } from 'lucide-react'
import { useBrandStore } from '@/storefront/lib/store/brandStore'
import { useCartStore } from '@/storefront/lib/store/cartStore'
import { useCategories } from '@/storefront/lib/hooks/useCategories'
import SearchBar from '../filters/SearchBar'

export default function StoreHeader() {
  const [menuOpen, setMenuOpen] = useState(false)
  const brand = useBrandStore((s) => s.brand)
  const { items, openDrawer } = useCartStore()
  const { data: categories = [] } = useCategories()

  const itemCount = items.reduce((acc, i) => acc + i.quantity, 0)

  return (
    <header className="sticky top-0 z-40 w-full border-b border-gray-200 bg-white/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link href="/" className="flex shrink-0 items-center gap-2">
          {brand?.logo_url ? (
            <Image
              src={brand.logo_url}
              alt={brand.store_name}
              width={120}
              height={40}
              className="h-8 w-auto object-contain"
            />
          ) : (
            <span className="text-lg font-bold text-gray-900">
              {brand?.store_name ?? 'Store'}
            </span>
          )}
        </Link>

        {/* Desktop nav */}
        <nav className="hidden gap-6 md:flex" aria-label="Categorie principali">
          {categories.slice(0, 6).map((cat) => (
            <Link
              key={cat.id}
              href={`/shop/${cat.slug}`}
              className="text-sm font-medium text-gray-600 transition-colors hover:text-gray-900"
            >
              {cat.name}
            </Link>
          ))}
        </nav>

        {/* Search + icons */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:block">
            <SearchBar />
          </div>

          <Link
            href="/account"
            aria-label="Il mio account"
            className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
          >
            <User size={20} />
          </Link>

          <button
            onClick={openDrawer}
            aria-label={`Carrello — ${itemCount} ${itemCount === 1 ? 'articolo' : 'articoli'}`}
            className="relative rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
          >
            <ShoppingBag size={20} />
            {itemCount > 0 && (
              <span
                aria-hidden="true"
                className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-[var(--color-primary,#111)] text-[10px] font-bold text-white"
              >
                {itemCount > 9 ? '9+' : itemCount}
              </span>
            )}
          </button>

          {/* Mobile hamburger */}
          <button
            className="rounded-lg p-2 text-gray-600 md:hidden"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label={menuOpen ? 'Chiudi menu' : 'Apri menu'}
            aria-expanded={menuOpen}
          >
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile search */}
      <div className="border-t border-gray-100 px-4 py-2 sm:hidden">
        <SearchBar />
      </div>

      {/* Mobile nav */}
      {menuOpen && (
        <nav
          className="border-t border-gray-100 px-4 py-3 md:hidden"
          aria-label="Menu mobile"
        >
          <ul className="space-y-2">
            <li>
              <Link
                href="/shop"
                className="block py-2 text-sm font-medium text-gray-700"
                onClick={() => setMenuOpen(false)}
              >
                Tutti i prodotti
              </Link>
            </li>
            {categories.map((cat) => (
              <li key={cat.id}>
                <Link
                  href={`/shop/${cat.slug}`}
                  className="block py-2 text-sm text-gray-600"
                  onClick={() => setMenuOpen(false)}
                >
                  {cat.name}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </header>
  )
}
