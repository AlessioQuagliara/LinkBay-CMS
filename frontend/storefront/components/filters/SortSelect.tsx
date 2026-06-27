'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'

const SORT_OPTIONS = [
  { label: 'Più recenti', value: 'created_at:desc' },
  { label: 'Meno recenti', value: 'created_at:asc' },
  { label: 'Prezzo crescente', value: 'price:asc' },
  { label: 'Prezzo decrescente', value: 'price:desc' },
  { label: 'Nome A–Z', value: 'name:asc' },
  { label: 'Nome Z–A', value: 'name:desc' },
] as const

export default function SortSelect() {
  const router = useRouter()
  const pathname = usePathname()
  const params = useSearchParams()

  const current = `${params.get('sort_by') ?? 'created_at'}:${params.get('sort_dir') ?? 'desc'}`

  function handleChange(value: string) {
    const [sort_by, sort_dir] = value.split(':')
    const next = new URLSearchParams(params.toString())
    next.set('sort_by', sort_by)
    next.set('sort_dir', sort_dir)
    next.delete('page')
    router.push(`${pathname}?${next.toString()}`)
  }

  return (
    <label className="flex items-center gap-2 text-sm text-gray-700">
      <span className="text-gray-500">Ordina per</span>
      <select
        value={current}
        onChange={(e) => handleChange(e.target.value)}
        aria-label="Ordina prodotti"
        className="rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary,#111)]"
      >
        {SORT_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </label>
  )
}
