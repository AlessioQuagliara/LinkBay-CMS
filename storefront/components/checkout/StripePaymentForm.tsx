'use client'

import { useState } from 'react'
import {
  PaymentElement,
  useStripe,
  useElements,
} from '@stripe/react-stripe-js'
import { Loader2, AlertCircle } from 'lucide-react'

interface Props {
  onSuccess: (paymentIntentId: string) => Promise<void>
}

export function StripePaymentForm({ onSuccess }: Props) {
  const stripe = useStripe()
  const elements = useElements()
  const [error, setError] = useState<string | null>(null)
  const [processing, setProcessing] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!stripe || !elements) return

    setError(null)
    setProcessing(true)

    try {
      const { error: submitError } = await elements.submit()
      if (submitError) {
        setError(submitError.message ?? 'Errore nella validazione del form')
        return
      }

      const { error: confirmError, paymentIntent } = await stripe.confirmPayment({
        elements,
        redirect: 'if_required',
      })

      if (confirmError) {
        setError(confirmError.message ?? 'Pagamento non riuscito')
        return
      }

      if (paymentIntent?.status === 'succeeded' || paymentIntent?.status === 'requires_capture') {
        await onSuccess(paymentIntent.id)
      } else {
        setError('Stato pagamento inatteso: ' + paymentIntent?.status)
      }
    } finally {
      setProcessing(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <PaymentElement
        options={{
          layout: 'tabs',
          fields: {
            billingDetails: {
              address: 'auto',
            },
          },
        }}
      />

      {error && (
        <div className="flex items-start gap-2 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <button
        type="submit"
        disabled={!stripe || !elements || processing}
        className="w-full flex items-center justify-center gap-2 rounded-lg bg-gray-900 text-white px-6 py-3 text-sm font-semibold hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {processing && <Loader2 className="w-4 h-4 animate-spin" />}
        {processing ? 'Elaborazione...' : 'Conferma pagamento'}
      </button>
    </form>
  )
}
