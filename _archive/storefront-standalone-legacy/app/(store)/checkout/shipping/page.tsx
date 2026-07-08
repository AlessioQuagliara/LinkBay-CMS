'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { storeApi } from '@/lib/api/client'
import { CheckoutLayout } from '@/components/checkout/CheckoutLayout'
import { ShippingMethodSelector } from '@/components/checkout/ShippingMethodSelector'
import type { CheckoutSession, ShippingMethod } from '@/types'
import { Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'

// Fallback shipping methods until the backend exposes a shipping-methods endpoint
const FALLBACK_METHODS: ShippingMethod[] = [
  { id: 1, name: 'Spedizione Standard', description: 'Corriere standard', price: 5.9, estimated_days: 5 },
  { id: 2, name: 'Spedizione Express', description: 'Corriere espresso', price: 12.9, estimated_days: 2 },
  { id: 3, name: 'Spedizione Gratuita', description: 'Disponibile per ordini superiori a €50', price: 0, estimated_days: 7 },
]

export default function CheckoutShippingPage() {
  const router = useRouter()
  const [checkout, setCheckout] = useState<CheckoutSession | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [selectedMethod, setSelectedMethod] = useState<number | null>(null)

  useEffect(() => {
    const checkoutId = sessionStorage.getItem('checkout_id')
    if (!checkoutId) {
      router.replace('/checkout')
      return
    }
    storeApi.getCheckout(checkoutId)
      .then((res) => {
        setCheckout(res.data)
        if (res.data.shipping_method) {
          setSelectedMethod(res.data.shipping_method.id)
        } else {
          setSelectedMethod(FALLBACK_METHODS[0].id)
        }
      })
      .catch(() => { router.replace('/checkout') })
      .finally(() => setLoading(false))
  }, [router])

  const handleSubmit = async () => {
    if (!selectedMethod) return
    setSubmitting(true)
    try {
      const method = FALLBACK_METHODS.find((m) => m.id === selectedMethod)
      sessionStorage.setItem('checkout_shipping_method', JSON.stringify(method))
      router.push('/checkout/payment')
    } catch {
      toast.error('Errore nella selezione del metodo di spedizione')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading || !checkout) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    )
  }

  return (
    <CheckoutLayout checkout={checkout} currentStep={1} title="Metodo di spedizione">
      <ShippingMethodSelector
        methods={FALLBACK_METHODS}
        selected={selectedMethod}
        onChange={setSelectedMethod}
        onSubmit={handleSubmit}
        loading={submitting}
      />
    </CheckoutLayout>
  )
}
