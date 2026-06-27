'use client'

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Search } from 'lucide-react'

export default function SearchBar() {
  const [query, setQuery] = useState('')
  const router = useRouter()

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault()
      const q = query.trim()
      if (q) router.push(`/search?q=${encodeURIComponent(q)}`)
    },
    [query, router],
  )

  return (
    <form
      onSubmit={handleSubmit}
      role="search"
      aria-label="Cerca prodotti"
      className="relative"
    >
      <Search
        size={16}
        className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
        aria-hidden="true"
      />
      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Cerca prodotti…"
        aria-label="Cerca prodotti"
        className="h-9 w-full rounded-lg border border-gray-200 bg-gray-50 pl-9 pr-4 text-sm placeholder-gray-400 focus:border-gray-400 focus:bg-white focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary,#111)] focus-visible:ring-offset-1 sm:w-56"
      />
    </form>
  )
}
