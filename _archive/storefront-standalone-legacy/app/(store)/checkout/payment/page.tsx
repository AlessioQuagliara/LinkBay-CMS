'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { loadStripe } from '@stripe/stripe-js'
import { Elements } from '@stripe/react-stripe-js'
import { storeApi } from '@/lib/api/client'
import { useBrandStore } from '@/stores/brandStore'
import { useCartStore } from '@/stores/cartStore'
import { CheckoutLayout } from '@/components/checkout/CheckoutLayout'
import { StripePaymentForm } from '@/components/checkout/StripePaymentForm'
import type { CheckoutSession } from '@/types'
import { Loader2, Lock } from 'lucide-react'
import toast from 'react-hot-toast'

export default function CheckoutPaymentPage() {
  const router = useRouter()
  const brand = useBrandStore((s) => s.brand)
  const clearCart = useCartStore((s) => s.clearCart)

  const [checkout, setCheckout] = useState<CheckoutSession | null>(null)
  const [clientSecret, setClientSecret] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkoutId = sessionStorage.getItem('checkout_id')
    if (!checkoutId) {
      router.replace('/checkout')
      return
    }

    const load = async () => {
      try {
        const [checkoutRes, piRes] = await Promise.all([
          storeApi.getCheckout(checkoutId),
          storeApi.createPaymentIntent(checkoutId),
        ])
        setCheckout(checkoutRes.data)
        setClientSecret(piRes.data.client_secret)
      } catch {
        toast.error('Errore nel caricamento del pagamento')
        router.replace('/checkout/shipping')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [router])

  const handlePaymentSuccess = async (paymentIntentId: string) => {
    const checkoutId = sessionStorage.getItem('checkout_id')
    if (!checkoutId || !checkout) return

    try {
      const res = await storeApi.confirmCheckout(checkoutId, { payment_intent_id: paymentIntentId })
      clearCart()
      sessionStorage.removeItem('checkout_id')
      sessionStorage.removeItem('checkout_address')
      sessionStorage.removeItem('checkout_email')
      sessionStorage.removeItem('checkout_shipping_method')
      router.push(`/checkout/confirmation/${res.data.order_id}`)
    } catch {
      toast.error('Errore nella conferma dell\'ordine. Contatta il supporto.')
    }
  }

  const publishableKey = brand?.stripe_publishable_key
  const stripePromise = publishableKey ? loadStripe(publishableKey) : null

  if (loading || !checkout || !clientSecret) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    )
  }

  if (!stripePromise) {
    return (
      <CheckoutLayout checkout={checkout} currentStep={2} title="Pagamento">
        <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-4 text-sm text-yellow-800">
          Il pagamento online non è disponibile al momento. Contatta il negozio.
        </div>
      </CheckoutLayout>
    )
  }

  return (
    <CheckoutLayout checkout={checkout} currentStep={2} title="Pagamento">
      <div className="mb-4 flex items-center gap-1.5 text-xs text-gray-500">
        <Lock className="w-3.5 h-3.5" />
        <span>Pagamento sicuro e crittografato</span>
      </div>

      <Elements
        stripe={stripePromise}
        options={{
          clientSecret,
          appearance: {
            theme: 'stripe',
            variables: {
              colorPrimary: '#111827',
              borderRadius: '8px',
              fontFamily: 'system-ui, -apple-system, sans-serif',
            },
          },
        }}
      >
        <StripePaymentForm onSuccess={handlePaymentSuccess} />
      </Elements>
    </CheckoutLayout>
  )
}
