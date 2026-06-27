'use client'

import Link from 'next/link'
import { Instagram, Facebook, Twitter, Youtube } from 'lucide-react'
import { useBrandStore } from '@/storefront/lib/store/brandStore'

const SOCIAL_ICONS: Record<string, React.ElementType> = {
  instagram: Instagram,
  facebook: Facebook,
  twitter: Twitter,
  youtube: Youtube,
}

export default function StoreFooter() {
  const brand = useBrandStore((s) => s.brand)

  return (
    <footer className="mt-16 border-t border-gray-200 bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {/* Brand info */}
          <div>
            <p className="text-lg font-bold text-gray-900">
              {brand?.store_name ?? 'Store'}
            </p>
            {brand?.tagline && (
              <p className="mt-1 text-sm text-gray-500">{brand.tagline}</p>
            )}
            {brand?.contact_email && (
              <a
                href={`mailto:${brand.contact_email}`}
                className="mt-3 block text-sm text-gray-600 hover:text-gray-900"
              >
                {brand.contact_email}
              </a>
            )}
            {brand?.phone && (
              <a
                href={`tel:${brand.phone}`}
                className="mt-1 block text-sm text-gray-600 hover:text-gray-900"
              >
                {brand.phone}
              </a>
            )}
          </div>

          {/* Navigation */}
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
              Informazioni
            </h3>
            <ul className="mt-4 space-y-2">
              {['chi-siamo', 'contatti', 'privacy', 'termini'].map((slug) => (
                <li key={slug}>
                  <Link
                    href={`/${slug}`}
                    className="text-sm text-gray-600 transition-colors hover:text-gray-900"
                  >
                    {slug.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Social */}
          {brand?.social_links && Object.keys(brand.social_links).length > 0 && (
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
                Seguici
              </h3>
              <div className="mt-4 flex gap-3">
                {Object.entries(brand.social_links).map(([platform, url]) => {
                  if (!url) return null
                  const Icon = SOCIAL_ICONS[platform]
                  return (
                    <a
                      key={platform}
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label={platform}
                      className="rounded-lg p-2 text-gray-500 transition-colors hover:bg-gray-200 hover:text-gray-900"
                    >
                      {Icon ? <Icon size={18} /> : platform}
                    </a>
                  )
                })}
              </div>
            </div>
          )}
        </div>

        <div className="mt-8 border-t border-gray-200 pt-6 text-center text-xs text-gray-400">
          © {new Date().getFullYear()} {brand?.store_name}. Tutti i diritti riservati.
        </div>
      </div>
    </footer>
  )
}
