'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ChevronDown, ChevronRight } from 'lucide-react'
import type { Category } from '@/storefront/lib/types/product'

interface CategoryNavProps {
  categories: Category[]
  activeSlug?: string
}

function CategoryItem({
  category,
  activeSlug,
  depth = 0,
}: {
  category: Category
  activeSlug?: string
  depth?: number
}) {
  const [open, setOpen] = useState(false)
  const hasChildren = category.children.length > 0
  const isActive = activeSlug === category.slug

  return (
    <li>
      <div className="flex items-center justify-between">
        <Link
          href={`/shop/${category.slug}`}
          className={`flex-1 rounded-lg px-3 py-2 text-sm transition-colors ${
            isActive
              ? 'bg-[var(--color-primary,#111)] font-medium text-white'
              : 'text-gray-700 hover:bg-gray-100'
          }`}
          style={{ paddingLeft: `${0.75 + depth * 0.75}rem` }}
          aria-current={isActive ? 'page' : undefined}
        >
          {category.name}
        </Link>
        {hasChildren && (
          <button
            onClick={() => setOpen(!open)}
            aria-expanded={open}
            aria-label={`${open ? 'Comprimi' : 'Espandi'} ${category.name}`}
            className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100"
          >
            {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </button>
        )}
      </div>
      {hasChildren && open && (
        <ul className="mt-1 space-y-1">
          {category.children.map((child) => (
            <CategoryItem
              key={child.id}
              category={child}
              activeSlug={activeSlug}
              depth={depth + 1}
            />
          ))}
        </ul>
      )}
    </li>
  )
}

export default function CategoryNav({ categories, activeSlug }: CategoryNavProps) {
  return (
    <nav aria-label="Categorie">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-500">
        Categorie
      </h2>
      <ul className="space-y-1">
        <li>
          <Link
            href="/shop"
            className={`block rounded-lg px-3 py-2 text-sm transition-colors ${
              !activeSlug
                ? 'bg-[var(--color-primary,#111)] font-medium text-white'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
            aria-current={!activeSlug ? 'page' : undefined}
          >
            Tutti i prodotti
          </Link>
        </li>
        {categories.map((cat) => (
          <CategoryItem key={cat.id} category={cat} activeSlug={activeSlug} />
        ))}
      </ul>
    </nav>
  )
}
