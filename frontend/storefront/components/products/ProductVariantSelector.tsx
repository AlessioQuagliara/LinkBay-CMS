'use client'

import type { ProductVariant } from '@/storefront/lib/types/product'

interface ProductVariantSelectorProps {
  variants: ProductVariant[]
  selectedId: number | null
  onChange: (variantId: number) => void
}

export default function ProductVariantSelector({
  variants,
  selectedId,
  onChange,
}: ProductVariantSelectorProps) {
  if (variants.length === 0) return null

  // Group variants by option key (e.g. "Taglia", "Colore")
  const optionKeys = [...new Set(variants.flatMap((v) => Object.keys(v.options)))]

  return (
    <div className="space-y-4">
      {optionKeys.map((key) => {
        const values = [...new Set(variants.map((v) => v.options[key]))]
        return (
          <div key={key}>
            <p className="mb-2 text-sm font-medium text-gray-700 capitalize">{key}</p>
            <div className="flex flex-wrap gap-2" role="group" aria-label={key}>
              {values.map((val) => {
                const matchingVariant = variants.find(
                  (v) => v.options[key] === val,
                )
                if (!matchingVariant) return null
                const isSelected = selectedId === matchingVariant.id
                const isUnavailable = matchingVariant.quantity <= 0

                return (
                  <button
                    key={val}
                    onClick={() => onChange(matchingVariant.id)}
                    disabled={isUnavailable}
                    aria-pressed={isSelected}
                    aria-label={`${key}: ${val}${isUnavailable ? ' — esaurito' : ''}`}
                    className={`rounded-lg border px-4 py-2 text-sm font-medium transition-colors ${
                      isSelected
                        ? 'border-[var(--color-primary,#111)] bg-[var(--color-primary,#111)] text-white'
                        : isUnavailable
                          ? 'border-gray-200 bg-gray-50 text-gray-300 line-through cursor-not-allowed'
                          : 'border-gray-300 text-gray-700 hover:border-gray-900'
                    }`}
                  >
                    {val}
                  </button>
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}
