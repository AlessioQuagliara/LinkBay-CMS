'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface PaginationProps {
  currentPage: number
  lastPage: number
  total: number
}

export default function Pagination({ currentPage, lastPage, total }: PaginationProps) {
  const router = useRouter()
  const pathname = usePathname()
  const params = useSearchParams()

  if (lastPage <= 1) return null

  function goTo(page: number) {
    const next = new URLSearchParams(params.toString())
    next.set('page', String(page))
    router.push(`${pathname}?${next.toString()}`)
  }

  const pages = Array.from({ length: lastPage }, (_, i) => i + 1).filter(
    (p) => p === 1 || p === lastPage || Math.abs(p - currentPage) <= 2,
  )

  return (
    <nav
      aria-label="Paginazione"
      className="flex items-center justify-center gap-1"
    >
      <button
        onClick={() => goTo(currentPage - 1)}
        disabled={currentPage === 1}
        aria-label="Pagina precedente"
        className="rounded-lg border border-gray-200 p-2 text-gray-600 hover:bg-gray-100 disabled:opacity-40"
      >
        <ChevronLeft size={16} />
      </button>

      {pages.map((page, idx) => {
        const prev = pages[idx - 1]
        const showEllipsis = prev != null && page - prev > 1
        return (
          <span key={page} className="flex items-center gap-1">
            {showEllipsis && <span className="px-1 text-gray-400">…</span>}
            <button
              onClick={() => goTo(page)}
              aria-label={`Pagina ${page}`}
              aria-current={page === currentPage ? 'page' : undefined}
              className={`h-9 w-9 rounded-lg text-sm font-medium transition-colors ${
                page === currentPage
                  ? 'bg-[var(--color-primary,#111)] text-white'
                  : 'border border-gray-200 text-gray-700 hover:bg-gray-100'
              }`}
            >
              {page}
            </button>
          </span>
        )
      })}

      <button
        onClick={() => goTo(currentPage + 1)}
        disabled={currentPage === lastPage}
        aria-label="Pagina successiva"
        className="rounded-lg border border-gray-200 p-2 text-gray-600 hover:bg-gray-100 disabled:opacity-40"
      >
        <ChevronRight size={16} />
      </button>
    </nav>
  )
}
