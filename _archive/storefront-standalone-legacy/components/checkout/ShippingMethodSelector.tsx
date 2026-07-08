'use client'

import { Loader2 } from 'lucide-react'
import type { ShippingMethod } from '@/types'

function formatCurrency(amount: number) {
  return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(amount)
}

interface Props {
  methods: ShippingMethod[]
  selected: number | null
  onChange: (id: number) => void
  onSubmit: () => Promise<void>
  loading?: boolean
}

export function ShippingMethodSelector({ methods, selected, onChange, onSubmit, loading }: Props) {
  if (methods.length === 0) {
    return (
      <p className="text-sm text-gray-500 py-4">
        Nessun metodo di spedizione disponibile per l'indirizzo selezionato.
      </p>
    )
  }

  return (
    <div className="space-y-3">
      {methods.map((method) => (
        <label
          key={method.id}
          className={`flex items-start gap-3 p-4 rounded-lg border-2 cursor-pointer transition-colors ${
            selected === method.id
              ? 'border-gray-900 bg-gray-50'
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          <input
            type="radio"
            name="shipping_method"
            value={method.id}
            checked={selected === method.id}
            onChange={() => onChange(method.id)}
            className="mt-0.5 accent-gray-900"
          />
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-900">{method.name}</span>
              <span className="text-sm font-semibold text-gray-900">
                {method.price === 0 ? 'Gratuita' : formatCurrency(method.price)}
              </span>
            </div>
            {method.description && (
              <p className="text-xs text-gray-500 mt-0.5">{method.description}</p>
            )}
            {method.estimated_days !== null && (
              <p className="text-xs text-gray-400 mt-0.5">
                Consegna stimata: {method.estimated_days}{' '}
                {method.estimated_days === 1 ? 'giorno' : 'giorni'}
              </p>
            )}
          </div>
        </label>
      ))}

      <button
        onClick={onSubmit}
        disabled={!selected || loading}
        className="w-full mt-4 flex items-center justify-center gap-2 rounded-lg bg-gray-900 text-white px-6 py-3 text-sm font-semibold hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading && <Loader2 className="w-4 h-4 animate-spin" />}
        Continua al pagamento
      </button>
    </div>
  )
}
